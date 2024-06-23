document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad del chat
    const chatButton = document.getElementById('chat-button');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const sendMessage = document.getElementById('send-message');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    chatButton.addEventListener('click', () => {
        chatWindow.style.display = 'flex';
    });

    closeChat.addEventListener('click', () => {
        chatWindow.style.display = 'none';
    });

    sendMessage.addEventListener('click', sendUserMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendUserMessage();
        }
    });

    function sendUserMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage('Usuario', message);
            // Aquí iría la lógica para enviar el mensaje a la IA y recibir una respuesta
            setTimeout(() => {
                addMessage('IA', 'Gracias por tu mensaje. ¿En qué puedo ayudarte con tu trading hoy?');
            }, 1000);
            userInput.value = '';
        }
    }

    function addMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${text}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Nueva funcionalidad de búsqueda
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    function performSearch() {
        const searchTerm = searchInput.value.trim();
        if (searchTerm) {
            // Aquí iría la lógica de búsqueda real
            console.log('Buscando:', searchTerm);
            alert(`Búsqueda realizada para: "${searchTerm}"`);
            // Limpia el input después de la búsqueda
            searchInput.value = '';
        }
    }
});