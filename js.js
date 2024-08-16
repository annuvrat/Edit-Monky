$(document).ready(function () {
    // Smooth scrolling for internal links
    $('a[href^="#"]').on('click', function (event) {
        var target = $($(this).attr('href'));

        if (target.length) {
            event.preventDefault();
            $('html, body').animate({
                scrollTop: target.offset().top
            }, 1000);
        }
    });

    // Show/hide scroll-to-top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('#scrollToTop').fadeIn();
        } else {
            $('#scrollToTop').fadeOut();
        }
    });

    // Scroll to top when scroll-to-top button is clicked
    $('#scrollToTop').click(function () {
        $('html, body').animate({ scrollTop: 0 }, 1000);
        return false;
    });
});
