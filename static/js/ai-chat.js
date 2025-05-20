// AI Chat JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const emergencyBanner = document.getElementById('emergency-banner');
    const emergencyCall = document.getElementById('emergency-call');
    const crisisText = document.getElementById('crisis-text');
    const suggestionChips = document.getElementById('suggestion-chips');
    
    // CSRF token for Django
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Add event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Set up suggestion bubbles
    document.querySelectorAll('.suggestion-bubble').forEach(bubble => {
        bubble.addEventListener('click', function() {
            userInput.value = this.textContent.trim();
            sendMessage();
        });
    });
    
    // Emergency buttons
    if (emergencyCall) {
        emergencyCall.addEventListener('click', function() {
            window.location.href = 'tel:911';
        });
    }
    
    if (crisisText) {
        crisisText.addEventListener('click', function() {
            window.location.href = 'sms:741741&body=HELP';
        });
    }
    
    // Initial suggestion chips
    updateSuggestionChips([
        "List shelters near me",
        "Show food banks in my area",
        "Find job opportunities",
        "List medical services"
    ]);
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addUserMessage(message);
        
        // Clear input
        userInput.value = '';
        
        // Show typing indicator
        addTypingIndicator();
        
        // Send to backend
        fetch('/ai-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Check if it's an emergency
            if (data.is_emergency) {
                emergencyBanner.classList.remove('hidden');
            }
            
            // Add AI response to chat
            addAssistantMessage(data.response, data.suggested_service_types);
            
            // Add services if available
            if (data.nearby_services && data.nearby_services.length > 0) {
                addServicesToChat(data.nearby_services);
            }
            
            // Update suggestion chips based on the context
            updateContextualSuggestions(data);
            
            // Scroll to bottom
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            addAssistantMessage('I apologize, but I encountered an error. Please try again.');
            scrollToBottom();
        });
    }
    
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start justify-end mb-4';
        
        messageDiv.innerHTML = `
            <div class="user-message">
                <p>${message}</p>
            </div>
            <div class="flex-shrink-0 ml-3">
                <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center shadow-sm">
                    <i class="fas fa-user text-white"></i>
                </div>
            </div>
        `;
        
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function addAssistantMessage(message, suggestedTypes = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start mb-4';
        
        // Format the message with proper HTML
        const formattedMessage = formatMessage(message);
        
        let html = `
            <div class="flex-shrink-0 mr-3">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shadow-sm">
                    <i class="fas fa-robot text-blue-600"></i>
                </div>
            </div>
            <div class="assistant-message">
                <div class="text-gray-800">${formattedMessage}</div>
        `;
        
        // Add follow-up suggestion bubbles if this is an AI message
        if (suggestedTypes && suggestedTypes.length > 0) {
            html += `<div class="mt-3 flex flex-wrap gap-2">`;
            
            // Add a "Show as list" button if the message might contain listable items
            if (message.includes("Here are") || message.includes("options") || 
                message.includes("consider") || suggestedTypes.length > 1) {
                html += `
                    <button class="suggestion-bubble text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium py-1.5 px-3 rounded-full transition-colors border border-blue-100">
                        Show as a list
                    </button>
                `;
            }
            
            // Add specific follow-up questions based on suggested service types
            suggestedTypes.forEach(type => {
                let suggestion = "";
                if (type.toLowerCase().includes("shelter")) {
                    suggestion = `List shelters with contact details`;
                } else if (type.toLowerCase().includes("food")) {
                    suggestion = `Show food banks with addresses`;
                } else if (type.toLowerCase().includes("employment") || type.toLowerCase().includes("job")) {
                    suggestion = `List job opportunities with contacts`;
                } else if (type.toLowerCase().includes("medical") || type.toLowerCase().includes("health")) {
                    suggestion = `Show medical services with phone numbers`;
                }
                
                if (suggestion) {
                    html += `
                        <button class="suggestion-bubble text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium py-1.5 px-3 rounded-full transition-colors border border-blue-100">
                            ${suggestion}
                        </button>
                    `;
                }
            });
            
            html += `</div>`;
        }
        
        html += `</div>`;
        
        messageDiv.innerHTML = html;
        chatContainer.appendChild(messageDiv);
        
        // Set up event listeners for the new suggestion bubbles
        messageDiv.querySelectorAll('.suggestion-bubble').forEach(bubble => {
            bubble.addEventListener('click', function() {
                userInput.value = this.textContent.trim();
                sendMessage();
            });
        });
        
        scrollToBottom();
    }
    
    function formatMessage(message) {
        // Check if the message already contains HTML
        if (message.includes('<ul>') || message.includes('<ol>') || 
            message.includes('<p>') || message.includes('<strong>')) {
            return message; // Already formatted as HTML
        }
        
        // Convert markdown-style bold to HTML
        let formattedMessage = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Check if the message contains list-like content
        if ((message.includes("1.") || message.includes("2.") || 
             message.includes("Here are") || message.includes("services")) && 
            !message.includes("<ul>")) {
            
            // Try to format as a proper list
            let lines = formattedMessage.split('\n');
            let inList = false;
            let formattedLines = [];
            
            for (let i = 0; i < lines.length; i++) {
                let line = lines[i].trim();
                
                // Check for list item patterns
                let listItemMatch = line.match(/^(\d+\.\s+|\-\s+|\*\s+)(.*)/);
                
                if (listItemMatch) {
                    if (!inList) {
                        // Start a new list
                        formattedLines.push("<ul class='list-disc pl-5 space-y-2 mt-2'>");
                        inList = true;
                    }
                    formattedLines.push(`<li><strong>${listItemMatch[2]}</strong></li>`);
                } else if (line.match(/^[A-Za-z0-9].*:$/)) {
                    // This looks like a header or category
                    if (inList) {
                        formattedLines.push("</ul>");
                        inList = false;
                    }
                    formattedLines.push(`<p class="font-medium mt-2">${line}</p>`);
                } else if (line.length > 0) {
                    if (inList) {
                        formattedLines.push("</ul>");
                        inList = false;
                    }
                    formattedLines.push(`<p>${line}</p>`);
                } else if (line.length === 0 && inList) {
                    formattedLines.push("</ul>");
                    inList = false;
                    formattedLines.push("<p></p>");
                } else if (line.length === 0) {
                    formattedLines.push("<p></p>");
                }
            }
            
            if (inList) {
                formattedLines.push("</ul>");
            }
            
            return formattedLines.join("");
        }
        
        // Convert line breaks to paragraphs for non-list content
        formattedMessage = formattedMessage.split('\n\n').map(para => 
            para.trim() ? `<p>${para.trim()}</p>` : ''
        ).join('');
        
        // Convert single line breaks within paragraphs
        formattedMessage = formattedMessage.replace(/<\/p><p>/g, '</p>\n<p>');
        formattedMessage = formattedMessage.replace(/<p>(.*?)\n(.*?)<\/p>/g, '<p>$1<br>$2</p>');
        
        return formattedMessage;
    }
    
    function addServicesToChat(services) {
        const servicesDiv = document.createElement('div');
        servicesDiv.className = 'flex items-start mb-4';
        
        let html = `
            <div class="flex-shrink-0 mr-3">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shadow-sm">
                    <i class="fas fa-robot text-blue-600"></i>
                </div>
            </div>
            <div class="assistant-message">
                <p class="font-medium text-gray-800 mb-3">Here are some services that might help:</p>
                <div class="space-y-3">
        `;
        
        services.forEach(service => {
            html += `
                <div class="service-card">
                    <div class="flex justify-between items-start">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            ${service.category}
                        </span>
                        ${service.distance ? `<span class="text-xs text-gray-500">${service.distance}</span>` : ''}
                    </div>
                    <h4 class="text-lg font-medium text-gray-900 mt-1">${service.name}</h4>
                    <div class="mt-2 space-y-1 text-sm text-gray-600">
            `;
            
            if (service.address) {
                html += `<p class="flex items-center"><i class="fas fa-map-marker-alt w-4 text-gray-400 mr-2"></i> ${service.address}</p>`;
            }
            
            if (service.phone) {
                html += `<p class="flex items-center"><i class="fas fa-phone w-4 text-gray-400 mr-2"></i> ${service.phone}</p>`;
            }
            
            if (service.hours) {
                html += `<p class="flex items-center"><i class="fas fa-clock w-4 text-gray-400 mr-2"></i> ${service.hours}</p>`;
            }
            
            html += `</div>`;
            
            if (service.website) {
                html += `
                    <div class="mt-3">
                        <a href="${service.website}" class="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800" target="_blank">
                            Visit Website <i class="fas fa-external-link-alt ml-1"></i>
                        </a>
                    </div>
                `;
            }
            
            html += `</div>`;
        });
        
        html += `</div></div>`;
        
        servicesDiv.innerHTML = html;
        chatContainer.appendChild(servicesDiv);
        scrollToBottom();
    }
    
    function updateSuggestionChips(suggestions) {
        suggestionChips.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const chip = document.createElement('button');
            chip.className = 'text-xs bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-1.5 px-3 rounded-full transition-colors';
            chip.textContent = suggestion;
            
            chip.addEventListener('click', function() {
                userInput.value = this.textContent;
                sendMessage();
            });
            
            suggestionChips.appendChild(chip);
        });
    }
    
    function updateContextualSuggestions(data) {
        let suggestions = [];
        
        // Add suggestions based on identified needs
        if (data.identified_needs) {
            data.identified_needs.forEach(need => {
                if (need === "shelter") {
                    suggestions.push("List shelters with contact details");
                } else if (need === "food") {
                    suggestions.push("Show food banks with addresses");
                } else if (need === "employment") {
                    suggestions.push("List job opportunities with contacts");
                } else if (need === "medical") {
                    suggestions.push("Show medical services near me");
                } else if (need === "mental health") {
                    suggestions.push("Find mental health support");
                }
            });
        }
        
        // Add general follow-up suggestions
        suggestions.push("Show more details");
        suggestions.push("How do I contact them?");
        
        // If we have location context, add location-specific suggestions
        if (data.response.toLowerCase().includes("bradford") || 
            (data.nearby_services && data.nearby_services.length > 0)) {
            suggestions.push("What's the closest to BD12BA?");
            suggestions.push("Which ones are open now?");
        }
        
        // Limit to 4 suggestions
        updateSuggestionChips(suggestions.slice(0, 4));
    }
    
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'flex items-start mb-4 typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="flex-shrink-0 mr-3">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shadow-sm">
                    <i class="fas fa-robot text-blue-600"></i>
                </div>
            </div>
            <div class="assistant-message flex items-center">
                <div class="typing-dots flex space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0s;"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s;"></div>
                </div>
            </div>
        `;
        
        chatContainer.appendChild(typingDiv);
        scrollToBottom();
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Add event listener for all "Show as a list" buttons
    document.addEventListener('click', function(e) {
        if (e.target && e.target.textContent.trim() === 'Show as a list') {
            userInput.value = "Show the previous information as a list";
            sendMessage();
        }
    });
});