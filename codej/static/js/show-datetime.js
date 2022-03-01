function formatDateTime(elem) {
  let $dt = $.trim(elem.text());
  let d = luxon.DateTime.fromISO($dt)
                        .setLocale('ru')
                        .toLocaleString(luxon.DateTime.DATE_FULL);
  let t = luxon.DateTime.fromISO($dt)
                        .setLocale('ru')
                        .toFormat('T');
  elem.text(d + ', ' + t);
}
