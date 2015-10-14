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
        .hide();

      $(tab).show();

      return false;
    });

    /* On load, show the senate tab */
    $('[href="#senators-div"]').addClass('active');
    $('#senators-div').show();
  });
})();
