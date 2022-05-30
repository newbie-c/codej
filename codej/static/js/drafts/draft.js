$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  formatFooter(now)
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() { formatDateTime($(this)); });
  scrollPanel($('.editor-forms-block'));
  $('#html-text-edit').focus();
  $('.slidable .block-header').on('click', showHideBlock);
  if ($('.entity-text-block').length) {
    let ch = $('.entity-text-block').children();
    let len = $('.entity-text-block').data().len;
    for (let i = 0, m = 0; i < ch.length && m < len; i++) {
      n = ch[i].nodeName;
      if (n === 'UL' || n === 'OL' || n === 'BLOCKQUOTE') {
        let lch = $(ch[i]).children();
        let l = lch.length;
        let j = 0;
        while (j < lch.length) {
          $(lch[j]).attr({'data-num': m, class: 'editable'});
          j++;
          m++;
        }
      } else {
        $(ch[i]).attr({'data-num': m, class: 'editable'});
        m++;
      }
    }
    $('.entity-text-block iframe').each(adjustFrame);
    $('.entity-text-block').children().each(setMargin);
    $('.entity-text-block img').each(adjustImage);
    $('#main-container').on('click', '.edit-par', function() {
      $(this).blur();
      let par = $(this).parent().next();
      let url = $('.entity-text-block').data().check;
      $.ajax({
        method: 'POST',
        url: url,
        data: {
          num: $(this).data().num,
          art: $(this).data().art
        },
        success: function(data) {
          if (!data.empty) {
            $('#sp-case').trigger('click');
            par.after(data.html).slideUp('slow');
            $('#paragraph-editor').hide()
              .removeClass('hidden').slideDown('slow').css({'margin': 0});
            $('.editor-forms-block').slideUp('slow');
            $('#options-block').slideUp('slow');
          }
        },
        error: function(data) {},
        dataType: 'json'
      });
    });
    $('#main-container').on('click', '.add-before', function() {
      $(this).blur();
      let par = $(this).parent();
      let html = '<div id="paragraph-editor" class="form-form hidden">' +
                 '  <div class="form-group">' +
                 '    <textarea id="paragraph-text-edit"' +
                 '              placeholder="oтредактируйте абзац топика"' +
                 '              data-url="' +
                 $('.entity-text-block').data().insert + '"' +
                 '              data-num="' + $(this).data().num + '"' +
                 '              data-art="' + $(this).data().art + '"' +
                 '              class="form-control"' +
                 '              rows="5"></textarea>' +
                 '  </div>' +
                 '  <div class="form-group last-group">' +
                 '    <button id="cancel-edit"' +
                 '            type="button"' +
                 '            title="отменить"' +
                 '            class="btn btn-info btn-sm">' +
                 '      <span class="glyphicon glyphicon-refresh"' +
                 '            aria-hidden="true"></span>' +
                 '    </button>' +
                 '  </div>' +
                 '</div>';
      par.before(html);
      $('#sp-case').trigger('click');
      $('#paragraph-editor').hide()
        .removeClass('hidden').slideDown('slow').css({'margin': 0});
      $('#paragraph-text-edit').focus();
    });
    $('#main-container').on('click', '#cancel-edit', function() {
      $(this).blur();
      let pare = $('#paragraph-editor');
      let par = pare.prev();
      par.slideDown('slow');
      pare.slideUp('slow', function() {
        $(this).remove();
      });
      par.slideDown('slow');
      $('.editor-forms-block').slideDown('slow');
      $('#options-block').slideDown('slow');
    });
    $('#main-container').on('click', '.remove-par', function() {
      $(this).blur();
      let par = $(this).parent().next();
      let url = $('.entity-text-block').data().rem;
      let html = '<div id="p-block" class="text-center hidden">' +
                 '  <img alt="progress show"' +
                 '       src="/static/images/upload.gif">' +
                 '</div>';
      par.after(html);
      $('#p-block').hide().removeClass('hidden').slideDown('slow');
      par.slideUp('slow');
      $('#sp-case').trigger('click');
      $.ajax({
        method: 'POST',
        url: url,
        data: {
          num: $(this).data().num,
          art: $(this).data().art
        },
        success: function(data) {
          if (!data.empty) window.location.reload();
        },
        error: function(data) {},
        dataType: 'json'
      });
    });
    $('.entity-text-block').on('mouseleave', function() {
      if (!$('#paragraph-editor').length) {
        $('#editor-opts').remove();
      }
    });
    $('.editable').on('mouseenter', function() {
      if (!$('#paragraph-editor').length && !$('#p-block').length) {
        $('#editor-opts').remove();
        let $this = $(this);
        let html = '<div id="editor-opts">' +
                   '  <button type="button"' +
                   '          class="btn btn-primary btn-xs edit-par"' +
                   '          title="редактировать"' +
                   '          data-art="' +
                   $('.entity-text-block').data().art + '"' +
                   '          data-num="' + $this.data().num + '">' +
                   '    <span class="glyphicon glyphicon-edit"' +
                   '          aria-hidden="true"></span>' +
                   '  </button>' +
                   '  <button type="button"' +
                   '          class="btn btn-primary btn-xs add-before"' +
                   '          title="добавить абзац выше"' +
                   '          data-url=""' +
                   '          data-art="' +
                   $('.entity-text-block').data().art + '"' +
                   '          data-num="' + $this.data().num + '">' +
                   '    <span class="glyphicon glyphicon-upload"' +
                   '          aria-hidden="true"></span>' +
                   '  </button>' +
                   '  <button type="button"' +
                   '          class="btn btn-danger btn-xs remove-par"' +
                   '          title="удалить абзац"' +
                   '          data-url=""' +
                   '          data-art="' +
                   $('.entity-text-block').data().art + '"' +
                   '          data-num="' + $this.data().num + '">' +
                   '    <span class="glyphicon glyphicon-trash"' +
                   '          aria-hidden="true"></span>' +
                   '  </button>' +
                   '</div>';
        if ($this[0].nodeName === 'LI') {
          if ($this.find('p').length) {
            $this.find('p').before(html);
          } else {
            $this.before(html);
          }
        } else {
          $this.before(html);
        }
      }
    });
    $('#main-container').on('keyup', '#paragraph-text-edit', function(event) {
      if (event.which == 13) {
        let val = $(this).val().trim();
        let url = $(this).data().url;
        let art = $(this).data().art;
        let num = $(this).data().num;
        const F = '```';
        if (val.startsWith(F)) {
          if (val.indexOf(F, 1) >= 4) {
            val = F + val.split(F)[1].trim() + '\n\n' + F;
            sendEdited(url, art, num, val, 1);
          }
        } else if (val) {
          sendEdited(url, art, num, val.replace('\n', ''), 0);
        }
      }
    });
  }
  $('#html-text-edit').on('keyup', function(event) {
    if (event.which == 13) {
      let val = $(this).val().trim();
      let url = $(this).data().url;
      let art = $('#entity-header-block').data().id;
      const F = '```';
      if (val.startsWith(F)) {
        if (val.indexOf(F, 1) >= 4) {
          val = F + val.split(F)[1].trim() + '\n\n' + F;
          sendPar(url, art, val, 1);
        }
      } else if (val) {
        sendPar(url, art, val.replace('\n', ''), 0);
      }
    }
  });
  $('#sp-case').on('click', function() {
    let o = $('#editor-opts');
    if (o.length) o.slideUp('slow');
  });
  $('.copy-link').on('click', showCopyForm);
  $('#copy-button').on('click', {cls: '.entity-link-copy-form'}, copyThis);
  $('#labels-button').on('click', function() {
    $(this).blur();
  });
  $('#edit-metadesc').on('click', function() {
    $(this).blur();
  });
  $('#edit-title').on('click', function() {
    $(this).blur();
  });
  $('#edit-summary').on('click', function() {
    $(this).blur();
  });
  let stbtn = $('#state-button');
  if (stbtn.length) stbtn.on('click', function() {
    $(this).blur();
  });
});
