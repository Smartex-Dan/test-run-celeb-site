 let activeUser = null;

function selectUser(id, username) {
    activeUser = id;
    document.getElementById("messageInput").disabled = false;
    document.getElementById("sendBtn").disabled = false;
    loadMessages();
}

function loadMessages() {
    if (!activeUser) return;

    fetch(`/get_messages/${activeUser}`)
        .then(res => res.json())
        .then(messages => {
            const box = document.getElementById("messages");
            box.innerHTML = "";

            messages.forEach(msg => {
                const div = document.createElement("div");
                div.classList.add("message");

                if (msg.sender_id === CURRENT_USER_ID) {
                    div.classList.add("sent");
                } else {
                    div.classList.add("received");
                }

                div.innerText = msg.message;
                box.appendChild(div);
            });

            box.scrollTop = box.scrollHeight;
        });
}

function sendMessage() {
    const input = document.getElementById("messageInput");
    const text = input.value.trim();
    if (!text) return;

    fetch("/send_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            receiver_id: activeUser,
            message: text
        })
    }).then(() => {
        input.value = "";
        loadMessages();
    });
}

setInterval(loadMessages, 3000);
