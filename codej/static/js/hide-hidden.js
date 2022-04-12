function hideHidden() {
  $('.to-be-hidden').each(function() {
    let $this = $(this);
    if (!$this.is(':hidden')) $this.hide();
  });
}
