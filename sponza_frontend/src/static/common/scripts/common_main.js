(function ($) {
  "use strict";

  // Scroll to Top Button Click Handler
  $(document).on("click", "a.scroll-to-top", function (e) {
    $("html, body").animate({ scrollTop: 0 }, 1000, "easeInOutExpo");
    e.preventDefault();
  });

  // Show or Hide Scroll to Top Button Based on Scroll Position
  $(document).on("scroll", function () {
    if ($(this).scrollTop() > 100) {
      $(".scroll-to-top").fadeIn();
    } else {
      $(".scroll-to-top").fadeOut();
    }
  });

  // Sidebar Toggle
  $(document).on("click", "#sidebarToggle, #sidebarToggleTop", function () {
    $("body").toggleClass("sidebar-toggled");
    $(".sidebar").toggleClass("toggled");

    // Collapse all sidebar items if sidebar is toggled
    if ($(".sidebar").hasClass("toggled")) {
      $(".sidebar .collapse").each(function () {
        var collapseInstance = bootstrap.Collapse.getInstance(this);
        if (collapseInstance) {
          collapseInstance.hide();
        }
      });
    }
  });

  // Window Resize Behavior
  $(window).resize(function () {
    if ($(window).width() < 768) {
      $(".sidebar .collapse").each(function () {
        var collapseInstance = bootstrap.Collapse.getInstance(this);
        if (collapseInstance) {
          collapseInstance.hide();
        }
      });
    }
    if ($(window).width() < 480 && !$(".sidebar").hasClass("toggled")) {
      $("body").addClass("sidebar-toggled");
      $(".sidebar").addClass("toggled");

      $(".sidebar .collapse").each(function () {
        var collapseInstance = bootstrap.Collapse.getInstance(this);
        if (collapseInstance) {
          collapseInstance.hide();
        }
      });
    }
  });
})(jQuery);
