#!/usr/bin/env python3
####################################################################################################################################################################################################################################################################
#                                                                                                                                                                                                                                                                  #
#                                                                                                                                                                                                                                                                  #
#        Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)                                                                                                                                                                                                   #
#                                                                                                                                                                                                                                                                  #
#        This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.    #
#        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.           #
#        You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.                                                                                                            #
#                                                                                                                                                                                                                                                                  #
####################################################################################################################################################################################################################################################################
#
from	__future__ import annotations
import	logging, argparse, errno
import	sys, os, signal, time, re
import	subprocess
import	requests, warnings
from	collections import defaultdict
from	dataclasses import dataclass, field
from	datetime import datetime
from	email.message import EmailMessage
from	email.utils import parseaddr
from	typing import Any, Final, Optional
from	typing import ClassVar, DefaultDict, Dict, List, NamedTuple, Pattern, Tuple
from	typing import cast
from	agn3.db import DB, Row
from	agn3.definitions import base, licence, fqdn, syscfg
from	agn3.email import EMail, ParseEMail
from	agn3.emm.bounce import Bounce
from	agn3.emm.datasource import Datasource
from	agn3.emm.types import UserStatus
from	agn3.exceptions import error
from	agn3.ignore import Ignore
from	agn3.io import which
from	agn3.log import log_limit, log
from	agn3.parser import ParseTimestamp, Unit, Line, Field, Lineparser, Tokenparser
from	agn3.runtime import Runtime
from	agn3.spool import Mailspool
from	agn3.stream import Stream
from	agn3.tools import atoi, listsplit, unescape
from	agn3.uid import UID, UIDHandler
#
logger = logging.getLogger (__name__)
#
def invoke (url: str, retries: int = 3, **kws: Any) -> Tuple[bool, requests.Response]:
	with log ('invoke'), warnings.catch_warnings ():
		warnings.simplefilter ("ignore")
		parameter: Dict[str, Any] = {
			'url': url,
			'verify': False,
			'timeout': (30, 180)
		}
		parameter.update (kws)
		for round in range (retries):
			if round > 0:
				time.sleep (round)
			try:
				response = requests.get (**parameter)
				if response.status_code // 100 == 2:
					logger.debug (f'{url} invoked successfully: {response}: "{response.text}"')
					return (True, response)
				logger.warning (f'{url} invocation failed: {response}: "{response.text}"')
				if response.status_code // 100 == 5 or round + 1 == retries:
					return (False, response)
			except Exception as e:
				logger.error (f'{url} invocation failed: {e}')
				raise
		raise error (f'{url} invocation failed after {retries} retries')

