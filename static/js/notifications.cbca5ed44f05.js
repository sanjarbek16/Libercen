$(function () {
  $('#notifications').popover({html: true, content: 'Loading...', trigger: 'manual'});

  $("#notifications").click(function () {
    if ($(".popover").is(":visible")) {
      $("#notifications").popover('hide');
    }
    else {
      $("#notifications").popover('show');
      $(".popover-body").html("<div style='text-align:center'><img src='/static/icons/loading.gif'></div>");
      $.ajax({
        url: '/notifications/last/',
        beforeSend: function () {
          $("#notifications").removeClass("new-notifications");
        },
        success: function (data) {
          $(".popover-body").html(data);
          $("#notifications .fa").removeClass("fa-bell");
          $("#notifications .fa").addClass("fa-bell-o");
        }
      });
    }
    return false;
  });


  function check_notifications() {
    $.ajax({
      url: '/notifications/check/',
      cache: false,
      success: function (data) {
        if (data != "0") {
          $("#notifications .fa").addClass("fa-bell");
          $("#notifications .fa").removeClass("fa-bell-o");
        }
        else {
          $("#notifications .fa").removeClass("fa-bell");
          $("#notifications .fa").addClass("fa-bell-o");
        }
      },
      complete: function () {
        window.setTimeout(check_notifications, 30000);
      }
    });
  };
  check_notifications();
});
$(function () {
  $('#userMenu').popover({html: true, content: 'Loading...', trigger: 'manual'});

  $("#userMenu").click(function () {
    if ($(".popover").is(":visible")) {
      $("#userMenu").popover('hide');
    }
    else {
      $("#userMenu").popover('show');
      $(".popover-body").html("<div style='text-align:center'><img src='/static/icons/loading.gif'></div>");
      $.ajax({
        url: '/user/menu/',
        success: function (data) {
          $(".popover-body").html(data);
        }
      });
    }
    return false;
    })
  });