
let socket = null;
let currentUsername = "";

const loginForm = document.getElementById("login-form");
const messageForm = document.getElementById("message-form");

const usernameInput = document.getElementById("username");
const messageInput = document.getElementById("message-input");

const loginSection = document.getElementById("login-section");
const chatSection = document.getElementById("chat-section");

const messagesContainer = document.getElementById("messages");
const usersList = document.getElementById("users-list");
const connectionStatus = document.getElementById("connection-status");


function updateConnectionStatus(connected) {
    connectionStatus.textContent = connected
        ? "Conectado"
        : "Desconectado";

    connectionStatus.classList.toggle("connected", connected);
    connectionStatus.classList.toggle("disconnected", !connected);
}


function connect(username) {
    socket = new WebSocket("ws://localhost:8765");

    socket.onopen = () => {
        updateConnectionStatus(true);

        socket.send(JSON.stringify({
            type: "join",
            username: username
        }));

        loginSection.classList.add("hidden");
        chatSection.classList.remove("hidden");

        messageInput.focus();
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        handleMessage(data);
    };

    socket.onclose = () => {
        updateConnectionStatus(false);
        console.log("Conexão WebSocket encerrada.");
    };

    socket.onerror = (error) => {
        console.error("Erro WebSocket:", error);
    };
}


function handleMessage(data) {
    switch (data.type) {
        case "chat_message":
            displayMessage(data);
            break;

        case "user_joined":
            displaySystemMessage(`${data.username} entrou no chat.`);
            break;

        case "user_left":
            displaySystemMessage(`${data.username} saiu do chat.`);
            break;

        case "users_update":
            updateUsersList(data.users);
            break;

        case "error":
            console.error(data.content);
            break;
    }
}


function displayMessage(data) {
    const emptyMessage = messagesContainer.querySelector(".empty-message");

    if (emptyMessage) {
        emptyMessage.remove();
    }

    const messageElement = document.createElement("div");

    messageElement.classList.add("message");

    if (data.username === currentUsername) {
        messageElement.classList.add("own");
    }

    const header = document.createElement("div");
    header.classList.add("message-header");

    const username = document.createElement("strong");
    username.textContent = data.username;

    const timestamp = document.createElement("span");
    timestamp.textContent = new Date(data.timestamp).toLocaleTimeString(
        "pt-BR",
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

    const content = document.createElement("p");
    content.textContent = data.content;

    header.append(username, timestamp);
    messageElement.append(header, content);

    messagesContainer.appendChild(messageElement);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}


function displaySystemMessage(content) {
    const messageElement = document.createElement("div");

    messageElement.classList.add("system-message");
    messageElement.textContent = content;

    messagesContainer.appendChild(messageElement);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}


function updateUsersList(users) {
    usersList.innerHTML = "";

    users.forEach((username) => {
        const item = document.createElement("li");

        item.textContent = `● ${username}`;

        usersList.appendChild(item);
    });
}


loginForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const username = usernameInput.value.trim();

    if (!username) {
        return;
    }

    currentUsername = username;

    connect(username);
});


messageForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const content = messageInput.value.trim();

    if (!content || !socket || socket.readyState !== WebSocket.OPEN) {
        return;
    }

    socket.send(JSON.stringify({
        type: "chat_message",
        content: content
    }));

    messageInput.value = "";
    messageInput.focus();
});
