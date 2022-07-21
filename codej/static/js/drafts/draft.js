$(function() {
  checkMC(800);
  hideHidden();
  let now = luxon.DateTime.now();
  formatFooter(now);
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
          $(lch[j]).attr({'data-num': m});
          $(lch[j]).addClass('editable');
          j++;
          m++;
        }
      } else {
        $(ch[i]).attr({'data-num': m});
        $(ch[i]).addClass('editable');
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
  $('#move-screen-up').on('click', function() {
    $(this).blur();
    scrollPanel($('#navigation'));
  });
  $('#labels-button').on('click', function() {
    $(this).blur();
    let f = $('#labels-editor');
    if (f.is(':hidden')) {
      f.slideDown('slow', function() {
        $('#labels-edit').focus();
        scrollPanel(f);
      });
      $('#new-paragraph-editor').slideUp('slow');
      $('#entity-title-editor').slideUp('slow');
      $('#summary-editor').slideUp('slow');
      $('#status-editor').slideUp('slow');
      $('#meta-description-editor').slideUp('slow');
    } else {
      f.slideUp('slow');
      $('#new-paragraph-editor').slideDown('slow', function() {
        $('#html-text-edit').focus();
      });
    }
  });
  $('#labels-edit').on('keyup blur', function() {
    let g = $(this).parents('.form-group');
    g.removeClass('has-error');
    let c = $(this).val().split(',');
    for (each in c) {
      each = $.trim(c[each]);
      if (each) {
        let re = /^[A-Za-zА-Яа-яЁё\d\-]{1,32}$/;
        if (!re.exec(each)) {
          g.addClass('has-error');
        }
      }
    }
  });
  $('#labels-submit').on('click', function() {
    $(this).blur();
    let e = $('#labels-edit').parents('.form-group');
    if (!e.hasClass('has-error')) {
      $.ajax({
        method: 'POST',
        url: $(this).data().url,
        data: {
          labels: $('#labels-edit').val(),
          aid: $('#entity-header-block').data().id
        },
        success: function(data) {
          if (!data.empty) {
            if (data.error) {
              e.addClass('has-error');
            } else {
              window.location.reload();
            }
          }
        },
        error: function(data) {},
        dataType: 'json'
      });
    }
  });
  $('#edit-metadesc').on('click', function() {
    $(this).blur();
    let f = $('#meta-description-editor');
    if (f.is(':hidden')) {
      f.slideDown('slow', function() {
        $('#metadesc-edit').focus();
        scrollPanel(f);
      });
      $('#new-paragraph-editor').slideUp('slow');
      $('#entity-title-editor').slideUp('slow');
      $('#summary-editor').slideUp('slow');
      $('#status-editor').slideUp('slow');
      $('#labels-editor').slideUp('slow');
    } else {
      f.slideUp('slow');
      $('#new-paragraph-editor').slideDown('slow', function() {
        $('#html-text-edit').focus();
      });
    }
  });
  $('#metadesc-edit')
    .on('keyup blur',
        {len: 180, marker: '#d-length-value', block: '#d-length-marker'},
        trackMarker);
  $('#metadesc-submit').on('click', function() {
    $(this).blur();
    if (!$('#metadesc-edit').parents('.form-group').hasClass('has-error')) {
      $.ajax({
        method: 'POST',
        url: $(this).data().url,
        data: {
          meta: $('#metadesc-edit').val(),
          art: $(this).data().art
        },
        success: function(data) {
          if (!data.empty) {
            window.location.reload();
          } else {
            $('#edit-metadesc').trigger('click');
          }
        },
        error: function(data) {},
        dataType: 'json'
      });
    }
  });
  $('#edit-title').on('click', function() {
    $(this).blur();
    let f = $('#entity-title-editor');
    if (f.is(':hidden')) {
      f.slideDown('slow', function() {
        $('#title').focus();
        scrollPanel(f);
      });
      $('#new-paragraph-editor').slideUp('slow');
      $('#meta-description-editor').slideUp('slow');
      $('#summary-editor').slideUp('slow');
      $('#status-editor').slideUp('slow');
      $('#labels-editor').slideUp('slow');
    } else {
      f.slideUp('slow');
      $('#new-paragraph-editor').slideDown('slow', function() {
        $('#html-text-edit').focus();
      });
    }
  });
  $('#title')
    .on('keyup blur',
        {min: 3, max: 100, block: '.input-field'}, markInputError);
  $('#title').on('keyup', function(event) {
    if (event.which == 13) $('#title-submit').trigger('click');
  });
  $('#title-submit').on('click', function() {
    $(this).blur();
    if (!$('.input-field').hasClass('has-error')) {
      $.ajax({
        method: 'POST',
        url: $(this).data().url,
        data: {
          title: $('#title').val().trim(),
          art: $(this).data().art
        },
        success: function(data) {
          if (!data.empty) {
            window.location.replace(data.url);
          } else {
            $('#edit-title').trigger('click');
          }
        },
        error: function(data) {},
        dataType: 'json'
      });
    }
  });
  $('#edit-summary').on('click', function() {
    $(this).blur();
    let f = $('#summary-editor');
    if (f.is(':hidden')) {
      f.slideDown('slow', function() {
        $('#summary-edit').focus();
        scrollPanel(f);
      });
      $('#new-paragraph-editor').slideUp('slow');
      $('#meta-description-editor').slideUp('slow');
      $('#entity-title-editor').slideUp('slow');
      $('#status-editor').slideUp('slow');
      $('#labels-editor').slideUp('slow');
    } else {
      f.slideUp('slow');
      $('#new-paragraph-editor').slideDown('slow', function() {
        $('#html-text-edit').focus();
      });
    }
  });
  $('#summary-submit').on('click', function() {
    $(this).blur();
    let s = $('#summary-edit').val();
    if (s.length) {
      $.ajax({
        method: 'POST',
        url: $(this).data().url,
        data: {
          art: $(this).data().art,
          summary: s
        },
        success: function(data) {
          if (!data.empty) {
            window.location.reload();
          } else {
            $('#edit-summary').trigger('click');
          }
        },
        error: function(data) {},
        dataType: 'json'
      });
    }
  });
  $('#summary-edit')
    .on('keyup blur',
        {len: 512, marker: '#s-length-value', block: '#s-length-marker'},
        trackMarker);
  let sft = $('#summary-from-text');
  if (sft.length) {
    sft.on('click', function() {
      $(this).blur();
      let l = $('.entity-text-block').children('p');
      let w = '';
      for (let n = 0; n < l.length && w.length < 512; n++) {
        w = w + ' ' + $(l[n]).text();
      }
      let t = w.trim().split(' ');
      let res = '';
      let i = 0;
      while ((res + '...').length <= 384 && i < t.length) {
        res = res + ' ' + t[i];
        i++;
      }
      $('#summary-edit').val(res.trim() + '...');
    });
  }
  let stbtn = $('#state-button');
  if (stbtn.length) {
    stbtn.on('click', function() {
      $(this).blur();
      let f = $('#status-editor');
      if (f.is(':hidden')) {
        f.slideDown('slow');
        $('#new-paragraph-editor').slideUp('slow');
        $('#meta-description-editor').slideUp('slow');
        $('#entity-title-editor').slideUp('slow');
        $('#summary-editor').slideUp('slow');
        $('#labels-editor').slideUp('slow');
      } else {
        f.slideUp('slow');
        $('#new-paragraph-editor').slideDown('slow', function() {
          $('#html-text-edit').focus();
        });
      }
    });
    $('#select-status').on('change', function() {
      $.ajax({
        method: 'POST',
        url: $(this).data().url,
        data: {
          art: $(this).data().art,
          state: $(this).val()
        },
        success: function(data) {
          if (!data.empty) window.location.reload();
        },
        error: function(data) {},
        dataType: 'json'
      });
    });
  }
  $('#comments-state').on('click', function() {
    $(this).blur();
    $.ajax({
      method: 'POST',
      url: $(this).data().url,
      data: {
        id: $('#entity-header-block').data().id
      },
      success: function(data) {
        if (!data.empty) window.location.reload();
      },
      error: function(data) {},
      dataType: 'json'
    });
  });
});
