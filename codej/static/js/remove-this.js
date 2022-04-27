function removeThis() {
  let $this = $(this);
  $this.blur();
  $.ajax({
    method: 'POST',
    url: $this.data().url,
    data: {
      suffix: $this.data().suffix,
      page: $this.data().page,
      last: $this.data().last
    },
    success: function(data) {
      if (!data.empty) {
        window.location.replace(data.url);
      } else {
        $this.fadeOut('slow');
      }
    },
    error: function(data) {
      $this.fadeOut('slow');
    },
    dataType: 'json'
  });
}
