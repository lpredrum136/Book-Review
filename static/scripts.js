$(document).ready(function(){
    // Show all popovers
    $('[data-toggle="popover"]').popover();

    // Some alert is not available by default, only show when user completed some action
    $('#NotAvailable:empty').hide();

    // Hide the review made by user by default

    // configure typeahead
    $("#query").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
                "<div>ISBN " +
                "{{ isbn }}" + ", <b>" + "{{ title }}" + "</b>, <b><i>" + "{{ author }}" + "</i></b>, " + "{{ year }}" +
                "</div>"
            )
        }
    });

    /* Click on a suggestion takes user to the book page */
    $("#query").on("typeahead:selected", function(eventObject, suggestion, name) {
        // Construct url to go
        var urlToGo = `/book/${suggestion.isbn}`;
        // Redirect to url above
        document.location.href = urlToGo;
    });

    /* Show toast when user submit a review */
    $('#message').click(function(){// When the button with id="message" is clicked
        $('.toast').toast('show'); // Show all toasts
    });

    /* Star rating https://codepen.io/anon/pen/ewjWmN */
    var $star_rating = $('.star-rating .fa');

    var SetRatingStar = function() {
        return $star_rating.each(function() {
            if (parseInt($star_rating.siblings('input.rating-value').val()) >= parseInt($(this).data('rating'))) {
            return $(this).removeClass('fa-star-o').addClass('fa-star');
            } else {
            return $(this).removeClass('fa-star').addClass('fa-star-o');
            }
        });
    };

    $star_rating.on('click', function() {
    $star_rating.siblings('input.rating-value').val($(this).data('rating'));
    // alert(`${$star_rating.siblings('input.rating-value').val()}`);
    return SetRatingStar();
    });

    SetRatingStar();

    /* If the user has not rate stars, disable the submit */
    $('#message').click(function() {
        if ($('.star-rating .rating-value').val() == 0) {
            alert('Please enter a rating');
            return false;
        }
    });

    /* Switch html between if the user has or has not reviewed */
    if ($('#NotAvailable').is(':empty')) {
        $('#alreadyReview').hide();
    } else {
        $('#textReview').hide();
    }

    /* Star rating shown for reviews already recorded */
    var star_rating_reviewed = $('.star-rating-reviewed .fa');
    star_rating_reviewed.each(function() {
        if (parseInt($(this).siblings('input.rating-value').val()) >= parseInt($(this).data('rating'))) {
            $(this).removeClass('fa-star-o').addClass('fa-star');
        } else {
            $(this).removeClass('fa-star').addClass('fa-star-o');
        }
    });
});

function search(query, syncResults, asyncResults)
{
    // get books matching query (asynchronously)
    var parameters = {
        q: query
    };
    $.getJSON(Flask.url_for("search"), parameters)
    .done(function(data, textStatus, jqXHR) {
     
        // call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());

        // call typeahead's callback with no results
        asyncResults([]);
    });
}

