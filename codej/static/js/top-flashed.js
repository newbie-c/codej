function closeTopFlashed() {
  let $flashed = $(this).parents('.flashed-message');
  let $next = $flashed.next('.flashed-message');
  let $cond = $next.length + $flashed.prev('.flashed-message').length;
  let $top = $flashed.parents('.top-flashed-block');
  if (!$flashed.hasClass('next-block')) {
    $flashed.remove();
    $next.removeClass('next-block');
  } else {
    $flashed.remove();
  }
  if (!$cond) {
    $top.remove();
  }
}
