function setMargin() {
  if (!$(this).prev().length) $(this).css({'margin-top': 0});
  if (!$(this).next().length) $(this).css({'margin-bottom': 0});
}