class Autoresponder:
	__slots__ = ['aid', 'sender']
	name_autoresponder: Final[str] = 'autoresponder'
	name_whitelist: Final[str] = 'whitelist'
	name_limit: Final[str] = 'limit'
	bounce_autoresponder_lastsent_table: Final[str] = 'bounce_ar_lastsent_tbl'
	unit = Unit ()
	def __init__ (self, aid: str, sender: str) -> None:
		self.aid = aid
		self.sender = sender.lower ()
	
	def is_in_whitelist (self, bounce: Bounce, parameter: Line) -> bool:
		whitelist: Optional[str] = bounce.get_config (
			company_id = parameter.company_id,
			rid = parameter.rid,
			name = self.name_autoresponder
		).get (self.name_whitelist)
		if whitelist is not None and self.sender in listsplit (whitelist.lower ()):
			return True
		return False
	
	def may_receive (self, db: DB, bounce: Bounce, parameter: Line, cinfo: ParseEMail.Origin, dryrun: bool) -> bool:
		may_receive = True
		limit: int = self.unit.parse (bounce.get_config (
			company_id = parameter.company_id,
			rid = parameter.rid,
			name = self.name_autoresponder
		).get (self.name_limit, '1d'))
		now = datetime.now ()
		rq = db.querys (
			'SELECT lastsent '
			f'FROM {self.bounce_autoresponder_lastsent_table} '
			'WHERE rid = :rid AND customer_id = :customer_id',
			{
				'rid': parameter.rid,
				'customer_id': cinfo.customer_id
			}
		)
		if rq is None:
			logger.debug (f'Never sent mail to {self.sender} from this autoresponder {self.aid}')
		elif rq.lastsent is None:
			logger.debug (f'Last sent mail to {self.sender} from this autoresponder {self.aid} is unspecified')
		else:
			if int (rq.lastsent.timestamp ()) + limit < int (now.timestamp ()):
				logger.debug (f'Last sent mail to {self.sender} had exceeded limit, last sent {rq.lastsent}')
			else:
				logger.info (f'Last sent mail to {self.sender} had not exceeded limit, last sent was {rq.lastsent}, no further mail is sent')
				may_receive = False
		if may_receive and not dryrun:
			with db.request () as cursor:
				data = {
					'rid': parameter.rid,
					'customer_id': cinfo.customer_id,
					'lastsent': now
				}
				if rq is None:
					cursor.update (
						f'INSERT INTO {self.bounce_autoresponder_lastsent_table} '
						'        (rid, customer_id, lastsent) '
						'VALUES '
						'        (:rid, :customer_id, :lastsent)',
						data
					)
				else:
					cursor.update (
						f'UPDATE {self.bounce_autoresponder_lastsent_table} '
						'SET lastsent = :lastsent '
						'WHERE rid = :rid AND customer_id = :customer_id',
						data
					)
				cursor.sync ()
		return may_receive
	
	def allow (self, db: DB, bounce: Bounce, parameter: Line, cinfo: ParseEMail.Origin, dryrun: bool) -> bool:
		if self.is_in_whitelist (bounce, parameter):
			return True
		if not self.may_receive (db, bounce, parameter, cinfo, dryrun):
			return False
		return True

	def trigger_message (self,
		db: DB,
		bounce: Bounce,
		cinfo: Optional[ParseEMail.Origin],
		parameter: Line,
		dryrun: bool
	) -> None:
		try:
			if not parameter.autoresponder_mailing_id:
				raise error ('no autoresponder mailing id set')
			if not parameter.company_id:
				raise error ('no company id set')
			mailing_id = parameter.autoresponder_mailing_id
			company_id = parameter.company_id
			if cinfo is None:
				raise error ('failed to determinate origin of mail')
			if not cinfo.valid:
				raise error ('uid from foreign instance %s (expected from %s)' % (cinfo.licence_id, licence))
			customer_id = cinfo.customer_id
			rdir_domain = None
			#
			if db.isopen ():
				rq = db.querys (
					'SELECT mailinglist_id, company_id, deleted '
					'FROM mailing_tbl '
					'WHERE mailing_id = :mailing_id',
					{'mailing_id': mailing_id}
				)
				if rq is None:
					raise error ('mailing %d not found' % mailing_id)
				if rq.company_id != company_id:
					raise error ('mailing %d belongs to company %d, but mailloop belongs to company %d' % (mailing_id, rq[1], company_id))
				if rq.deleted:
					logger.info ('mailing %d is marked as deleted' % mailing_id)
				mailinglist_id = rq.mailinglist_id
				#
				rq = db.querys (
					'SELECT user_type '
					'FROM customer_%d_binding_tbl '
					'WHERE customer_id = :customer_id AND mailinglist_id = :mailinglist_id AND mediatype = 0'
					% company_id,
					{
						'customer_id': customer_id,
						'mailinglist_id': mailinglist_id
					}
				)
				if rq is None or rq.user_type not in ('A', 'T', 't'):
					if not self.allow (db, bounce, parameter, cinfo, dryrun):
						raise error ('recipient is not allowed to received (again) an autoresponder')
				else:
					logger.info ('recipient %d on %d for %d is admin/test recipient and not blocked' % (customer_id, mailinglist_id, mailing_id))
				#
				rq = db.querys (
					'SELECT rdir_domain '
					'FROM mailinglist_tbl '
					'WHERE mailinglist_id = :mailinglist_id',
					{'mailinglist_id': mailinglist_id}
				)
				if rq is not None and rq.rdir_domain is not None:
					rdir_domain = rq.rdir_domain
				else:
					rq = db.querys (
						'SELECT rdir_domain '
						'FROM company_tbl '
						'WHERE company_id = :company_id',
						{'company_id': company_id}
					)
					if rq is not None:
						rdir_domain = rq.rdir_domain
				if rdir_domain is None:
					raise error ('failed to determinate rdir-domain')
					#
				rq = db.querys (
					'SELECT security_token '
					'FROM mailloop_tbl '
					'WHERE rid = :rid',
					{'rid': int (self.aid)}
				)
				if rq is None:
					raise error ('no entry in mailloop_tbl for %s found' % self.aid)
				security_token = rq.security_token if rq.security_token else ''
				url = f'{rdir_domain}/sendMailloopAutoresponder.do'
				params: Dict[str, str] = {
					'mailloopID': self.aid,
					'companyID': str (company_id),
					'customerID': str (customer_id),
					'securityToken': security_token
				}
				if dryrun:
					print (f'Would trigger mail using {url} with {params}')
				else:
					try:
						(success, response) = invoke (url, params = params)
						if success:
							logger.info ('Autoresponder mailing %d for customer %d triggered: %s' % (mailing_id, customer_id, response))
						else:
							logger.warning (f'Autoresponder mailing {mailing_id} for customer {customer_id} failed due to: {response} with {response.text}')
					except Exception as e:
						logger.error (f'Failed to trigger {url}: {e}')

		except error as e:
			logger.info ('Failed to send autoresponder: %s' % str (e))
		except (KeyError, ValueError, TypeError) as e:
			logger.error ('Failed to parse %s: %s' % (parameter, str (e)))
#
@dataclass
class Entry:
	pattern: str
	action: Optional[str] = None
	regexp: Pattern[str] = field (init = False)
	action_pattern: ClassVar[Pattern[str]] = re.compile ('^(\\{([^}]+)\\})(.*)$')

	@classmethod
	def parse (cls, line: str) -> Entry:
		match = cls.action_pattern.match (line)
		action: Optional[str]
		pattern: str
		if match is not None:
			(_, action, pattern) = match.groups ()
		else:
			action = None
			pattern = line
		return cls (pattern, action)
		
	def __post_init__ (self) -> None:
		self.regexp = re.compile (self.pattern, re.IGNORECASE)
		
	def match (self, line: str) -> bool:
		return self.regexp.search (line) is not None

@dataclass
class Section:
	name: str
	entries: List[Entry] = field (default_factory = list)
	def append (self, line: str) -> None:
		try:
			self.entries.append (Entry.parse (line))
		except re.error as e:
			logger.error ('Got illegal regular expression "%s" in [%s]: %s' % (line, self.name, e))

	def match (self, line: str) -> Optional[Entry]:
		for e in self.entries:
			if e.match (line):
				return e
		return None

@dataclass
class Scan:
	section: Optional[Section] = None
	entry: Optional[Entry] = None
	reason: Optional[str] = None
	dsn: Optional[str] = None
	etext: Optional[str] = None
	minfo: Optional[ParseEMail.Origin] = None

