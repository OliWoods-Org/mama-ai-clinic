// MAMA AI Clinic -- Chat interface

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSend = document.getElementById('chatSend');

let conversationHistory = [];

function addBubble(text, role) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return bubble;
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = '';
    addBubble(text, 'user');
    conversationHistory.push({ role: 'user', content: text });

    chatSend.disabled = true;
    const loadingBubble = addBubble('Thinking...', 'assistant');

    try {
        const resp = await fetch('/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: conversationHistory }),
        });
        const data = await resp.json();
        loadingBubble.textContent = data.response;
        conversationHistory.push({ role: 'assistant', content: data.response });
    } catch (err) {
        loadingBubble.textContent = 'Error: Could not reach the AI server. Check system status.';
    } finally {
        chatSend.disabled = false;
        chatInput.focus();
    }
}

chatSend.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});
