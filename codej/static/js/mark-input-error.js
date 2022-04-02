function markInputError(event) {
  let $value = $(this).val();
  let $block = $(this).parents(event.data.block);
  if ($value.length < event.data.min || $value.length > event.data.max) {
    $block.addClass('has-error');
  } else {
    if ($block.hasClass('has-error')) $block.removeClass('has-error');
  }
}