class Rule:
	__slots__ = ['rules', 'sections']
	DSNRE = (
		re.compile ('[45][0-9][0-9] +([0-9]\\.[0-9]\\.[0-9]+) +(.*)'),
		re.compile ('\\(#([0-9]\\.[0-9]\\.[0-9]+)\\)'),
		re.compile ('^([0-9]\\.[0-9]\\.[0-9+])')
	)
	def __init__ (self, rules: Dict[str, List[str]]) -> None:
		self.rules = rules
		self.sections: Dict[str, Section] = {}
		for (name, patterns) in self.rules.items ():
			self.sections[name] = section = Section (name)
			for pattern in patterns:
				section.append (pattern)
	
	def __collect_sections (self, use: List[str]) -> List[Section]:
		return [_s for (_n, _s) in self.sections.items () if _n in use]
	
	def __match (self, line: str, sects: List[Section]) -> Tuple[Optional[Section], Optional[Entry]]:
		for s in sects:
			entry = s.match (line)
			if entry:
				return (s, entry)
		return (None, None)
	
	def __check_header (self, msg: EmailMessage, sects: List[Section]) -> Optional[Tuple[Section, Entry, str]]:
		try:
			for key in msg.keys ():
				try:
					value = msg[key]
					line = f'{key}: {value}'
					(sec, ent) = self.__match (line, sects)
					if sec and ent:
						reason = '[%s/%s] %s' % (sec.name, ent, line)
						return (sec, ent, reason)
				except Exception as e:
					logger.debug (f'{key.lower ()}: ignore invalid header: {e}')
		except Exception as e:
			logger.warning (f'failed to check header due to: {e}')
		return None

	def match_header (self, msg: EmailMessage, use: List[str]) -> Optional[Tuple[Section, Entry, str]]:
		return self.__check_header (msg, self.__collect_sections (use))

	def __scan (self, msg: EmailMessage, scan: Scan, sects: List[Section], checkheader: bool, level: int) -> None:
		if checkheader:
			if not scan.section:
				rc = self.__check_header (msg, sects)
				if rc:
					(scan.section, scan.entry, scan.reason) = rc
		subj = msg['subject']
		if not scan.dsn:
			if subj:
				mt = Rule.DSNRE[0].search (str (subj))
				if mt:
					grps = mt.groups ()
					scan.dsn = grps[0]
					scan.etext = grps[1]
					logger.debug ('Found DSN in Subject: %s' % subj)
			if not scan.dsn:
				action = msg['action']
				status = msg['status']
				if action and status:
					mt = Rule.DSNRE[2].match (str (status))
					if mt:
						scan.dsn = mt.groups ()[0]
						scan.etext = f'Action: {action}'
						logger.debug ('Found DSN in Action: %s / Status: %s' % (action, status))
		pl = msg.get_payload (decode = True)
		if not pl:
			pl = msg.get_payload ()
		if isinstance (pl, bytes):
			try:
				pl = pl.decode ('UTF-8')
			except UnicodeDecodeError:
				pl = pl.decode ('UTF-8', errors = 'backslashreplace')
		if isinstance (pl, str):
			for line in pl.split ('\n'):
				if not scan.section:
					(sec, ent) = self.__match (line, sects)
					if sec and ent:
						scan.section = sec
						scan.entry = ent
						scan.reason = line
						logger.debug ('Found pattern "%s" in body "%s"' % (scan.entry.pattern, line))
				if not scan.dsn:
					mt = Rule.DSNRE[0].search (line)
					if mt:
						grps = mt.groups ()
						scan.dsn = grps[0]
						scan.etext = grps[1]
						logger.debug ('Found DSN %s / Text "%s" in body: %s' % (scan.dsn, scan.etext, line))
					else:
						mt = Rule.DSNRE[1].search (line)
						if mt:
							scan.dsn = mt.groups ()[0]
							scan.etext = line
							logger.debug ('Found DSN %s in body: %s' % (scan.dsn, line))
		elif type (pl) is list:
			for p in cast (List[EmailMessage], pl):
				self.__scan (p, scan, sects, True, level + 1)
				if scan.section and scan.dsn and scan.minfo:
					break
	
	def scan_message (self, cinfo: Optional[ParseEMail.Origin], msg: EmailMessage, use: List[str]) -> Scan:
		rc = Scan ()
		rc.minfo = cinfo
		sects = self.__collect_sections (use)
		self.__scan (msg, rc, sects, True, 0)
		if rc.section:
			if not rc.dsn:
				if rc.section.name == 'hard':
					rc.dsn = '5.9.9'
				else:
					rc.dsn = '4.9.9'
		if not rc.etext:
			if rc.reason:
				rc.etext = rc.reason
			else:
				rc.etext = ''
		logger.debug ('Scan results to section={section}, entry={entry}, reason={reason}, dsn={dsn}, error={error}, origin={origin}'.format (
			section = rc.section.name if rc.section is not None else '-',
			entry = '{action}: {pattern}'.format (action = rc.entry.action if rc.entry.action else '-', pattern = rc.entry.pattern) if rc.entry is not None else '-',
			reason = rc.reason if rc.reason is not None else '-',
			dsn = rc.dsn if rc.dsn is not None else '-',
			error = rc.etext if rc.etext is not None else '-',
			origin = rc.minfo if rc.minfo is not None else '-'
		))
		return rc
#
class BavBounce (Bounce):
	__slots__ = ['rulefile']
	rule_parser = Lineparser (
		lambda l: l.split (';', 2),
		'name',
		'section',
		'pattern'
	)
	def set_rulefile (self, rulefile: Optional[str] = None) -> None:
		self.rulefile = rulefile
	
	def read (self, *, read_rules: bool = True, read_config: bool = True) -> None:
		super ().read (read_rules = read_rules, read_config = read_config)
		if read_rules and self.rulefile and os.path.isfile (self.rulefile):
			with open (self.rulefile) as fd:
				try:
					master_rule = self.rules[(0, 0)]
				except KeyError:
					master_rule = self.rules[(0, 0)] = {}
				for (lineno, line) in enumerate ((_l.strip () for _l in fd), start = 1):
					if line and not line.startswith ('#'):
						try:
							Entry.parse (line)
							rule = self.rule_parser (line)
							if not rule.section:
								raise error ('missing section')
							if rule.section not in ['systemmail', 'filter', 'hard', 'soft']:
								raise error (f'unknown section {rule.section}')
							if not rule.pattern:
								raise error ('missing pattern')
						except Exception as e:
							log_limit (logger.warning, f'{self.rulefile}:{lineno}: invalid line "{line}": {e}')
						else:
							try:
								section = master_rule[rule.section]
							except KeyError:
								section = master_rule[rule.section] = []
							if rule.pattern not in section:
								section.append (rule.pattern)
