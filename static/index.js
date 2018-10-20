var socket = io();
var blocked_echo = false;
var blocked_search = false;

$("#echo_message").keypress(function (e) {
    if (e.which == 13 & !blocked_echo) {
        blocked_echo = true;
        var msg = $('#echo_message').val();
        $("#echo_message").val("");

        $("#container_bubble").append('<div class="row">\n' +
            '        <div class="col-md-5 message-bubble-user"><p>' + msg + '</p></div>\n' +
            '        <div class="col-md-7"></div>\n' +
            '    </div>');
        socket.emit('echo', msg);
    }
});

$("#btn_download").on('click', function () {
    if (!blocked_search)
        blocked_search = true;
    socket.emit('search');
});

socket.on('search', function (url) {
    //download(data.file_name, data.content);
    if (!url) {
        $('.alert').show()
    } else {
        document.getElementById('download').src = url;
    }

    blocked_search = false
});

socket.on('echo', function (data) {
    $("#container_bubble").append('<div class="row">\n' +
        '        <div class="col-md-7"></div>\n' +
        '        <div class="col-md-5 message-bubble-server"><p>' + data + '</p></div>\n' +
        '    </div>');
    blocked_echo = false;
});