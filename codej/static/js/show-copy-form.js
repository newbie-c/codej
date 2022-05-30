function showCopyForm() {
  $(this).blur();
  let target = $(this).siblings('.entity-link-copy-form');
  if (target.is(':hidden')) {
    target.slideDown('slow');
  } else {
    target.slideUp('slow');
  }
}
