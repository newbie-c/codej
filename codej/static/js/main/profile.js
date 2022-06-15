$(function() {
  checkMC(800);
  formatFooter(luxon.DateTime.now());
  $('.close-top-flashed').on('click', closeTopFlashed);
  $('.date-field').each(function() {formatDateTime($(this));});
  $('.last-seen').each(renderLastSeen);
  $('.slidable .block-header').on('click', showHideBlock);
  if ($('#permissions-block').length) {
    $('#submit').on('click', function() { $(this).blur(); });
    let $blocker = $('#cannot-log-in');
    if ($blocker.length) {
      $blocker.on('change', function() {
        if ($(this).is(':checked')) {
          uncheckBox('#read-journal');
          uncheckBox('#follow-users');
          uncheckBox('#like-dislike');
          uncheckBox('#send-pm');
          uncheckBox('#write-commentary');
          uncheckBox('#create-link-alias');
          uncheckBox('#create-entity');
          uncheckBox('#block-entity');
          uncheckBox('#change-user-role');
          uncheckBox('#upload-pictures');
          uncheckBox('#make-announcement');
          uncheckBox('#special-case');
          uncheckBox('#administer-service');
        } else {
          checkBox('#read-journal');
        }
      });
    }
    let $reader = $('#read-journal');
    if ($reader.length) {
      $reader.on('change', function() {
        if ($(this).is(':checked')) {
          uncheckBox('#cannot-log-in');
        } else {
          checkBox('#cannot-log-in');
          uncheckBox('#follow-users');
          uncheckBox('#like-dislike');
          uncheckBox('#send-pm');
          uncheckBox('#write-commentary');
          uncheckBox('#create-link-alias');
          uncheckBox('#create-entity');
          uncheckBox('#block-entity');
          uncheckBox('#change-user-role');
          uncheckBox('#upload-pictures');
          uncheckBox('#make-announcement');
          uncheckBox('#special-case');
          uncheckBox('#administer-service');
        }
      });
    }
    let $admin = $('#administer-service');
    if ($admin.length) {
      $admin.on('change', function() {
        if ($(this).is(':checked')) {
          uncheckBox('#cannot-log-in');
          checkBox('#read-journal');
          checkBox('#follow-users');
          checkBox('#like-dislike');
          checkBox('#send-pm');
          checkBox('#write-commentary');
          checkBox('#create-link-alias');
          checkBox('#create-entity');
          checkBox('#block-entity');
          checkBox('#change-user-role');
          checkBox('#upload-pictures');
          checkBox('#make-announcement');
          checkBox('#special-case');
        }
      });
    }
    checkAverage('#follow-users');
    checkAverage('#like-dislike');
    checkAverage('#send-pm');
    checkAverage('#write-commentary');
    checkAverage('#create-link-alias');
    checkAverage('#create-entity');
    checkAverage('#block-entity');
    checkAverage('#change-user-role');
    checkAverage('#upload-pictures');
    checkAverage('#make-announcement');
    checkAverage('#special-case');
  }
  let $desc = $('#fix-description');
  if ($desc.length) {
    $desc.on('click', function() {
      $(this).blur();
      $(this).parents('.description-block').slideUp('slow');
      let $editor = $('#description-e');
      $editor.slideDown('slow', function() { scrollPanel($editor); });
      $('#description-editor').focus();
    });
  }
  let $cancel = $('#cancel-description');
  if ($cancel.length) {
    $cancel.on('click', function() {
      $(this).blur();
      $(this).parents('#description-e').slideUp('slow');
      let $description = $('.description-block');
      $description.slideDown(
        'slow', function() { scrollPanel($description); });
    });
  }
  let $d_ed = $('#description-editor');
  if ($d_ed.length) {
    $d_ed.on(
      'keyup',
      {len: 500, marker: '#length-marker', block: '.length-marker'},
      trackMarker);
    $d_ed.on('blur', function() {
      let v = $(this).val();
      let g = $(this).parents('.form-group');
      if (v.length === 0) g.addClass('has-error');
    });
  }
  let $d_submit = $('#description-submit');
  if ($d_submit.length) {
    $d_submit.on('click', function(event) {
      $(this).blur();
      event.preventDefault();
      $('#description-editor').trigger('blur');
      if (!$(this).parents('.form-group')
                  .siblings('.form-group').hasClass('has-error')) {
        $.ajax({
          method: 'POST',
          url: $(this).data().url,
          data: {
            uid: $(this).data().id,
            desc: $('#description-editor').val()
          },
          success: function(data) {
            if (!data.empty) window.location.reload();
          },
          error: function(data) {},
          dataType: 'json'
        });
      }
    });
  }
  let $fr = $('#make-friend');
  if ($fr.length) {
    $fr.on('click', function() {
      $(this).blur();
      $.ajax({
        method: 'POST',
        url: $(this).data().url,
        data: {
          friend: $(this).data().friend
        },
        success: function(data) {
          if (!data.empty) window.location.reload();
        },
        error: function(data) {
          $('.action-block').slideUp('slow');
        },
        dataType: 'json'
      });
    });
  }
});
