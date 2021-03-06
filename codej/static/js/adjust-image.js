function wrapImage($img) {
  if ($img.parent().prop('tagName') === 'P') {
    var $url = $img.attr('src');
    var html = '<a href="' + $url + '"' +
               '   target="_blank" rel="nofollow"></a>';
    $img.wrap(html);
  }
}

function adjust(image) {
  var width = image.width();
  var $parent = image.parents('p');
  var $width = parseInt($parent.outerWidth());
  if (width > $width) image.attr('width', $width);
}

function adjustImage() {
  adjust($(this));
  $(this).on('load', function() {
    adjust($(this));
  });
  $(this).parents('p').addClass('image-par');
}

function adjustImageW() {
  adjust($(this));
  $(this).on('load', function() {
    adjust($(this));
  });
  wrapImage($(this));
  $(this).parents('p').addClass('image-par');
}
