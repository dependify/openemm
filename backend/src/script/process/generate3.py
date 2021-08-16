#!/usr/bin/env python3
####################################################################################################################################################################################################################################################################
#                                                                                                                                                                                                                                                                  #
#                                                                                                                                                                                                                                                                  #
#        Copyright (C) 2019 AGNITAS AG (https://www.agnitas.org)                                                                                                                                                                                                   #
#                                                                                                                                                                                                                                                                  #
#        This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.    #
#        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.           #
#        You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.                                                                                                            #
#                                                                                                                                                                                                                                                                  #
####################################################################################################################################################################################################################################################################
#
from	__future__ import annotations
import	logging, argparse
import	os, signal
import	time, json
from	datetime import datetime
from	dataclasses import dataclass
from	types import FrameType
from	typing import Any, Callable, Optional
from	typing import Dict, List, NamedTuple, Tuple, Type
from	typing import cast
from	agn3.daemon import Daemonic
from	agn3.db import DB
from	agn3.definitions import base, host, program
from	agn3.emm.companyconfig import CompanyConfig
from	agn3.emm.mailing import Mailing
from	agn3.ignore import Ignore
from	agn3.flow import Schedule, Jobqueue
from	agn3.parser import Unit
from	agn3.process import Processtitle
from	agn3.runtime import Runtime
from	agn3.stream import Stream
from	agn3.tools import Range
from	activator3 import Activator
#
logger = logging.getLogger (__name__)
#
class Entry: #{{{
	__slots__ = ['name', 'companyID', 'mailingID', 'statusID', 'statusField', 'sendDate', 'genDate', 'genChange', 'startDate']
	def __init__ (self,
		name: Optional[str],
		companyID: int,
		mailingID: int,
		statusID: int,
		statusField: str,
		sendDate: datetime,
		genDate: datetime,
		genChange: datetime,
		startDate: Optional[datetime] = None
	) -> None:
		self.name: str = f'#(statusID) {statusID}' if name is None else name
		self.companyID = companyID
		self.mailingID = mailingID
		self.statusID = statusID
		self.statusField = statusField
		self.sendDate = sendDate
		self.genDate = genDate
		self.genChange = genChange
		self.startDate = startDate
	
	def __repr__ (self) -> str:
		return 'Entry (%r, %r, %r, %r, %r, %r, %r, %r, %r)' % (self.name, self.companyID, self.mailingID, self.statusID, self.statusField, self.sendDate, self.genDate, self.genChange, self.startDate)
	__str__ = __repr__
#}}}
class Task: #{{{
	name = 'task'
	immediately = False
	def __init__ (self, ref: ScheduleGenerate) -> None:
		self.ref = ref
		self.db = DB ()
		self.unit = Unit ()
		
	def __del__ (self) -> None:
		self.close ()
	
	def __call__ (self) -> bool:
		rc = False
		if self.db.isopen ():
			self.ref.processtitle.push (self.name)
			try:
				self.execute ()
				self.ref.pendings ()
			except Exception as e:
				logger.exception ('failed due to: %s' % e)
			else:
				rc = True
			finally:
				self.close ()
				self.ref.processtitle.pop ()
				self.ref.lockTitle ()
		return rc
	
	def close (self) -> None:
		self.db.close ()
		
	def configuration (self, key: str, default: Any = None) -> Any:
		return self.ref.configuration (key, name = self.name, default = self.default_for (key, default))
	
	def title (self, title: Optional[str] = None) -> None:
		self.ref.processtitle ('%s%s' % (self.name, (' %s' % title) if title else ''))
	
	def default_for (self, key: str, default: Any) -> Any:
		return default
	#
	# to overwrite
	def execute (self) -> None:
		pass
