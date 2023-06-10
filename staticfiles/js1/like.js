$(document).on('click', '.like-button', function(e) {
    e.preventDefault();
    var postid = $(this).val();
    var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    console.log('test')
    $.ajax({
        type: 'POST',
        url: '{% url "app:like" %}',
        data: {
            postid: postid,
            csrfmiddlewaretoken: csrftoken,
            action: 'post'
        },
        success: function(json) {
            $('#like-count-' + postid).text(json.result);
        },
        error: function(xhr, errmsg, err) {
            // handle error
        }
    });
});