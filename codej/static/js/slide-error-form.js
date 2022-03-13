function slideError(cls) {
  let $form = $(cls);
  if ($form.find('.error').length) {
    setTimeout(function() {
      $form.slideDown('slow');
    }, 600);
  }
}
