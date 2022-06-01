function trackMarker(event) {
  let $value = $(this).val();
  let $marker = $(event.data.marker);
  let $mblock = $(event.data.block);
  let $block = $(this).parents('.form-group');
  $marker.text(event.data.len - $value.length);
  if ($value.length > event.data.len) {
    $block.addClass('has-error');
    $mblock.addClass('error');
  } else {
    if ($block.hasClass('has-error')) $block.removeClass('has-error');
    if ($mblock.hasClass('error')) $mblock.removeClass('error');
  }
}
