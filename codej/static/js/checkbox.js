function checkBox(id) {
  let box = $(id);
  if (box.length && !box.is(':checked')) box.prop('checked', true);
}

function uncheckBox(id) {
  let box = $(id);
  if (box.length && box.is(':checked')) box.prop('checked', false);
}