#
class BAVConfig:
	__slots__ = ['config']
	config_file = os.path.join (base, 'var', 'lib', 'bav.conf')
	address_pattern = re.compile ('<([^>]*)>')
	class Parser (Tokenparser):
		__slots__: List[str] = []
		class Subscribe (NamedTuple):
			mailinglist_id: int
			form_id: int
		def __init__ (self) -> None:
			super ().__init__ (
				Field ('sender', self.__parse_address, optional = True, source = 'from'),
				Field ('to', self.__parse_address, optional = True),
				Field ('rid', atoi, optional = True, default = lambda: 0),
				Field ('rid_name', optional = True, source = 'rid'),
				Field ('company_id', int, optional = True, source = 'cid'),
				Field ('forward', self.__listsplit, optional = True, source = 'fwd'),
				Field ('spam_email', self.__listsplit, optional = True),
				Field ('spam_forward', float, optional = True, source = 'spam_fwd'),
				Field ('spam_required', float, optional = True, source = 'spam_req'),
				Field ('autoresponder', lambda a: a, optional = True, source = 'ar'),
				Field ('autoresponder_mailing_id', int, optional = True, source = 'armid'),
				Field ('subscribe', self.__parse_subscribe, optional = True, source = 'sub')
			)
		
		def parse (self, line: str) -> Dict[str, str]:
			return (Stream (line.split (','))
				.map (lambda t: unescape (t).split ('=', 1))
				.filter (lambda kv: len (kv) == 2)
				.dict ()
			)
		
		def __parse_address (self, address: str) -> str:
			match = BAVConfig.address_pattern.search (address)
			return match.group (1) if match is not None else address

		def __listsplit (self, s: str) -> List[str]:
			return list (listsplit (s))
		
		def __parse_subscribe (self, s: str) -> BAVConfig.Parser.Subscribe:
			try:
				(mailinglist_id, form_id) = s.split (':', 1)
				return BAVConfig.Parser.Subscribe (int (mailinglist_id), int (form_id))
			except ValueError:
				return BAVConfig.Parser.Subscribe (0, 0)

	parameter_parser = Parser ()		
	def __init__ (self) -> None:
		self.config: DefaultDict[str, List[str]] = defaultdict (list)
		if os.path.isfile (BAVConfig.config_file):
			with open (BAVConfig.config_file, errors = 'backslashreplace') as fd:
				aliases: DefaultDict[str, List[str]] = defaultdict (list)
				for line in (_l.strip () for _l in fd):
					with Ignore (ValueError):
						(domain, control) = line.split ('\t', 1)
						(action, parameter) = control.split (':', 1)
						if action == 'accept':
							self.config[domain].append (parameter)
						elif action == 'alias':
							aliases[domain].append (parameter)
				for (alias, domains) in aliases.items ():
					for domain in domains:
						if domain in self.config:
							self.config[alias] += self.config[domain]
	
	def __getitem__ (self, address: str) -> List[str]:
		try:
			return self.config[address]
		except KeyError:
			try:
				return self.config['@{domain}'.format (domain = address.split ('@', 1)[-1])]
			except KeyError:
				raise KeyError (address)
	
	def parse (self, parameter: str) -> Line:
		return BAVConfig.parameter_parser (parameter)

