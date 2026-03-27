const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");

function appendMessage(text, sender) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.innerText = text;
  chatBox.appendChild(msg);

  chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
  const userText = input.value.trim();
  if (!userText) return;

  appendMessage(userText, "user");
  input.value = "";

  // Fake bot response (you can replace this with API call)
//   setTimeout(() => {
//     const botReply = "You said: " + userText;
//     appendMessage(botReply, "bot");
//   }, 500);
  setTimeout(() => {
    const botReply = "reply: " + sendQuestion(userText);
    appendMessage(botReply, "bot");
  }, 5000);
}

// Enter key support
input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});