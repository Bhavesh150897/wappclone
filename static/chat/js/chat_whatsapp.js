let currentRecipient = '';
let chatInput = $('#input');
let messageList = $('#messages');

let userList = []; // latest_message,username


// this will be used to store the date of the last message
// in the message area
let lastDate = "";

function capitalizeFirstLetter(string){
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function fetchUserList() {
    $.getJSON('/api/v1/users/', function (data) {
        userList = data;
        drawUserList();
    });
}

function drawUserList() {
    $('.user-side').empty();
    // sort users based on latest message timestamp
    userList.sort((a,b)=>new Date(b.timestamp) - new Date(a.timestamp));
    for (let i = 0; i < userList.length; i++) {
        const msg = userList[i]['latest_message'];
        const username = capitalizeFirstLetter(userList[i]['username']);
        const profile_img = userList[i]['profile'];
        const last_online_time = userList[i]['last_online_time'];
        console.log(userList[i]);
         const online = userList[i]['online'];
         status = '';
         if (online == 1) {
             status = 'online';
         }else{
             status = 'offline';
         }
        const userItem = `
            <li class="contact image-user ${currentRecipient === userList[i]['username'] ? " active" : ""}" onclick="onClickUserList(this, '${userList[i]['username']}', '${userList[i]['online']}', '${userList[i]['last_online_time']}')">
                    <div class="wrap">
                        <span class="contact-status ${status}"></span>
                        <img src="${profile_img}" height="40" alt=""/>
                        <div class="meta">
                            <p class="name">${username}</p>
                            <p class="preview">${msg ? msg.substr(0, 50) : ""}</p>
                        </div>
                    </div>
                </li>`;
        $(userItem).appendTo('.user-side');
    }
}


function getTime(dateString){
  if (!dateString) return ''
  let date = new Date(dateString);
  let dualize = (x) => x < 10 ? "0" + x : x;
  return dualize(date.getHours()) + ":" + dualize(date.getMinutes());
}

function showDateUserlist(dateString) {
    let weekdaydate = showDatesWeekDays(dateString);
    if (weekdaydate === 'TODAY') 
        return getTime(dateString)
    return weekdaydate
}

function showDatesWeekDays(dateString) {
    if (!dateString) return ''
    const dt = new Date(dateString)        
    let days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']; 

    let date_weekday = dt.toLocaleDateString();
    if (dt.toDateString() == new Date().toDateString()) {
        date_weekday = 'TODAY';
    } else if(dt > new Date(Date.now() - 604800000)) {
        // if date is greater than last 7 days date
        date_weekday = days[dt.getDay()].toUpperCase()
    }
    return date_weekday;
}

function sendImageRec(obj,currUser,img) {
    if (obj === currUser) {
        return '';
    }else{
        return '<a href="'+img+'" download="'+img+'"><i class="fa fa-arrow-down download-btn" aria-hidden="true"></i></a>'
    }
}

function GetFilename(url)
{
   return new URL(url).pathname.split('/').pop();
}

function sentImageHide(obj,currUser,img,time) {
    var extension = img.substr( (img.lastIndexOf('.') +1) );
    if (obj === currUser) {
        if (extension == 'mp4') {
            return '<video width="250" style="float:right;" height="100" controls><source src="'+img+'" type="video/mp4"></video><small class="chat-time">'+formatDate(time)+'</small>';
        }else if(extension == 'mp3'){
            return '<audio controls style="float:right;"><source src="'+img+'" type="audio/mpeg"></audio><small class="chat-time">'+formatDate(time)+'</small>';
        }else if(extension == 'png' || extension == 'jpg' || extension == 'jpeg' || extension == 'gif'){
            return '<img class="send-img" src="'+img+'"><small class="chat-time">'+formatDate(time)+'</small>'
        }else{
            return '<p><a href="'+img+'" class="cur-send-file" download="'+img+'">' +GetFilename(img)+'</a><small class="chat-time">'+formatDate(time)+'</small></p>'
        }
    }else{
        return '<p><a href="'+img+'" class="image-name" download="'+img+'"><i class="fa fa-arrow-down download-btn" aria-hidden="true"></i>' +GetFilename(img)+'</a><small class="chat-time">'+formatDate(time)+'</small></p>'
    }
}

function drawMessage(message) {
    
    let msgDate = showDatesWeekDays(message.timestamp);
    let messageItem = '';
    if (lastDate != msgDate) {
        messageItem += `<div class="text-center text-white small mt-2"><span class="bg-cutom">${msgDate}</span>
        </div>`;
        lastDate = msgDate;
    }

    if (message.image) {
        messageItem += `
            <ul>
            <li class="${message.user === currentUser ? "replies" : "sent"}">
                <img src="${message.profile}" height="22" width="22" alt=""/>
                ${sentImageHide(message.user,currentUser,message.image,message.timestamp)}
            </li></ul>`;
    }else{
        messageItem += `
            <ul>
            <li class="${message.user === currentUser ? "replies" : "sent"}">
                <img src="${message.profile}" height="22" width="22" alt=""/>
                <p>${message.body} <small class="chat-time">${formatDate(message.timestamp)}</small></p>
            </li></ul>`;
    }

    $(messageItem).appendTo('#messages');
}

function onClickUserList(elem,recipient,status,last_online_time) {
    if (status == 1) {
        $('.online-status').html('Online');
    }else{
        var now = moment(new Date());
        var mom = moment.duration(now.diff(last_online_time)).humanize()
        $('.online-status').html('last seen <span class="time">'+mom+' ago'+'</span>');
    }
    $('.contact-profile').css('background','#FFF');
    $('#user-img').css('display','block');
    $('.message-input').css('display','block');
    $('.video-btn').css('display','block');
    $( ".msg-input" ).focus();
    currentRecipient = recipient;
    $("#name").text(capitalizeFirstLetter(recipient));
    messageList.empty();
    $.getJSON(`/api/v1/message/?target=${recipient}`, function (data) {
        var img = $(elem).find('img').attr('src');
        $('#user-img').attr('src', img);
        $(".contact").removeClass("active");
        $(elem).addClass("active");

        lastDate = "";
        for (let i = data.length - 1; i >= 0; i--) {
            drawMessage(data[i]);
        }

        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });
}

function updateUserList(data) {
    let data_username = data.user;
    if (data.user === currentUser) {
        data_username = data.recipient;
    }

    const obj = userList.find(v => v.username === data_username); obj.latest_message = data.body; obj.timestamp = data.timestamp;
    
    drawUserList();
}
function getMessageById(message) {
    const msg_id = JSON.parse(message).message;
    $.getJSON(`/api/v1/message/${msg_id}/`, function (data) {
        if (data.user === currentRecipient ||
            (data.recipient === currentRecipient && data.user == currentUser)) {
            drawMessage(data);
            updateUserList(data);
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    });
}


function sendMessage() {
    const body = chatInput.val();
    if (body.length > 0) {
        $.post('/api/v1/message/', {
            recipient: currentRecipient,
            body: body
        }).fail(function () {
            alert('Error! Check console!');
        });
        chatInput.val('');
    }
}


let showProfileSettings = () => {
    $("#profile-settings").css("left", 0); //.style.left = 0;
};

let hideProfileSettings = () => {
    $("#profile-settings").css("left", "-110%");
};

$(document).ready(function () {
    fetchUserList();
    let wsStart = 'ws://';
    if (window.location.protocol == 'https:') {
         wsStart = 'wss://'
    }
    var socket = new WebSocket(wsStart + window.location.host + `/ws?session_key=${sessionKey}`)

    chatInput.keypress(function (e) {
        if (e.keyCode == 13) sendMessage();
    });

    socket.onmessage = function (e) {
        getMessageById(e.data);
    };
});

$('#id_ajax_upload_form').submit(function(e){
    e.preventDefault();
    $form = $(this)
    var filename = $('.custom-file-input').val().replace(/C:\\fakepath\\/i, '')
    var formData = new FormData(this);
    formData.append('currentRecipient', currentRecipient);
    $.ajax({
        url: chat,
        type: 'POST',
        data: formData,
        success: function (response) {
            $('.error').remove();
            if (response.success) {
                $('#bio').text(response.bio);
                $('#profile-img').attr('src', '/media/images/'+filename);
                $('#myModal').modal('hide');
            }else if(response.errors) {
                $.each(response.errors, function(name, error){
                    error = '<small class="text-danger error mt-2">' + error + '</small>'
                    $form.find('[name=' + name + ']').after(error);
                })
            }

        },
        cache: false,
        contentType: false,
        processData: false
    });
});

function formatAMPM(date) {
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var ampm = hours >= 12 ? 'pm' : 'am';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? '0'+minutes : minutes;
  var strTime = hours + ':' + minutes + ' ' + ampm;
  return strTime;
}

function formatDate(date) {
    var dateUTC = new Date(date);
    var dateUTC = dateUTC.getTime() 
    var dateIST = new Date(dateUTC);
    var dateIST = formatAMPM(dateIST);
    return dateIST;
}

$(document).ready(function(){
   $('.contact-profile').css('background','#E6EAEA');
   $('#user-img').css('display','none');
   $('.message-input').css('display','none');
   $('.video-btn').css('display','none');

    setInterval(updateUserStatus, 10000);

    function updateUserStatus() {
         $.ajax({
             url: urlOnline,
             method: 'GET',
             dataType: 'json',
             data: {
                 'user_id': currentUserId,
             },
             success: function(data) {
                fetchUserList();
             }
         })
    }

function readURL(input, type) {
    if (input) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $("." + type).html('<img src="' + e.target.result + '"/>');
        }

        reader.readAsDataURL(input);
    }
}

$('body').on('change','#my_file',function (argument) {
    var image = this.files[0];
    var token = $('input[name="csrfmiddlewaretoken"]').val();

    if (typeof image !== "undefined") {        
        formData = new FormData;
        formData.append('image', image);
        formData.append('currentRecipient', currentRecipient);
        formData.append('_token', $('input[name="csrfmiddlewaretoken"]').val());
        $.ajax({
            type: "POST",
            contentType: false,
            processData: false,
            headers: {
               'X-CSRFToken': token
            },
            url: chatSendImage,
            data: formData,
            success: function (data) {
                console.log(data);
            },
            fail: function (xhr, textStatus, errorThrown) {
                $(".cli-" + item).removeAttr("disabled");
            }
        });
    }
});

});
