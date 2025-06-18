document.addEventListener('DOMContentLoaded', () => {
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    const chatLog = document.getElementById('chatLog');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');

    /**
     * Adiciona uma mensagem ao chat log
     */
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.innerHTML = `<p>${text}</p>`;
        chatLog.appendChild(messageDiv);
        // Faz scroll automático para o fundo do chat
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    /**
     * Mostra o indicador de loading e desativa os inputs
     */
    function showLoading() {
        loadingIndicator.classList.add('active');
        askButton.disabled = true;
        questionInput.disabled = true;
        errorMessage.classList.remove('active');
    }

    /**
     * Esconde o indicador de loading e ativa os inputs
     */
    function hideLoading() {
        loadingIndicator.classList.remove('active');
        askButton.disabled = false;
        questionInput.disabled = false;
        questionInput.focus(); // Volta a focar o input
    }

    /**
     * Mostra uma mensagem de erro no ecrã
     */
    function showErrorMessage(message = "Oops! Something went wrong. Please try again.") {
        errorMessage.querySelector('p').textContent = message;
        errorMessage.classList.add('active');
    }

    /**
     * Evento ao clicar no botão "Ask"
     * Envia a pergunta para o backend e mostra a resposta
     */
    askButton.addEventListener('click', async () => {
        const question = questionInput.value.trim();
        if (question === '') {
            return;
        }

        addMessage(question, 'user');
        questionInput.value = '';
        showLoading();

        try {
            // Envia o pedido para o backend Python (Flask) no endpoint /ask
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Network response was not ok.');
            }

            const data = await response.json();
            addMessage(data.answer, 'bot');

        } catch (error) {
            console.error('Error asking question:', error);
            showErrorMessage(error.message);
        } finally {
            hideLoading();
        }
    });

    /**
     * Permite enviar a pergunta ao carregar na tecla Enter
     */
    questionInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            askButton.click();
        }
    });

    // Foco inicial no input ao carregar a página
    questionInput.focus();
});