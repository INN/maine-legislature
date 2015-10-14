(function() {
  var $ = jQuery;

  $(document).ready(function() {
    /* Select house or senate tab */
    $('.house-selector li a').on('click', function() {
      var tab = $(this).attr('href');

      $(this)
        .parent()
        .parent()
        .find('a')
        .removeClass('active');

      $(this)
        .addClass('active');

      $(tab)
        .siblings('.tab')
        .removeClass('active');

      $(tab).addClass('active');

      $('img.lazy').lazyload();

      return false;
    });

    $('img.lazy').lazyload();
  });
})();
