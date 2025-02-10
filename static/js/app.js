document.addEventListener("DOMContentLoaded", async () => {
    await initializeChat();

    // Listen for "Enter" key in the input box
    document.getElementById("prompt").addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevents new line in input
            sendPrompt();
        }
    });
});

async function initializeChat() {
    try {
        const response = await fetch("/chat", { method: "POST" });
        const data = await response.json();
        if (data.error) {
            console.error("Error initializing chat:", data.error);
            alert("Chat initialization failed. Try again.");
        } else {
            displayMessage("Chat initialized! Ask me anything about the PDF.", "model-message");
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

async function sendPrompt() {
    const prompt = document.getElementById("prompt").value.trim();
    if (!prompt) {
        alert("Please enter a prompt.");
        return;
    }

    displayMessage(prompt, "user-message");
    document.getElementById("prompt").value = "";

    // Show "Typing..." while waiting for a response
    let typingMessage = displayMessage("Typing...", "model-message");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt }),
        });

        const data = await response.json();
        document.getElementById("chat-box").removeChild(typingMessage); // Remove "Typing..." message

        if (response.ok) {
            displayMessage(data.response, "model-message");
        } else {
            displayMessage("Error: " + data.error, "error-message");
        }
    } catch (error) {
        document.getElementById("chat-box").removeChild(typingMessage);
        displayMessage("Error: " + error.message, "error-message");
    }
}

function displayMessage(message, className) {
    const chatBox = document.getElementById("chat-box");
    const msgElement = document.createElement("div");
    msgElement.className = className;
    msgElement.innerHTML = message;
    chatBox.appendChild(msgElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgElement;  // Return message element for "Typing..."
}
