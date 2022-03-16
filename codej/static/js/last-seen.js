function renderLastSeen() {
  let text = $.trim($(this).text());
  $(this).text(luxon.DateTime.fromISO(text)
                             .setLocale('ru').toRelative());
}
