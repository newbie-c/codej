function formatFooter(dto) {
  let $footer = $.trim($('#footer-link').text());
  let html = '<span class="footer-link-text">' +
             $footer + ', ' + dto.year + ' г.</span>';
  $('#footer-link').html(html);
}
