$('.multi-menu .title').click(function () {
    // $(this).next().toggleClass('hidden')

    $(this).next().removeClass('hidden');

    $(this).parent().siblings().find('.body').addClass('hidden')

})
