const postPk = JSON.parse(document.getElementById('json-post-pk').textContent);
const firstName = JSON.parse(document.getElementById('json-first-name').textContent);

function scrollToBottom() {
    let objDiv = document.getElementById("chat-messages");
    objDiv.scrollTop = objDiv.scrollHeight;
}

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/post/'
    + postPk
    + '/'
)

chatSocket.onmessage = function(e) {
    console.log('onmessage')

    const data = JSON.parse(e.data)

    if (data.message) {
        document.querySelector('#chat-messages').innerHTML += ('<b>' + data.firstName + '</b>: ' + data.message + '<br>');
    }
    else {
        alert("The message is empty")
    }

    scrollToBottom();
}

chatSocket.onclose = function(e) {
    console.log("the socket closed")
}

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;

    chatSocket.send(JSON.stringify({
        'message': message,
        'firstName': firstName,
        'postPk': postPk
    }));

    messageInputDom.value = '';
};