function adjustFrame() {
  if ($(this).hasClass('editable')) {
    let html = '<div class="embedded-container editable"' +
               '     data-num="' + $(this).data().num +'"></div>';
    $(this).wrap(html);
    $(this).removeClass('editable').addClass('video');
  } else {
    let html = '<div class="embedded-container"></div>';
    $(this).wrap(html);
    $(this).addClass('video');
  }
}
