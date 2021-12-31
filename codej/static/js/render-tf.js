function showDateTime(dto) {
  return dto.setLocale('ru')
            .toLocaleString(luxon.DateTime.DATE_FULL) + ', ' +
         dto.setLocale('ru')
            .toLocaleString(luxon.DateTime.TIME_WITH_SECONDS);
}

function renderTF(cls, dto) {
  $(cls).text(showDateTime(dto));
  setInterval(function() {
    let ndto = luxon.DateTime.now();
    $(cls).each(function() {
      $(this).text(showDateTime(ndto));
    });
  }, 1000);
}
