function ping() {
  $.ajax({
    method: 'POST',
    url: '/ajax/ping',
    data: {
      empty: true
    },
    success: function(data) {},
    error: function(data) {},
    dataType: 'json'
  });
}

function pingU() {
  setTimeout(ping, 300000);
  setInterval(ping, 3540000);
}
