(function() {
  var $ = jQuery,
      legislatorBucketHTML = $('#legislators-bucket').html();

  $(document).ready(function() {

    var bindHouseSelectors = function() {
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
    };

    bindHouseSelectors();
    $('img.lazy').lazyload();

    /* Search */
    var setupTypehead = function(data) {
      var searchFields = _.keys(data[0]);

      $('.typeahead').typeahead({
        minLength: 3,
        highlight: true
      }, {
        name: 'legislators',
        source: function(query, syncResults) {
          var results = {};

          query = query.toLowerCase();

          _.each(data, function(datum) {
            _.each(searchFields, function(val, idx) {
              if ( datum[val].toLowerCase().indexOf( query ) >= 0 ) {
                if ( ! results[datum.id] )
                  results[datum.id] = datum;
              }
            });
          });

          filterLegislators(_.values(results));
        }
      });
    };

    var filterLegislators = _.debounce(function(legislators) {
      $('#legislators-bucket').html(JST.legislators({ legislators: legislators }));
      $('img.lazy').lazyload();
    }, 250);

    var fetchTypeaheadData = function() {
      $.ajax({
        url: APP_CONFIG.S3_BASE_URL + '/legislators.json',
        dataType: 'json',
        method: 'get',
        success: setupTypehead
      });
    };

    var resetSearch = function() {
      $('#legislators-bucket').html(legislatorBucketHTML);
      bindHouseSelectors();
      $('img.lazy').lazyload();
      return false;
    };

    $('.reset-search').click(resetSearch);

    fetchTypeaheadData();
  });
})();
