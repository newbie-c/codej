function likeArt() {
  $(this).blur();
  $.ajax({
    method: 'POST',
    url: $(this).data().url,
    data: {
      suffix: $('#entity-header-block').data().suffix
    },
    success: function(data) {
      if (!data.empty) {
        $('.like-block .value').text(data.likes);
        $('.dislike-block .value').text(data.dislikes);
        $('#like-button .value').text(data.likes);
        $('#dislike-button .value').text(data.dislikes);
      }
    },
    error: function(data) {},
    dataType: 'json'
  });
}
