AGN.Lib.Controller.new('recipient-statistics-view', function() {
  const Form = AGN.Lib.Form;

  this.addAction({change: 'type-change'}, function() {
    const $el = this.el;
    const selectedOption = $el.find('option:selected');
    const $mailinglist = $('#mailinglist-select');

    if (selectedOption.is('[data-mailinglist-required]') && $mailinglist.val() === '0') {
      AGN.Lib.Select.get($mailinglist).selectNext();
    }
    Form.get($el).submit();
  });

  this.addAction({change: 'change-period'}, function() {
    Form.get(this.el).submit();
  });
});
