document.addEventListener('DOMContentLoaded', () => {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {

        // Notify. user has joined
        socket.emit('joined');

        // Forget last channel when user add a new one
        document.querySelector('#newChannel').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        // When user leaves a channel, redirect to index
        document.querySelector('#leave').addEventListener('click', () => {

            // Notify, user has left. 
            socket.emit('left');

            localStorage.removeItem('last_channel');
            window.location.replace('/');
        })

        // When user log out -> Forget last channel
        document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('last_channel');
        });

        // Pressing Enter sends the message 
        document.querySelector('#comment').addEventListener("keydown", event => {
            if (event.key == "Enter") {
                document.getElementById("send-button").click();
            }
        });
        
        // Send button when pressed emits a "message sent" event
        document.querySelector('#send-button').addEventListener("click", () => {
            
            // Save time 
            let timestamp = new Date;
            timestamp = timestamp.toLocaleTimeString();

            // Save user message
            let msg = document.getElementById("comment").value;

            socket.emit('send message', msg, timestamp);
            
            // Clear box when message subḿitted
            document.getElementById("comment").value = '';
        });
    });
    
    // When user joins a channel, add a message and on users connected.
    socket.on('status', data => {
        let row = '<' + `${data.msg}` + '>'
        document.querySelector('#chat').value += row + '\n';
        localStorage.setItem('last_channel', data.channel)
    })

    // Message is announced
    socket.on('announce message', data => {

        // Print formatted message
        let row = '(' + `${data.timestamp}` + ') - ' + '[' + `${data.user}` + ']:  ' + `${data.msg}`
        document.querySelector('#chat').value += row + '\n'
    })

    
});