class BAV:
	__slots__ = [
		'bounce',
		'raw', 'msg', 'dryrun', 'uid_handler', 'parsed_email', 'cinfo', 'parameter',
		'header_from', 'rid', 'sender', 'rule', 'reason'
	]
	x_agn = 'X-AGNMailloop'
	has_spamassassin = which ('spamassassin') is not None
	save_pattern = os.path.join (base, 'var', 'spool', 'filter', '%s-%s')
	ext_bouncelog = os.path.join (base, 'log', 'extbounce.log')
	class From (NamedTuple):
		realname: str
		address: str
	
	def __init__ (self, bavconfig: BAVConfig, bounce: Bounce, raw: str, msg: EmailMessage, dryrun: bool = False) -> None:
		self.bounce = bounce
		self.raw = raw
		self.msg = msg
		self.dryrun = dryrun
		self.uid_handler = UIDHandler (enable_cache = True)
		self.parsed_email = ParseEMail (raw, uid_handler = self.uid_handler)
		self.cinfo = self.parsed_email.get_origin ()
		return_path = None
		return_path_header = self.msg['return-path']
		if return_path_header is not None:
			match = BAVConfig.address_pattern.search (return_path_header)
			if match is not None:
				return_path = match.group (1)
		try:
			parameter: Optional[str] = self.msg[BAV.x_agn]
		except KeyError:
			parameter = None
			if return_path is not None:
				with Ignore (ValueError, KeyError):
					(local_part, domain_part) = return_path.split ('@', 1)
					address = '{local_part}@{domain_part}'.format (local_part = local_part, domain_part = domain_part.lower ())
					parameter = bavconfig[address][0]
		if parameter is not None:
			self.parameter = bavconfig.parse (parameter)
			if (
				self.cinfo is not None and
				self.cinfo.valid and
				self.cinfo.company_id > 0 and
				self.cinfo.company_id != self.parameter.company_id and
				self.parameter.to
			):
				with Ignore (StopIteration):
					for address in (
						self.parameter.to,
						'@{domain}'.format (domain = self.parameter.to.split ('@', 1)[-1])
					):
						with Ignore (KeyError):
							for parameter in bavconfig[address]:
								new_parameter = bavconfig.parse (parameter)
								if new_parameter.company_id == self.cinfo.company_id:
									self.parameter = new_parameter._replace (sender = self.parameter.sender, to = self.parameter.to)
									raise StopIteration ()
		else:
			self.parameter = bavconfig.parse ('')

		try:
			self.header_from: Optional[BAV.From] = BAV.From (*parseaddr (cast (str, self.msg['from']))) if 'from' in self.msg else None
		except:
			self.header_from = None
		self.rid = self.parameter.rid
		if return_path is not None:
			self.sender = return_path
		elif self.parameter.sender:
			self.sender = self.parameter.sender
		else:
			self.sender = 'postmaster'
		if not msg.get_unixfrom ():
			msg.set_unixfrom (time.strftime ('From ' + self.sender + '  %c'))
		self.rule = Rule (bounce.get_rule (0 if self.cinfo is None else self.cinfo.company_id, self.rid))
		self.reason = ''

	def save_message (self, action: str) -> None:
		fname = BAV.save_pattern % (action, self.parameter.rid_name if self.parameter.rid_name else self.rid)
		if self.dryrun:
			print ('Would save message to "%s"' % fname)
		else:
			try:
				with open (fname, 'a') as fd:
					fd.write (EMail.as_string (self.msg, True) + '\n')
				logger.debug (f'Saved mesage to {fname}')
			except IOError as e:
				logger.error ('Unable to save mail copy to %s %s' % (fname, e))
	
	def sendmail (self, msg: EmailMessage, to: List[str]) -> None:
		if self.dryrun:
			print ('Would send mail to "%s"' % Stream (to).join (', '))
		else:
			try:
				mailtext = EMail.as_string (msg, False)
				cmd = syscfg.sendmail (to)
				pp = subprocess.Popen (cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True, errors = 'backslashreplace')
				(pout, perr) = pp.communicate (mailtext)
				if pout:
					logger.debug ('Sendmail to "%s" outputs this for information:\n%s' % (to, pout))
				if pp.returncode or perr:
					logger.warning ('Sendmail to "%s" returns %d:\n%s' % (to, pp.returncode, perr))
				else:
					logger.debug (f'Send message to {to}')
			except Exception as e:
				logger.exception ('Sending mail to %s failed %s' % (to, e))

	__find_score = re.compile ('score=([0-9]+(\\.[0-9]+)?)')
	def filter_with_spam_assassin (self, fwd: Optional[List[str]]) -> Optional[List[str]]:
		pp = subprocess.Popen (['spamassassin'], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True, errors = 'backslashreplace')
		(pout, perr) = pp.communicate (EMail.as_string (self.msg, False))
		if pp.returncode:
			logger.warning ('Failed to filter mail through spam assassin, returns %d' % pp.returncode)
			if perr:
				logger.warning ('Error message:\n%s' % perr)
		elif pout:
			nmsg = EMail.from_string (pout)
			if nmsg is not None:
				self.msg = nmsg
				spam_status = nmsg['x-spam-status']
				if spam_status is not None:
					try:
						m = self.__find_score.search (cast (str, spam_status))
						if m is not None:
							spam_score = float (m.group (1))
							if self.parameter.spam_required is not None and self.parameter.spam_required < spam_score:
								fwd = None
							elif self.parameter.spam_forward is not None and self.parameter.spam_forward < spam_score:
								fwd = self.parameter.spam_email
					except ValueError as e:
						logger.warning ('Failed to parse spam score/spam parameter: %s' % str (e))
				else:
					logger.warning ('Do not find spam assassin header after filtering')
			else:
				logger.warning ('Failed to parse filtered mail')
		else:
			logger.warning ('Failed to retrieve filtered mail')
		return fwd
	
	def unsubscribe (self, db: DB, customer_id: int, mailing_id: int, user_remark: str) -> None:
		if self.dryrun:
			print (f'Would unsubscribe {customer_id} due to mailing {mailing_id} with {user_remark}')
			return
		#
		if db.isopen ():
			rq = db.querys ('SELECT mailinglist_id, company_id FROM mailing_tbl WHERE mailing_id = :mailing_id', {'mailing_id': mailing_id})
			if rq is not None:
				mailinglist_id = rq.mailinglist_id
				company_id = rq.company_id
				cnt = db.update (
					'UPDATE customer_%d_binding_tbl '
					'SET user_status = :userStatus, user_remark = :user_remark, timestamp = CURRENT_TIMESTAMP, exit_mailing_id = :mailing_id '
					'WHERE customer_id = :customer_id AND mailinglist_id = :mailinglist_id'
					% company_id,
					{
						'userStatus': UserStatus.OPTOUT.value,
						'user_remark': user_remark,
						'mailing_id': mailing_id,
						'customer_id': customer_id,
						'mailinglist_id': mailinglist_id
					}
				)
				if cnt > 0:
					logger.info ('Unsubscribed customer %d for company %d on mailinglist %d due to mailing %d using %s' % (customer_id, company_id, mailinglist_id, mailing_id, user_remark))
				else:
					logger.warning ('Failed to unsubscribe customer %d for company %d on mailinglist %d due to mailing %d, matching %d rows (expected one row)' % (customer_id, company_id, mailinglist_id, mailing_id, cnt))
				db.sync ()
			else:
				logger.debug (f'No mailing for {mailing_id} found')

	def subscribe (self, db: DB, address: str, fullname: str, company_id: int, mailinglist_id: int, formular_id: int) -> None:
		if self.dryrun:
			print ('Would try to subscribe "%s" (%r) on %d/%d sending DOI using %r' % (address, fullname, company_id, mailinglist_id, formular_id))
			return
		#
		if db.isopen ():
			logger.info ('Try to subscribe %s (%s) for %d to %d using %d' % (address, fullname, company_id, mailinglist_id, formular_id))
			customer_id: Optional[int] = None
			new_binding = True
			send_mail = True
			user_remark = 'Subscribe via mailloop #%s' % self.rid
			custids = (db.stream ('SELECT customer_id FROM customer_%d_tbl WHERE email = :email' % company_id, {'email': address })
				.map_to (int, lambda r: r.customer_id)
				.list ()
			)
			if custids:
				logger.info ('Found these customer_ids %s for the email %s' % (custids, address))
				query = 'SELECT customer_id, user_status FROM customer_%d_binding_tbl WHERE customer_id ' % company_id
				if len (custids) > 1:
					query += 'IN ('
					sep = ''
					for custid in custids:
						query += '%s%d' % (sep, custid)
						sep = ', '
					query += ')'
				else:
					query += '= %d' % custids[0]
				query += ' AND mailinglist_id = %d AND mediatype = 0' % mailinglist_id
				use: Optional[Row] = None
				for rec in db.query (query):
					logger.info (f'Found binding [cid, status] {rec}')
					if rec.user_status == UserStatus.ACTIVE.value:
						if use is None or use.user_status != UserStatus.ACTIVE.value or rec.user_status > use.user_status:
							use = rec
					elif use is None or (use.user_status != UserStatus.ACTIVE.value and rec.customer_id > use.customer_id):
						use = rec
				if use is not None:
					logger.info ('Use customer_id %d with user_status %d' % (use.customer_id, use.user_status))
					customer_id = use.customer_id
					new_binding = False
					if use.user_status in (UserStatus.ACTIVE.value, UserStatus.WAITCONFIRM.value):
						logger.info ('User status is %d, stop processing here' % use.user_status)
						send_mail = False
					else:
						logger.info ('Set user status to 5')
						db.update (
							'UPDATE customer_%d_binding_tbl '
							'SET timestamp = CURRENT_TIMESTAMP, user_status = :user_status, user_remark = :user_remark '
							'WHERE customer_id = :customer_id AND mailinglist_id = :mailinglist_id AND mediatype = 0'
							% company_id,
							{
								'user_status': UserStatus.WAITCONFIRM.value,
								'user_remark': user_remark,
								'customer_id': customer_id,
								'mailinglist_id': mailinglist_id
							},
							commit = True
						)
				else:
					customer_id = max (custids)
					logger.info ('No matching binding found, use cutomer_id %s' % customer_id)
			else:
				datasource_description = 'Mailloop #%s' % self.rid
				dsid = Datasource ()
				datasource_id = dsid.get_id (datasource_description, company_id, 4)
				if db.dbms in ('mysql', 'mariadb'):
					db.update (
						'INSERT INTO customer_%d_tbl (email, gender, mailtype, timestamp, creation_date, datasource_id) '
						'VALUES (:email, 2, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :datasource_id)'
						% company_id,
						{
							'email': address,
							'datasource_id': datasource_id
						},
						commit = True
					)
					for rec in db.query ('SELECT customer_id FROM customer_%d_tbl WHERE email = :email' % company_id, {'email': address}):
						customer_id = rec.customer_id
				elif db.dbms == 'oracle':
					for rec in db.query ('SELECT customer_%d_tbl_seq.nextval FROM dual' % company_id):
						customer_id = rec[0]
					logger.info ('No customer for email %s found, use new customer_id %s' % (address, customer_id))
					if customer_id is not None:
						logger.info ('Got datasource id %s for %s' % (datasource_id, datasource_description))
						prefix = 'INSERT INTO customer_%d_tbl (customer_id, email, gender, mailtype, timestamp, creation_date, datasource_id' % company_id
						values = 'VALUES (:customer_id, :email, 2, 1, sysdate, sysdate, :datasource_id'
						data = {
							'customer_id': customer_id,
							'email': address,
							'datasource_id': datasource_id
						}
						parts = fullname.split ()
						while len (parts) > 2:
							if parts[0] and parts[0][-1] == '.':
								parts = parts[1:]
							elif parts[1] and parts[1][-1] == '.':
								parts = parts[:1] + parts[2:]
							else:
								temp = [parts[0], ' '.join (parts[1:])]
								parts = temp
						if len (parts) == 2:
							prefix += ', firstname, lastname'
							values += ', :firstname, :lastname'
							data['firstname'] = parts[0]
							data['lastname'] = parts[1]
						elif len (parts) == 1:
							prefix += ', lastname'
							values += ', :lastname'
							data['lastname'] = parts[0]
						query = prefix + ') ' + values + ')'
						logger.info ('Using "%s" with %s to write customer to database' % (query, data))
						try:
							db.update (query, data, commit = True)
						except Exception as e:
							logger.error ('Failed to insert new customer %r: %s' % (address, e))
							customer_id = None
			if customer_id is not None:
				if new_binding:
					db.update (
						'INSERT INTO customer_%d_binding_tbl '
						'            (customer_id, mailinglist_id, user_type, user_status, user_remark, timestamp, creation_date, mediatype) '
						'VALUES '
						'            (:customer_id, :mailinglist_id, :user_type, :user_status, :user_remark, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)'
						% company_id,
						{
							'customer_id': customer_id,
							'mailinglist_id': mailinglist_id,
							'user_type': 'W',
							'user_status': UserStatus.WAITCONFIRM.value,
							'user_remark': user_remark
						},
						commit = True
					)
					logger.info ('Created new binding using')
				if send_mail:
					formname = None
					rdir = None
					for rec in db.query ('SELECT formname FROM userform_tbl WHERE form_id = %d AND company_id = %d' % (formular_id, company_id)):
						if rec.formname:
							formname = rec.formname
					for rec in db.query ('SELECT rdir_domain FROM mailinglist_tbl WHERE mailinglist_id = %d' % mailinglist_id):
						rdir = rec.rdir_domain
					if rdir is None:
						for rec in db.query ('SELECT rdir_domain FROM company_tbl WHERE company_id = %d' % company_id):
							if rdir is None:
								rdir = rec.rdir_domain
					if not formname is None and not rdir is None:
						mailing_id: Optional[int] = None
						creation_date: Optional[datetime] = None
						for rec in db.queryc ('SELECT mailing_id, creation_date FROM mailing_tbl WHERE company_id = %d AND (deleted = 0 OR deleted IS NULL)' % company_id):
							if rec.mailing_id is not None:
								mailing_id = rec.mailing_id
								creation_date = rec.creation_date
								break
						if mailing_id is not None and creation_date is not None:
							try:
								uid = UID (
									company_id = company_id,
									mailing_id = mailing_id,
									customer_id = customer_id
								)
								url = f'{rdir}/form.action'
								params: Dict[str, str] = {
									'agnCI': str (company_id),
									'agnFN': formname,
									'agnUID': self.uid_handler.create (uid)
								}
								logger.info (f'Trigger mail using {url} with {params}')
								(success, response) = invoke (url, params = params)
								logger.info (f'Subscription request returns "{response}" with "{response.text}"')
								resp = response.text.strip ()
								if not success or not isinstance (resp, str) or not resp.lower ().startswith ('ok'):
									logger.error (f'Subscribe formular "{url}" returns error "{resp}"')
							except Exception as e:
								logger.error (f'Failed to trigger [prot] forumlar using "{url}": {e}')
						else:
							logger.error ('Failed to find active mailing for company %d' % company_id)
					else:
						if not formname:
							logger.error ('No formular with id #%d found' % formular_id)
						if not rdir:
							logger.error ('No rdir domain for company #%d/mailinglist #%d found' % (company_id, mailinglist_id))

	def execute_is_systemmail (self) -> bool:
		if self.parsed_email.unsubscribe:
			return True
		return self.rule.match_header (self.msg, ['systemmail']) is not None
	
	def execute_filter_or_forward (self, db: DB) -> bool:
		if self.parsed_email.ignore:
			action = 'ignore'
		else:
			match = self.rule.match_header (self.msg, ['filter'])
			if not match is None:
				if not match[1].action:
					action = 'save'
				else:
					action = match[1].action
			else:
				action = 'sent'
		fwd: Optional[List[str]] = None
		if action == 'sent':
			fwd = self.parameter.forward
			if BAV.has_spamassassin and (self.parameter.spam_forward is not None or self.parameter.spam_required is not None):
				fwd = self.filter_with_spam_assassin (fwd)
		self.save_message (action)
		if action == 'sent':
			while BAV.x_agn in self.msg:
				del self.msg[BAV.x_agn]
			if fwd is not None:
				self.sendmail (self.msg, fwd)

			if self.parameter.autoresponder:
				if self.parameter.sender and self.header_from is not None and self.header_from.address:
					sender = self.header_from.address
					auto_responder = Autoresponder (self.parameter.autoresponder, sender)
					if self.parameter.autoresponder_mailing_id:
						logger.info ('Trigger autoresponder message for %s' % sender)
						auto_responder.trigger_message (db, self.bounce, self.cinfo, self.parameter, self.dryrun)
					else:
						logger.warning ('Old autorepsonder without content found')
				else:
					logger.info ('No sender in original message found')
			if (
				self.parameter.subscribe and
				self.parameter.subscribe.mailinglist_id and
				self.parameter.subscribe.form_id and
				self.parameter.company_id and
				self.parameter.sender and
				self.header_from is not None and
				self.header_from.address
			):
				with log ('subscribe'):
					self.subscribe (
						db,
						self.header_from.address.lower (),
						self.header_from.realname,
						self.parameter.company_id,
						self.parameter.subscribe.mailinglist_id,
						self.parameter.subscribe.form_id
					)
		return True

	def execute_scan_and_unsubscribe (self, db: DB) -> bool:
		if self.parsed_email.ignore:
			action = 'ignore'
		else:
			action = 'unspec'
			scan = self.rule.scan_message (self.cinfo, self.msg, ['hard', 'soft'])
			if scan:
				if scan.entry and scan.entry.action:
					action = scan.entry.action
				if scan.minfo:
					if self.parsed_email.unsubscribe:
						action = 'unsubscribe'
						with log ('unsubscribe'):
							user_remark = 'Opt-out by mandatory CSA link (mailto)'
							self.unsubscribe (db, scan.minfo.customer_id, scan.minfo.mailing_id, user_remark)
					else:
						if scan.section:
							if self.dryrun:
								print ('Would write bouncelog with: %s, %d, %d, %s' % (scan.dsn, scan.minfo.mailing_id, scan.minfo.customer_id, scan.etext.strip () if isinstance (scan.etext, str) else scan.etext))
							else:
								try:
									with open (BAV.ext_bouncelog, 'a') as fd:
										fd.write ('%s;%s;%s;0;%s;timestamp=%s\tmailloop=%s\tserver=%s\n' % (scan.dsn, licence, scan.minfo.mailing_id, scan.minfo.customer_id, ParseTimestamp ().dump (datetime.now ()), scan.etext, fqdn))
								except IOError as e:
									logger.error ('Unable to write %s %s' % (BAV.ext_bouncelog, e))
		self.save_message (action)
		return True

