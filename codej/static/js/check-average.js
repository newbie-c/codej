function checkAverage(id) {
  let average = $(id);
  if (average.length) {
    average.on('change', function() {
      if ($(this).is(':checked')) {
        checkBox('#read-journal');
        uncheckBox('#cannot-log-in');
      } else {
        uncheckBox('#administer-service');
      }
    });
  }
}
