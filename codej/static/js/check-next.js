function checkNext() {
  let $next = $(this).next('.content-block');
  if ($next.length && !$next.hasClass('next-block')) {
    $next.addClass('next-block');
  }
}