class BAVD (Runtime):
	__slots__ = ['max_children', 'delay', 'spooldir', 'worksize', 'size', 'rulefile', 'files']
	def check_procmailrc (self, now: time.struct_time, spool: Mailspool) -> None:
		prc = os.path.join (base, '.procmailrc')
		try:
			with open (prc, errors = 'backslashreplace') as fd:
				ocontent = fd.read ()
		except IOError as e:
			if e.args[0] != errno.ENOENT:
				logger.warning ('Failed to read "%s": %r' % (prc, e.args))
			ocontent = ''
		ncontent = """# This file is generated by bavd, do not edit it by hand
:0:
%(path)s/%(ts)s-inbox
""" % {'path': spool.store, 'ts': '%04d%02d%02d' % (now.tm_year, now.tm_mon, now.tm_mday)}
		if ocontent != ncontent:
			try:
				with open (prc, 'w') as fd:
					fd.write (ncontent)
				os.chmod (prc, 0o600)
				logger.info ('Create new procmailrc file "%s".' % prc)
			except (IOError, OSError) as e:
				logger.error ('Failed to install procmailrc file "%s": %r' % (prc, e.args))

	def bav_debug (self) -> None:
		log.outlevel = logging.DEBUG
		log.outstream = sys.stderr
		log.loglevel = logging.FATAL
		print ('Entering simulation mode')
		with DB () as db:
			bavconfig = BAVConfig ()
			bounce = BavBounce (db)
			bounce.set_rulefile (self.rulefile)
			bounce.read ()
			for fname in self.files:
				print ('Try to interpret: %s' % fname)
				try:
					with open (fname, errors = 'backslashreplace') as fd:
						content = fd.read ()
					bav = BAV (bavconfig, bounce, content, EMail.from_string (content), True)
					if bav.execute_is_systemmail ():
						print ('--> Scan and unsubscribe')
						ok = bav.execute_scan_and_unsubscribe (db)
					else:
						print ('--> Filter or forward')
						ok = bav.execute_filter_or_forward (db)
					if ok:
						print ('OK')
					else:
						print ('Failed')
				except IOError as e:
					print ('Failed to open %s: %r' % (fname, e.args))
	
	def setup (self) -> None:
		self.max_children = 10
		self.delay = 10
		self.spooldir = os.path.join (base, 'var', 'spool', 'mail')
		self.worksize = None
		self.size = 65536
		self.rulefile: Optional[str] = None
		self.files: List[str] = []
	
	def supports (self, option: str) -> bool:
		return option != 'dryrun'
		
	def add_arguments (self, parser: argparse.ArgumentParser) -> None:
		parser.add_argument ('-C', '--max-children', action = 'store', type = int, default = self.max_children, help = f'Set maximum number of subprocesses (default {self.max_children})', dest = 'max_children')
		parser.add_argument ('-D', '--delay', action = 'store', type = int, default = self.delay, help = f'Set delay in seconds between scan for new mails (defailt {self.delay})')
		parser.add_argument ('-S', '--spool-directory', action = 'store', default = self.spooldir, help = f'Set directory for mail processing (default {self.spooldir})', dest = 'spool_directory')
		parser.add_argument ('-W', '--worksize', action = 'store', type = int, default = self.worksize, help = 'Set size for each single batch to process')
		parser.add_argument ('-L', '--size-limit', action = 'store', type = int, default = self.size, help = f'Set limit for incoming mails before they are truncated (default {self.size} bytes)', dest = 'size_limit')
		parser.add_argument ('-R', '--rulefile', action = 'store', help = 'Add temporary content of rule file (three column, semicolumn separated, with "name;section;pattern") for debug processing')
		
	def use_arguments (self, args: argparse.Namespace) -> None:
		self.max_children = args.max_children
		self.delay = args.delay
		self.spooldir = args.spool_directory
		self.worksize = args.worksize
		self.size = args.size_limit
		self.rulefile = args.rulefile
		self.files = args.parameter
	
	class Child:
		__slots__ = ['ref', 'bounce', 'ws', 'pid', 'active']
		def __init__ (self, ref: BAVD, bounce: Bounce, ws: Mailspool.Workspace) -> None:
			self.ref = ref
			self.bounce = bounce
			self.ws = ws
			self.pid: Optional[int] = None
			self.active = False
		
		def execute (self, size: int) -> None:
			bavconfig = BAVConfig ()
			db = DB ()
			try:
				for path in self.ws:
					ok = False
					try:
						with open (path, errors = 'backslashreplace') as fd:
							body = fd.read (size)
						msg = EMail.from_string (body)
						bav = BAV (bavconfig, self.bounce, body, msg)
						if bav.execute_is_systemmail ():
							with log ('scan'):
								ok = bav.execute_scan_and_unsubscribe (db)
						else:
							with log ('filter'):
								ok = bav.execute_filter_or_forward (db)
					except IOError as e:
						logger.error ('Failed to open %s: %r' % (path, e.args))
					except Exception as e:
						logger.exception ('Fatal: catched failure: %s' % e)
					if ok:
						self.ws.success (bav.sender)
					else:
						self.ws.fail ()
					if not self.ref.running:
						break
				self.ws.done ()
			finally:
				db.close ()
		
		def start (self, size: int) -> None:
			def executor () -> None:
				with self.ref.title (str (self.ws)):
					try:
						self.execute (size)
					except Exception as e:
						logger.exception (f'{self.ws}: failed due to {e}')
			self.pid = self.ref.spawn (executor)
			self.active = self.pid > 0
		
		def signal (self) -> None:
			if self.active and self.pid is not None:
				try:
					os.kill (self.pid, signal.SIGTERM)
				except OSError as e:
					if e.args[0] == errno.ECHILD:
						self.active = False

		def wait (self) -> None:
			if self.active and self.pid is not None:
				try:
					(pid, status) = os.waitpid (self.pid, os.WNOHANG)
					if pid == self.pid:
						if status:
							if os.WIFEXITED (status):
								err = 'exited with return code %d' % os.WEXITSTATUS (status)
							elif os.WIFSIGNALED (status):
								err = 'died due to signal %d' % os.WTERMSIG (status)
							else:
								err = 'terminated due to unknown status %d' % status
							logger.error ('Child for ws %s %s' % (self.ws.path, err))
						self.active = False
				except OSError as e:
					if e.args[0] == errno.ECHILD:
						self.active = False
	
	def wait_for_children (self, children: List[BAVD.Child]) -> List[BAVD.Child]:
		nchildren: List[BAVD.Child] = []
		for child in children:
			child.wait ()
			if child.active:
				nchildren.append (child)
		if len (children) != len (nchildren):
			count = len (children) - len (nchildren)
			logger.debug ('%d child%s terminated' % (count, count != 1 and 'ren' or ''))
		return nchildren
	
	def executor (self) -> bool:
		if self.files:
			self.bav_debug ()
			return True
		#
		lastCheck = -1
		bounce = BavBounce ()
		bounce.set_rulefile (self.rulefile)
		children: List[BAVD.Child] = []
		spool = Mailspool (self.spooldir, worksize = self.worksize, scan = False, store_size = self.size)
		while self.running:
			now = time.localtime ()
			if now.tm_yday != lastCheck:
				self.check_procmailrc (now, spool)
				lastCheck = now.tm_yday
			if len (children) < self.max_children:
				if len (children) == 0:
					spool.scan_workspaces ()
				for ws in spool:
					bounce.check ()
					logger.debug ('New child starting in %s' % ws.path)
					ch = BAVD.Child (self, bounce, ws)
					ch.start (self.size)
					children.append (ch)
					if len (children) >= self.max_children:
						break
			n = self.delay
			while self.running and n > 0:
				time.sleep (1)
				if children:
					children = self.wait_for_children (children)
				n -= 1
		while children:
			logger.debug ('Wait for %d children to terminate' % len (children))
			for child in children:
				child.signal ()
			time.sleep (1)
			children = self.wait_for_children (children)
		return True
	#
if __name__ == '__main__':
	BAVD.main ()