#}}}
class Sending (Task): #{{{
	def __init__ (self, *args: Any, **kwargs: Any) -> None:
		super ().__init__ (*args, **kwargs)
		self.in_queue: Dict[int, Entry] = {}
		self.in_progress: Dict[int, Entry] = {}
		self.pending: Optional[List[int]] = None
		self.pending_path = os.path.join (base, 'var', 'run', 'generate-%s.pending' % self.name)
		self.load_pending ()
	
	def load_pending (self) -> None:
		if os.path.isfile (self.pending_path):
			with open (self.pending_path) as fd:
				self.pending = json.load (fd)
				logger.debug ('loaded pending: %r' % (self.pending, ))
			os.unlink (self.pending_path)
	
	def save_pending (self, pending: List[int]) -> None:
		if pending:
			with open (self.pending_path, 'w') as fd:
				json.dump (pending, fd, indent = 2, sort_keys = True)
				logger.debug ('saved pending: %r' % (pending, ))
	
	def add_to_queue (self, entry: Entry) -> None:
		self.in_queue[entry.statusID] = entry
		logger.debug ('%s: added to queue' % entry.name)
	
	def remove_from_queue (self, entry: Entry) -> None:
		with Ignore (KeyError):
			removed_entry = entry
			del self.in_queue[entry.statusID]
			logger.debug ('%s: removed from queue' % removed_entry.name)

	def is_active (self) -> bool:
		return bool (self.in_queue or self.in_progress)
	
	def change_genstatus (self, status_id: int, old_status: Optional[int], new_status: int) -> bool:
		query = (
			'UPDATE maildrop_status_tbl '
			'SET genstatus = :newStatus, genchange = :now '
			'WHERE status_id = :statusID'
		)
		data = {
			'newStatus': new_status,
			'now': datetime.now (),
			'statusID': status_id
			}
		if old_status is not None:
			query += ' AND genstatus = :oldStatus'
			data['oldStatus'] = old_status
		return self.db.update (query, data, commit = True) == 1

	def invalidate_maildrop_entry (self, status_id: int, old_status: Optional[int] = None) -> bool:
		return self.change_genstatus (status_id, old_status = old_status, new_status = 4)
		
	def execute (self) -> None:
		new = not self.is_active ()
		self.collect_entries_for_sending ()
		self.pending = None
		if new and self.is_active ():
			self.ref.defer (self, self.starter)
	
	def starter (self) -> bool:
		if self.db.isopen ():
			def duration_format (d: int) -> str:
				return ('%d:%02d:%02d' % (d // 3600, (d // 60) % 60, d % 60)) if d >= 3600 else ('%d:%02d' % (d // 60, d % 60))
			mailing = Mailing (merger = self.configuration ('merger', 'localhost'))
			expire = self.unit.parse (self.configuration ('expire', '30m'))
			parallel = self.unit.parse (self.configuration ('parallel', '4'))
			startup = self.unit.parse (self.configuration ('startup', '5m'))
			now = datetime.now ()
			if self.in_progress:
				self.title ('checking %d mailings for temination' % len (self.in_progress))
				seen = set ()
				for row in self.db.queryc (
					'SELECT status_id, genstatus, genchange '
					'FROM maildrop_status_tbl '
					'WHERE status_id IN (%s)'
					% (Stream (self.in_progress.values ())
						.map (lambda e: e.statusID)
						.join (', '),
					)
				):
					seen.add (row.status_id)
					entry = self.in_progress.pop (row.status_id)
					if row.genstatus in (3, 4) or (row.genstatus == 1 and row.genchange > entry.genChange):
						duration = int ((row.genchange - entry.startDate).total_seconds ())
						logger.info ('%s: generation finished after %s' % (entry.name, duration_format (duration)))
					elif entry.startDate is not None:
						duration = int ((now - entry.startDate).total_seconds ())
						if row.genstatus == 1:
							if duration >= startup:
								logger.warning ('%s: startup time exceeded, respool entry' % entry.name)
								if self.db.update (
									'DELETE FROM rulebased_sent_tbl WHERE mailing_id = :mailingID',
									{
										'mailingID': entry.mailingID
									},
									commit = True
								) > 0:
									logger.info ('%s: entry from rulebased_sent_tbl had been removed' % entry.name)
								else:
									logger.info ('%s: no entry in rulebased_sent_tbl found to remove' % entry.name)
								self.add_to_queue (entry)
							else:
								logger.debug ('%s: during startup since %s up to %s' % (entry.name, duration_format (duration), duration_format (startup)))
								self.in_progress[entry.statusID] = entry
						elif row.genstatus == 2:
							if duration > expire:
								logger.info ('%s: creation exceeded expiration time, leave it running' % entry.name)
							else:
								logger.debug ('%s: still in generation for %s up to %s' % (entry.name, duration_format (duration), duration_format (expire)))
								self.in_progress[entry.statusID] = entry
						else:
							logger.error ('%s: unexpected genstatus %s, leave it alone' % (entry.name, row.genstatus))
					else:
						logger.warning (f'{entry}: unset startDate, but had been started, startDate set to {now}')
						entry.startDate = now
				self.db.sync ()
				for entry in Stream (self.in_progress.values ()).filter (lambda e: e.statusID not in seen).list ():
					logger.warning ('%s: maildrop status entry vanished, remove from observing' % entry.name)
					self.in_progress.pop (entry.statusID)
				self.title ()
			#
			if len (self.in_progress) < parallel and self.in_queue:
				if not self.ref._running:
					logger.info ('Postpone generation of %d mailings due to shutdown in progress' % len (self.in_queue))
					self.save_pending (list (self.in_queue.keys ()))
					self.in_queue.clear ()
					self.in_progress.clear ()
				else:
					self.title ('try to start %d out of %d mailings' % (parallel - len (self.in_progress), len (self.in_queue)))
					for entry in list (self.in_queue.values ()):
						if not mailing.active ():
							logger.error ('%s: merger not active, abort' % entry.name)
							break
						if self.ref.islocked (entry.companyID) and entry.statusField != 'T':
							logger.debug ('%s: company %d is locked' % (entry.name, entry.companyID))
							continue
						if not self.start_entry (entry):
							logger.debug ('%s: start denied' % entry.name)
							continue
						self.remove_from_queue (entry)
						if self.ready_to_send (now, entry):
							if mailing.fire (status_id = entry.statusID, cursor = self.db.cursor):
								entry.startDate = now
								self.in_progress[entry.statusID] = entry
								logger.info ('%s: started' % entry.name)
								if len (self.in_progress) >= parallel:
									break
							else:
								logger.error ('%s: failed to start' % entry.name)
								if self.resume_entry (entry):
									self.add_to_queue (entry)
					self.db.sync ()
					self.title ()
		return self.is_active ()
	#
	# to overwrite
	def collect_entries_for_sending (self) -> None:
		pass
	def ready_to_send (self, now: datetime, entry: Entry) -> bool:
		return False
	def start_entry (self, entry: Entry) -> bool:
		return True
	def resume_entry (self, entry: Entry) -> bool:
		return False
#}}}
class Rulebased (Sending): #{{{
	name = 'rulebased'
	interval = '1h'
	immediately = True
	priority = 3
	defaults = {
		'expire':	'10m',
		'parallel':	'4',
		'startup':	'5m'
	}
	def default_for (self, key: str, default: Any) -> Any:
		try:
			return self.defaults[key]
		except KeyError:
			return default
		
	def ready_to_send (self, now: datetime, entry: Entry) -> bool:
		ready = False
		rq = self.db.querys (
			'SELECT lastsent '
			'FROM rulebased_sent_tbl '
			'WHERE mailing_id = :mailingID',
			{
				'mailingID': entry.mailingID
			}
		)
		if rq is None or rq.lastsent is None or rq.lastsent.toordinal () != now.toordinal ():
			new = rq is None
			for state in 1, 2:
				rq = self.db.querys (
					'SELECT genchange '
					'FROM maildrop_status_tbl '
					'WHERE status_id = :statusID',
					{
						'statusID': entry.statusID
					}
				)
				if rq is None:
					break
				elif rq.genchange is None and state == 1:
					self.db.update (
						'UPDATE maildrop_status_tbl '
						'SET genchange = :now '
						'WHERE status_id = :statusID',
						{
							'now': now,
							'statusID': entry.statusID
						},
						commit = True
					)
				else:
					break
			if rq is not None and rq.genchange is not None:
				entry.genChange = rq.genchange
				count = self.db.update (
					'INSERT INTO rulebased_sent_tbl (mailing_id, lastsent) VALUES (:mailingID, :now)'
						if new else
					'UPDATE rulebased_sent_tbl SET lastsent = :now WHERE mailing_id = :mailingID',
					{
						'mailingID': entry.mailingID,
						'now': now
					},
					commit = True
				)
				if count == 1:
					ready = True
				else:
					logger.error ('%s: failed to %s entry in rulebased_sent_tbl' % (entry.name, 'set' if new else 'update'))
			else:
				logger.error ('%s: failed to query current genchange' % entry.name)
		else:
			logger.warning ('%s: unexpected this mailing had been generated this day' % entry.name)
		self.db.sync ()
		return ready

	def start_entry (self, entry: Entry) -> bool:
		return Stream (self.in_progress.values ()).filter (lambda e: bool (e.companyID == entry.companyID)).count () == 0
			
	def resume_entry (self, entry: Entry) -> bool:
		return True

	def collect_entries_for_sending (self) -> None:
		now = datetime.now ()
		today = now.toordinal ()
		query = (
			'SELECT md.status_id, md.status_field, md.senddate, md.gendate, md.genchange, md.company_id, '
			'       co.shortname AS company_name, co.status, '
			'       mt.mailing_id, mt.shortname AS mailing_name, mt.deleted, '
			'       rb.lastsent '
			'FROM maildrop_status_tbl md '
			'     INNER JOIN company_tbl co ON (co.company_id = md.company_id) '
			'     INNER JOIN mailing_tbl mt ON (mt.mailing_id = md.mailing_id) '
			'     LEFT OUTER JOIN rulebased_sent_tbl rb ON (rb.mailing_id = md.mailing_id) '
			'WHERE md.genstatus = :genStatus AND md.status_field = :statusField AND md.senddate <= :now'
		)
		data = {
			'genStatus': 1,
			'statusField': 'R',
			'now': now
		}
		for row in self.db.queryc (query, data):
			msg = '%s (%d) for %s (%d)/%s' % (row.mailing_name, row.mailing_id, row.company_name, row.company_id, row.senddate)
			#
			# 1.) Skip not allowed companies
			if not self.ref.allow (row.company_id):
				logger.debug ('%s: is not on my list of allowed companies' % msg)
				continue
			#
			# 2.) Skip already sent mails for today
			if row.lastsent is not None and row.lastsent.toordinal () == today:
				logger.debug ('%s: already sent today' % msg)
				continue
			#
			# 3.) Skip already queued mails
			if row.status_id in self.in_queue:
				logger.debug ('%s: already in queue' % msg)
				continue
			#
			# 4.) Skip already processing entry
			if row.status_id in self.in_progress:
				logger.debug ('%s: is currently in production' % msg)
				continue
			#
			# 5.) Skip not yet ready to send
			if row.senddate.hour > now.hour:
				logger.debug ('%s: not yet ready to process' % msg)
				continue
			#
			# 6.) Skip outdated and keep pending entries
			if row.senddate.hour < now.hour:
				if self.pending is not None and row.status_id in self.pending:
					logger.debug ('%s: pending' % msg)
				else:
					logger.debug ('%s: outdated' % msg)
					continue
			#
			# 7.) Skip invalid company or mailing
			if row.status != 'active' or row.deleted:
				if row.status != 'active':
					logger.debug ('%s: company %s (%d) is not active, but %s' % (msg, row.company_name, row.company_id, row.status))
				if row.deleted:
					logger.debug ('%s: mailing marked as deleted' % msg)
				self.invalidate_maildrop_entry (row.status_id)
				continue
			self.add_to_queue (Entry (msg, row.company_id, row.mailing_id, row.status_id, row.status_field, row.senddate, row.gendate, row.genchange))
		self.db.sync ()
#}}}
class Worldmailing (Sending): #{{{
	name = 'generate'
	interval = '15m'
	priority = 4
	def ready_to_send (self, now: datetime, entry: Entry) -> bool:
		if not self.change_genstatus (entry.statusID, old_status = 0, new_status = 1):
			logger.error ('%s: failed to update maildrop status table' % entry.name)
			return False
		#
		entry.genChange = self.db.stream (
			'SELECT genchange FROM maildrop_status_tbl WHERE status_id = :statusID',
			{
				'statusID': entry.statusID
			}
		).map (lambda r: r[0]).first (no = None)
		if entry.genChange is None:
			logger.error ('%s: failed to query current gen change' % entry.name)
			if not self.resume_entry (entry):
				return False
		self.db.sync ()
		return True

	def resume_entry (self, entry: Entry) -> bool:
		if not self.change_genstatus (entry.statusID, old_status = 1, new_status = 0):
			logger.critical ('%s: failed to revert status id from 1 to 0' % entry.name)
			return False
		else:
			logger.info ('%s: resumed setting genstatus from 1 to 0' % entry.name)
			return True

	def collect_entries_for_sending (self) -> None:
		query = (
			'SELECT md.status_id, md.status_field, md.senddate, md.gendate, md.genchange, md.company_id, md.optimize_mail_generation, '
			'       co.shortname AS company_name, co.status, mt.mailing_id, mt.shortname AS mailing_name, mt.deleted '
			'FROM maildrop_status_tbl md INNER JOIN company_tbl co ON (co.company_id = md.company_id) INNER JOIN mailing_tbl mt ON (mt.mailing_id = md.mailing_id) '
			'WHERE md.genstatus = 0 AND ( '
			'      (md.status_field = \'W\' AND md.gendate <= :now) '
			'      OR '
			'      (md.status_field = \'T\' AND md.senddate <= :now) '
			') ORDER BY md.status_id'
		)
		now = datetime.now ()
		limit = None
		if self.ref.oldest >= 0:
			limit = now.fromordinal (now.toordinal () - self.ref.oldest)
		for row in self.db.queryc (query, {'now': now}):
			msg = 'Mailing "%s" (mailingID=%d, statusID=%d, statusField=%r, company=%s, companyID=%d)' % (
				row.mailing_name, row.mailing_id, 
				row.status_id, row.status_field,
				row.company_name, row.company_id
			)
			if not self.ref.allow (row.company_id):
				logger.debug ('%s: not in my list of allowed companies' % msg)
				continue
			startIt = False
			keepIt = False
			if row.status != 'active':
				logger.info ('%s: company is not active, but %s' % (msg, row.status))
			elif row.deleted:
				logger.info ('%s: mailing is marked as deleted' % msg)
			elif limit is not None and row.gendate is not None and row.gendate < limit:
				logger.info ('%s: mailing gendate is too old (%s, limit is %s)' % (msg, str (row.gendate), str (limit)))
			else:
				if (
					row.optimize_mail_generation is not None and
					row.optimize_mail_generation == 'day' and
					row.senddate is not None and
					row.senddate.toordinal () > now.toordinal ()
				):
					logger.info ('%s: day based optimized mailing will not be generate on a previous day, deferred' % msg)
					keepIt = True
				else:
					startIt = True
			if startIt:
				if row.status_id in self.in_queue:
					logger.info ('%s: already queued' % msg)
				else:
					self.add_to_queue (Entry (msg, row.company_id, row.mailing_id, row.status_id, row.status_field, row.senddate, row.gendate, row.genchange))
					logger.info ('%s: added to queue' % msg)
			else:
				if row.status_id in self.in_queue:
					logger.info ('%s: queued, remove it from queue' % msg)
					self.remove_from_queue (row.status_id)
				if not keepIt:
					if self.invalidate_maildrop_entry (row.status_id, old_status = 0):
						logger.info ('%s: disabled' % msg)
					else:
						logger.error ('%s: failed to disable' % msg);
		self.db.sync ()
#}}}
class ScheduleGenerate (Schedule): #{{{
	__slots__ = ['modules', 'oldest', 'processes', 'control', 'deferred', 'config', 'companies', 'locks', 'processtitle']
	@dataclass
	class Pending:
		description: str
		method: Callable[..., bool]
		prepare: Optional[Callable[..., None]]
		finalize: Optional[Callable[..., None]]
		args: Tuple[Any, ...]
		kwargs: Dict[str, Any]
		pid: Optional[int]
	class Control (NamedTuple):
		subprocess: Daemonic
		queued: Dict[int, List[ScheduleGenerate.Pending]]
		running: List[ScheduleGenerate.Pending]
	class Deferred (NamedTuple):
		task: Task
		description: str
		method: Callable[..., bool]
		args: Tuple[Any, ...]
		kwargs: Dict[str, Any]
	def __init__ (self, modules: Dict[str, Type[Task]], oldest: int, processes: int, *args: Any, **kwargs: Any) -> None:
		super ().__init__ (*args, **kwargs)
		self.modules = modules
		self.oldest = oldest
		self.processes = processes
		self.control = ScheduleGenerate.Control (Daemonic (), {}, [])
		self.deferred: List[ScheduleGenerate.Deferred] = []
		self.config: Dict[str, str] = {}
		self.companies: Optional[Range] = None
		self.locks: Dict[int, int] = {}
		self.processtitle = Processtitle ('$original [$title]')
	
	def readConfiguration (self) -> None:
		ccfg = CompanyConfig ()
		ccfg.read ()
		self.config = (Stream (ccfg.scan_config (class_names = ['generate'], single_value = True))
			.map (lambda cv: (cv.name, cv.value))
			.dict ()
		)
		self.companies = self.configuration (
			'companies',
			convert = lambda v: Stream.ifelse (Range (v))
		)
		if self.companies:
			logger.info ('Limit operations on these companies: %s' % self.companies)
	
	def configuration (self, key: str, name: Optional[str] = None, default: Any = None, convert: Optional[Callable[[Any], Any]] = None) -> Any:
		return (
			Stream.of (
				('%s:%s[%s]' % (name, key, host)) if name is not None else None,
				'%s[%s]' % (key, host),
				('%s:%s' % (name, key)) if name is not None else None,
				key
			)
			.filter (lambda k: k is not None and k in self.config)
			.map (lambda k: self.config[k])
			.first (no = default, finisher = lambda v: v if convert is None or v is None else convert (v))
		)
	
	def allow (self, companyID: int) -> bool:
		return self.companies is None or companyID in self.companies

	def title (self, info: Optional[str] = None) -> None:
		self.processtitle ('schedule%s' % ((' %s' % info) if info else ''))

	def reload (self, sig: signal.Signals, stack: FrameType) -> None:
		self.readConfiguration ()
		
	def status (self, sig: signal.Signals, stack: FrameType) -> None:
		self.show_status ()
	
	def show_status (self) -> None:
		logger.info ('Currently blocked companies: %s' % (Stream.of (self.locks.items ()).map (lambda kv: '%s=%r' % kv).join (', ') if self.locks else 'none', ))
		for (name, queue) in Stream.of (self.control.queued.items ()).map (lambda kv: ('queued prio %d' % kv[0], kv[1])).list () + [('running', self.control.running)]:
			logger.info ('Currently %d %s processes' % (len (queue), name))
			for entry in queue:
				logger.info ('  %s%s' % (entry.description, (' (%d)' % entry.pid if entry.pid is not None else '')))
		for job in self.deferred:
			logger.info ('%s: deferred' % job.description)
		if self._schedule.queue:
			logger.info ('Currently scheduled events:')
			for event in self._schedule.queue:
				ts = event.time % (24 * 60 * 60)
				logger.info ('\t%2d:%02d:%02d [Prio %d]: %s' % (
					ts // 3600, (ts // 60) % 60, ts % 60,
					event.priority, cast (Schedule.Job, event.action).name
				))
	
	def log (self, area: str, message: str) -> None:
		logger.debug (f'sched/{area}: {message}')

	def start (self) -> None:
		self.title ()
		self.readConfiguration ()
		(Stream.of (self.modules.values ())
			.sorted (key = lambda task: task.priority)
			.each (lambda task: self.every (
				task.name,
				self.configuration (
					'immediately',
					name = task.name,
					default = task.immediately
				),
				self.configuration (
					'interval',
					name = task.name,
					default = task.interval,
					convert = lambda v: Stream.ifelse (v, alternator = task.interval)
				),
				task.priority,
				task (self),
				()
			))
		)
		def configurator () -> bool:
			self.readConfiguration ()
			return True
		def stopper () -> bool:
			while self.control.running:
				if self.wait () is None:
					break
			if not self.control.running and not self.deferred:
				self.stop ()
				return False
			return True
		self.every ('reload', False, '1h', 0, configurator, ())
		self.every ('restart', False, '24h', 0, stopper, ())
		super ().start ()
	
	def term (self) -> None:
		super ().term ()
		if self.control.running:
			self.title ('in termination')
			(Stream.of (self.control.running)
				.peek (lambda p: logger.info ('Sending terminal signal to %s' % p.description))
				.each (lambda p: self.control.subprocess.term (p.pid))
			)
			while self.control.running:
				logger.info ('Waiting for %d remaining child processes' % len (self.control.running))
				self.wait (True)
		if self.deferred:
			logger.info ('Schedule final run for %d deferred tasks' % len (self.deferred))
			self.defers ()

	def wait (self, block: bool = False) -> Optional[ScheduleGenerate.Pending]:
		w: Optional[ScheduleGenerate.Pending] = None
		while self.control.running and w is None:
			rc = self.control.subprocess.join (timeout = None if block else 0)
			if not rc.pid:
				break
			#
			w = (Stream.of (self.control.running)
				.filter (lambda r: bool (r.pid == rc.pid))
				.first (no = None)
			)
			if w is not None:
				logger.debug ('{desc}: returned with {ec}'.format (
					desc = w.description,
					ec = f'exit with {rc.exitcode}' if rc.exitcode is not None else f'died due to signal {rc.signal}'
				))
				if w.finalize is not None:
					try:
						w.finalize (rc, *w.args, **w.kwargs)
					except Exception as e:
						logger.exception ('%s: finalize fails: %s' % (w.description, e))
				self.control.running.remove (w)
				self.lockTitle ()
		return w

	def defers (self) -> bool:
		for job in self.deferred[:]:
			logger.debug ('%s: starting' % job.description)
			self.processtitle.push (job.description)
			try:
				if not job.method (*job.args, **job.kwargs):
					logger.debug ('%s: finished' % job.description)
					self.deferred.remove (job)
					job.task.close ()
				else:
					logger.debug ('%s: still active' % job.description)
			finally:
				self.processtitle.pop ()
		return bool (self.deferred)
	
	def defer (self, task: Task, method: Callable[..., bool], *args: Any, **kwargs: Any) -> None:
		self.deferred.append (ScheduleGenerate.Deferred (task, task.name, method, args, kwargs))
		if len (self.deferred) == 1:
			self.every ('defer', False, '10s', 0, self.defers, ())

	def pendings (self) -> bool:
		while self.control.running:
			pending = self.wait ()
			if pending is None:
				break
			logger.debug ('%s: process finished' % pending.description)
		while self.control.queued and len (self.control.running) < self.processes:
			prio = Stream.of (self.control.queued.keys ()).sorted ().first ()
			w = self.control.queued[prio].pop (0)
			if not self.control.queued[prio]:
				del self.control.queued[prio]
			#
			if w.prepare is not None:
				try:
					w.prepare (*w.args, **w.kwargs)
				except Exception as e:
					logger.exception ('%s: prepare fails: %s' % (w.description, e))
			def starter () -> bool:
				self.processtitle (w.description)
				rc = w.method (*w.args, **w.kwargs)
				self.processtitle ()
				return rc
			w.pid = self.control.subprocess.spawn (starter)
			self.control.running.append (w)
			logger.debug ('%s: launched' % w.description)
		return bool (self.control.running or self.control.queued)

	def launch (self,
		prio: int,
		description: str,
		method: Callable[..., bool],
		prepare: Optional[Callable[..., None]],
		finalize: Optional[Callable[..., None]],
		*args: Any,
		**kwargs: Any
	) -> None:
		active = self.pendings ()
		launching = ScheduleGenerate.Pending (
			description = description,
			method = method,
			prepare = prepare,
			finalize = finalize,
			args = args,
			kwargs = kwargs,
			pid = None
		)
		try:
			self.control.queued[prio].append (launching)
		except KeyError:
			self.control.queued[prio] = [launching]
		if not active:
			self.every ('pending', False, '1m', 0, self.pendings, ())

	def lockTitle (self) -> None:
		self.title (Stream.of (self.locks.items ())
			.map (lambda kv: '%s=%r' % kv)
			.join (', ', lambda s: ('active locks %s' % s) if s else s)
		)

	def islocked (self, key: int) -> bool:
		return key in self.locks
	
	def lock (self, key: int) -> None:
		try:
			self.locks[key] += 1
			logger.debug ('%r increased' % key)
		except KeyError:
			self.locks[key] = 1
			logger.debug ('%r set' % key)
	
	def unlock (self, key: int) -> None:
		with Ignore (KeyError):
			self.locks[key] -= 1
			if self.locks[key] <= 0:
				del self.locks[key]
				logger.debug ('%r removed' % key)
			else:
				logger.debug ('%r decreased' % key)
#}}}
class JobqueueGenerate (Jobqueue): #{{{
	__slots__: List[str] = ['reload', 'status']
	def __init__ (self, schedule: ScheduleGenerate) -> None:
		super ().__init__ (schedule)
		self.reload = schedule.reload
		self.status = schedule.status
		schedule.processtitle ('watchdog')

	def setup_handler (self, master: bool = False) -> None:
		super ().setup_handler (master)
		if not master:
			self.setsignal (signal.SIGHUP, self.reload)
			self.setsignal (signal.SIGUSR1, self.status)
#}}}
class Generate (Runtime):
	__slots__ = ['oldest', 'processes', 'modules']
	def supports (self, option: str) -> bool:
		return option != 'dryrun'

	def add_arguments (self, parser: argparse.ArgumentParser) -> None:
		unit = Unit ()
		parser.add_argument (
			'-O', '--oldest',
			action = 'store', type = unit, default = unit ('3d'),
			help = 'oldest entry to process'
		)
		parser.add_argument (
			'-P', '--processes', '--parallel',
			action = 'store', type = int, default = 4,
			help = 'specifiy the number of parallel generation processes'
		)
	
	def use_arguments (self, args: argparse.Namespace) -> None:
		self.oldest = args.oldest
		self.processes = args.processes
		self.modules = args.parameter
	
	def executor (self) -> bool:
		with Activator () as activator:
			modules = (Stream.of (globals ().values ())
				.filter (lambda module: type (module) is type and issubclass (module, Task) and hasattr (module, 'interval'))
				.filter (lambda module: bool (activator.check (['%s-%s' % (program, module.name)])))
				.map (lambda module: (module.name, module))
				.dict ()
			)
		logger.info ('Active modules: %s' % ', '.join (sorted (modules.keys ())))
		schedule = ScheduleGenerate (modules, self.oldest, self.processes)
		if self.modules:
			schedule.readConfiguration ()
			for name in self.modules:
				if name not in modules:
					print ('** %s not known' % name)
				else:
					logger.info ('Module found')
					module = modules[name] (schedule)
					rc = module ()
					schedule.show_status ()
					logger.info ('Module returns %r' % (rc, ))
					if schedule.control.queued or schedule.control.running:
						logger.info ('Execute backgound processes')
						try:
							while schedule.control.queued:
								schedule.show_status ()
								schedule.pendings ()
								if len (schedule.control.running) == self.processes:
									logger.info ('Currently %d processes running, wait for at least one to terminate' % len (schedule.control.running))
									schedule.show_status ()
									schedule.wait (True)
							logger.info ('Wait for %d background process to teminate' % len (schedule.control.running))
							while schedule.control.running:
								schedule.show_status ()
								if not schedule.wait (True):
									break
						except KeyboardInterrupt:
							logger.info ('^C, terminate all running processes')
							for p in schedule.control.running[:]:
								if p.pid is not None:
									schedule.control.subprocess.term (p.pid)
									schedule.wait ()
								else:
									schedule.control.running.remove (p)
							logger.info ('Waiting for 2 seconds to kill all remaining processes')
							time.sleep (2)
							for p in schedule.control.running[:]:
								if p.pid is not None:
									schedule.control.subprocess.term (p.pid, signal.SIGKILL)
								else:
									schedule.control.running.remove (p)
							logger.info ('Waiting for killed processes to terminate')
							while schedule.wait (True) is not None:
								pass
						logger.info ('Background processes done')
					if schedule.deferred:
						logger.info ('Deferred jobs active, process them')
						try:
							last = -1
							while schedule.defers ():
								cur = len (schedule.deferred)
								if cur != last:
									logger.info ('%d jobs remaining' % cur)
									last = cur
								time.sleep (1)
						except KeyboardInterrupt:
							logger.info ('^C, terminating')
		else:
			jq = JobqueueGenerate (schedule)
			jq.start (restart_delay = '1m', termination_delay = '5m')
		return True
#}}}
if __name__ == '__main__':
	Generate.main ()
