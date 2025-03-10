<script lang="ts">
    // Chatbot state
    let isChatOpen = false;
    let messages = [
        { 
            type: 'bot', 
            content: 'Hi! I can help you with information about this PDF-Chat application. What would you like to know?' 
        }
    ];
    let userInput = '';
    
    // Handle sending a message
    function handleSend() {
        if (!userInput.trim()) return;
        
        // Add user message
        messages = [...messages, { type: 'user', content: userInput }];
        
        // Process user input and create bot response
        const response = generateResponse(userInput);
        setTimeout(() => {
            messages = [...messages, { type: 'bot', content: response }];
        }, 500);
        
        userInput = '';
    }
    
    // Generate chatbot responses
    function generateResponse(input: string) {
        input = input.toLowerCase();
        
        if (input.includes('github') || input.includes('source') || input.includes('code')) {
            return 'You can find the source code for this project on GitHub: <a href="https://github.com/govardhan27/pdf-chat/" target="_blank" class="text-blue-600 underline">https://github.com/govardhan27/pdf-chat/</a>';
        }
        
        if (input.includes('what') && (input.includes('this') || input.includes('app') || input.includes('application'))) {
            return 'This is a PDF-Chat application that allows you to upload PDF documents and chat with them using AI. You can ask questions about your documents and get intelligent answers based on their content.';
        }
        
        if (input.includes('how') && input.includes('use')) {
            return 'To use this application: 1) Click "New" to upload a PDF, 2) Click "View" on any document to open it, 3) Ask questions about the document in the chat panel.';
        }
        
        if (input.includes('feature')) {
            return 'Key features include: document upload, AI-powered document chat, conversation history, and document management.';
        }
        
        return "I'm here to help with information about this PDF-Chat application. You can ask about its features, how to use it, or get the GitHub link to the source code!";
    }
    
    // Handle key press for Enter key
    function handleKeyPress(event: KeyboardEvent) {
        if (event.key === 'Enter') {
            handleSend();
        }
    }
</script>

<div 
    style="bottom: 64px;
        right: 64px;
        border-radius: 54px;
        background: linear-gradient(90deg, rgba(10, 64, 255, 0.1) 0%, rgba(10, 64, 255, 0) 95%), rgb(255, 255, 255);
        border: 3px solid rgba(10, 64, 255, 0.4);
        cursor: pointer;
        color: rgb(10, 64, 255);
        transition: 0.5s;
        box-shadow: rgba(10, 64, 255, 0.11) 0px 3px 26.25px 0px;
        padding: 12px 24px;
        position: fixed;
        z-index: 9999;"
    on:click={() => isChatOpen = !isChatOpen}
    on:keydown={(event) => { if (event.key === 'Enter' || event.key === ' ') { isChatOpen = !isChatOpen; } }}
    tabindex="0"
    role="button"
    aria-pressed={isChatOpen}
>
    {isChatOpen ? '✕ Close Help' : '💬 Ask AI?'}
</div>

{#if isChatOpen}
    <div class="fixed bottom-32 right-16 w-80 md:w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50 overflow-hidden flex flex-col" style="height: 400px;">
        <div style="background-color: #1e1e1e" class="bg-blue-600 text-white px-4 py-3 font-medium flex justify-between items-center">
            <span>PDF-Chat Assistant</span>
            <button on:click={() => isChatOpen = false} class="text-white hover:text-gray-200">✕</button>
        </div>
        
        <div class="flex-1 p-4 overflow-y-auto flex flex-col space-y-3">
            {#each messages as message}
                <div class={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div class={`max-w-3/4 p-3 rounded-lg ${message.type === 'user' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                        {#if message.type === 'bot'}
                            {@html message.content}
                        {:else}
                            {message.content}
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
        
        <div class="border-t p-3 flex">
            <input 
                type="text" 
                bind:value={userInput} 
                placeholder="Type your question here..." 
                class="flex-1 border rounded-l-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                on:keypress={handleKeyPress}
            />
            <button 
                on:click={handleSend}
                class="bg-blue-600 text-white rounded-r-lg px-4 py-2 hover:bg-blue-700"
            >
                Send
            </button>
        </div>
    </div>
{/if}


