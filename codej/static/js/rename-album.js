function renameAlbum() {
  $(this).blur();
  if (!$('#rename-form').hasClass('has-error')) {
    $.ajax({
      method: 'POST',
      url: $(this).data().url,
      data: {
        album: $(this).data().aid,
        title: $('#title-change').val()
      },
      success: function(data) {
        if (data.empty) {
          $('#rename-form').slideUp('slow');
        } else {
          window.location.reload();
        }
      },
      error: function(data) {
        $('#rename-form').slideUp('slow');
      },
      dataType: 'json'
    });
  }
}
