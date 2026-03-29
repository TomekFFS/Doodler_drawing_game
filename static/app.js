const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const messagesList = document.getElementById('messages');


const clientId = Date.now()

const socket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);


socket.onmessage = function(event) {

    //parsing the JSON passed from the backend
    const parsedData = JSON.parse(event.data) 

    // chat messages:
    if (parsedData.type === "chat"){
        const message = document.createElement('li') 

        // If you are the sender:
        if (String(parsedData.user_id) === String(clientId)){ 
            message.textContent = `You: ${parsedData.message}`
            message.classList.add('my-msg')
        }

        // If you are the receiver:
        else { 
            message.textContent = `User#${parsedData.user_id}: ${parsedData.message}`
        }
        messagesList.appendChild(message) 
    }

    // system messages:
    else if (parsedData.type === "system") {
        console.log("System event: ", parsedData.message)

        // pass on the count of users
        const count = document.getElementById("user-count")
        count.innerText = `Active users: ${parsedData.active_users}`

        // display it in the lobby's chat
        const sysMessage = document.createElement('li')
        sysMessage.textContent = parsedData.message
        sysMessage.classList.add("system-msg")

        messagesList.appendChild(sysMessage)
    }

    // scroll down to the new message (if overflow the screen)
    window.scrollTo(0, document.body.scrollHeight);
}

chatForm.onsubmit = function(event) {
    event.preventDefault() // prevent the page from refreshing

    const message = messageInput.value; // deklaracja wiadomości, to co jest w polu input

    if (message) { // jeśli jest cokolwiek we wiadomości 
        socket.send(message) // wyślij wiadomość poprzez wtyczkę 
        messageInput.value = '' // usuń zawartość pola input po wysłaniu
    }
}


socket.onerror = function(error) {
    console.error("WebSocket Error: ", error);
};

socket.onclose = function(event) {
    console.warn("WebSocket Connection Closed. Code:", event.code, "Reason:", event.reason);
};