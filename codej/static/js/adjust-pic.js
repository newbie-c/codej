function adjustPicture() {
  let $itself = $(this).parents('.picture-itself');
  let $this = $(this);
  let $itself_width = parseInt($itself.outerWidth());
  let $parent_width = parseInt(
    $itself.parents('.picture-block').outerWidth());
  let $sibling_width = parseInt(
    $itself.siblings('.options-button-block').outerWidth());
  if ($itself_width + $sibling_width < $parent_width) {
    let $pic_width = parseInt($this.attr('width'));
    if ($pic_width >= $itself_width) {
      let $pic_height = parseInt($this.attr('height'));
      let width = $itself_width - 4;
      let height = Math.round($pic_height / ($pic_width / width));
      $this.attr({"width": width, "height": height});
    }
  }
}
