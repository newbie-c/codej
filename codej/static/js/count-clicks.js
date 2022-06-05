function countClicks(elem) {
  let $suffix = elem.data().suffix;
  let current = window.localStorage.getItem('viewed_');
  if (!current) {
    current = new Array();
  } else {
    current = current.split(',')
  }
  if (!current.includes($suffix)) {
    $.ajax({
      method: 'POST',
      url: elem.data().url,
      data: {
        suffix: $suffix,
      },
      success: function(data) {
        if (!data.empty) {
          $('.viewed-ind .value').text(data.views);
        }
      },
      error: function(data) {},
      dataType: 'json'
    });
    current.push($suffix);
    if (current.length > 200) current.shift();
    window.localStorage.setItem('viewed_', current.join());
  }
}
