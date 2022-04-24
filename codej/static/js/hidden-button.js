function showHideButton($this, cls) {
  let $target = $this.siblings(cls);
  if ($target.is(':hidden')) {
    $(cls).each(function() { $(this).fadeOut('slow'); });
    $target.fadeIn('slow');
  } else {
    $target.fadeOut('slow');
  }
}
