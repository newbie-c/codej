function copyThis(event) {
  $(this).blur();
  let clipboard = new ClipboardJS('#' + $(this)[0].id);
  clipboard.on('success', function(e) {
    $(event.data.cls).slideUp('slow');
  })
}
