// Nebula.AI Frontend JavaScript
class NebulaAI {
    constructor() {
        this.conversationCount = 0;
        this.currentLogType = 'gemini';
        this.conversationHistory = [];
        this.initialize();
    }

    initialize() {
        this.bindEvents();
        this.loadUserEmail();
        this.fetchLogs();
        this.updateConversationCount();
    }

    bindEvents() {
        // Chat form submission
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => this.handleChatSubmit(e));
        }

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleQuickAction(e));
        });

        // Email input
        const emailInput = document.getElementById('user-email');
        if (emailInput) {
            emailInput.addEventListener('change', (e) => this.saveUserEmail(e.target.value));
        }

        // Tool buttons
        const testApisBtn = document.getElementById('test-apis-btn');
        if (testApisBtn) {
            testApisBtn.addEventListener('click', () => this.testAllAPIs());
        }

        const clearHistoryBtn = document.getElementById('clear-history-btn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        }

        // Log tabs
        document.querySelectorAll('.log-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchLogTab(e));
        });

        // Help button and modal
        const helpBtn = document.getElementById('help-btn');
        const modal = document.getElementById('examples-modal');
        const closeModal = document.getElementById('close-modal');

        if (helpBtn && modal) {
            helpBtn.addEventListener('click', () => {
                modal.style.display = 'flex';
            });
        }

        if (closeModal && modal) {
            closeModal.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }

        // Close modal on outside click
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }

        // Example query clicks
        document.querySelectorAll('.example-category li').forEach(item => {
            item.addEventListener('click', (e) => {
                const query = e.target.textContent.replace(/"/g, '');
                document.getElementById('user-query').value = query;
                document.getElementById('examples-modal').style.display = 'none';
                document.getElementById('user-query').focus();
            });
        });
    }

    async handleChatSubmit(e) {
        e.preventDefault();

        const queryInput = document.getElementById('user-query');
        const query = queryInput.value.trim();

        if (!query) {
            this.showNotification('Please enter a query.', 'warning');
            return;
        }

        const sendBtn = document.querySelector('.send-btn');
        const btnText = sendBtn.querySelector('.btn-text');
        const spinner = sendBtn.querySelector('.loading-spinner');

        // Show loading state
        btnText.style.display = 'none';
        spinner.style.display = 'inline-block';
        sendBtn.disabled = true;

        try {
            const userEmail = document.getElementById('user-email').value;
            const response = await this.sendRequest('/process_goal', {
                query: query,
                user_email: userEmail
            });

            this.displayResponse(response);
            this.addToConversationHistory(query, response);
            this.updateConversationCount();

            // Clear the input
            queryInput.value = '';

        } catch (error) {
            console.error('Error processing query:', error);
            this.displayResponse({
                success: false,
                message: `An error occurred: ${error.message}`
            });
        } finally {
            // Reset button state
            btnText.style.display = 'inline';
            spinner.style.display = 'none';
            sendBtn.disabled = false;
        }
    }

    handleQuickAction(e) {
        const action = e.currentTarget.getAttribute('data-action');
        if (action) {
            document.getElementById('user-query').value = action;
            document.getElementById('user-query').focus();
        }
    }

    async sendRequest(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    displayResponse(response) {
        const responseCard = document.getElementById('response-card');
        const responseContent = document.getElementById('response-content');
        const optionsCard = document.getElementById('options-card');

        responseCard.style.display = 'block';

        // Clear previous options
        optionsCard.style.display = 'none';

        if (response.success) {
            responseContent.innerHTML = `
                <div class="response-success">
                    <i class="fas fa-check-circle"></i> ${response.message}
                </div>
            `;

            // Handle next actions
            if (response.next_action) {
                this.handleNextAction(response);
            }
        } else {
            let errorMessage = response.message || response.error || 'An error occurred';

            // Special handling for assistant unavailable
            if (response.error_type === 'assistant_unavailable') {
                errorMessage += `
                    <div class="troubleshooting-info" style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                        <h4>🔧 Troubleshooting Steps:</h4>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            ${response.troubleshooting ? response.troubleshooting.map(step => `<li>${step}</li>`).join('') : ''}
                        </ul>
                        <p><strong>Note:</strong> Without the Assistant service, calendar scheduling and email features will not work.</p>
                    </div>
                `;
            }

            responseContent.innerHTML = `
                <div class="response-error">
                    <i class="fas fa-exclamation-circle"></i> ${errorMessage}
                </div>
            `;

            // Handle missing fields
            if (response.next_action === 'input_missing_fields' && response.missing_fields) {
                this.showMissingFieldsForm(response.missing_fields);
            }
        }

        // Scroll to response
        responseCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    handleNextAction(response) {
        const optionsCard = document.getElementById('options-card');
        const optionsTitle = document.getElementById('options-title');
        const optionsContent = document.getElementById('options-content');

        switch (response.next_action) {
            case 'select_time_slot':
                optionsTitle.innerHTML = '⏰ Available Time Slots';
                optionsContent.innerHTML = this.renderTimeSlots(response.options || []);
                optionsCard.style.display = 'block';
                break;

            case 'select_restaurant':
                optionsTitle.innerHTML = '🍽️ Restaurant Options';
                optionsContent.innerHTML = this.renderRestaurants(response.options || []);
                optionsCard.style.display = 'block';
                break;

            case 'display_schedules':
                optionsTitle.innerHTML = '📅 Team Schedules';
                optionsContent.innerHTML = this.renderSchedules(response.schedules || {});
                optionsCard.style.display = 'block';
                break;

            case 'complete':
                // Task completed, no additional action needed
                break;
        }
    }

    renderTimeSlots(timeSlots) {
        if (!timeSlots.length) {
            return '<p class="text-info">No time slots available.</p>';
        }

        return timeSlots.map((slot, index) => `
            <div class="option-item" data-type="time-slot" data-index="${index}">
                <h4>${slot.time}</h4>
                <p>Duration: ${slot.duration} minutes</p>
                <p>Available for: ${slot.attendees ? slot.attendees.join(', ') : 'All attendees'}</p>
            </div>
        `).join('');
    }

    renderRestaurants(restaurants) {
        if (!restaurants.length) {
            return '<p class="text-info">No restaurants found.</p>';
        }

        return restaurants.slice(0, 5).map((restaurant, index) => `
            <div class="option-item" data-type="restaurant" data-index="${index}">
                <h4>${restaurant.name}</h4>
                <p><i class="fas fa-star"></i> Rating: ${restaurant.rating}/5</p>
                <p><i class="fas fa-map-marker-alt"></i> ${restaurant.address}</p>
                ${restaurant.phone ? `<p><i class="fas fa-phone"></i> ${restaurant.phone}</p>` : ''}
                <p><i class="fas fa-tag"></i> Price: ${'$'.repeat(restaurant.price_level || 1)}</p>
                ${restaurant.website ? `<p><i class="fas fa-globe"></i> <a href="${restaurant.website}" target="_blank">Website</a></p>` : ''}
                <p><i class="fas fa-info-circle"></i> Source: ${restaurant.source}</p>
            </div>
        `).join('');
    }

    renderSchedules(schedules) {
        if (!Object.keys(schedules).length) {
            return '<p class="text-info">No schedule data available.</p>';
        }

        return Object.entries(schedules).map(([email, schedule]) => `
            <div class="schedule-item">
                <h4>${email}</h4>
                ${schedule && schedule.length ?
                schedule.map(event => `
                        <div class="event-item">
                            <strong>${event.title}</strong><br>
                            ${event.start_time} - ${event.end_time}
                        </div>
                    `).join('') :
                '<p class="text-info">No events scheduled</p>'
            }
            </div>
        `).join('');
    }

    showMissingFieldsForm(missingFields) {
        const optionsCard = document.getElementById('options-card');
        const optionsTitle = document.getElementById('options-title');
        const optionsContent = document.getElementById('options-content');

        optionsTitle.innerHTML = '📝 Additional Information Required';

        const formHTML = `
            <form id="missing-fields-form">
                ${missingFields.map(field => `
                    <div class="form-group">
                        <label for="${field}">${field}:</label>
                        <textarea id="${field}" name="${field}" rows="3" placeholder="Please provide: ${field}"></textarea>
                    </div>
                `).join('')}
                <button type="submit" class="send-btn">Submit Information</button>
            </form>
        `;

        optionsContent.innerHTML = formHTML;
        optionsCard.style.display = 'block';

        // Bind form submission
        document.getElementById('missing-fields-form').addEventListener('submit', (e) => {
            this.handleMissingFieldsSubmit(e, missingFields);
        });
    }

    async handleMissingFieldsSubmit(e, missingFields) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const missingInfo = {};

        missingFields.forEach(field => {
            missingInfo[field] = formData.get(field);
        });

        // Compose updated query
        const lastConversation = this.conversationHistory[this.conversationHistory.length - 1];
        const originalQuery = lastConversation ? lastConversation.query : '';
        const filledInfo = Object.entries(missingInfo)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n');

        const updatedQuery = `${originalQuery}\n${filledInfo}`;

        try {
            const userEmail = document.getElementById('user-email').value;
            const response = await this.sendRequest('/process_goal', {
                query: updatedQuery,
                user_email: userEmail
            });

            this.displayResponse(response);
            this.addToConversationHistory(updatedQuery, response);
            this.updateConversationCount();

        } catch (error) {
            console.error('Error processing updated query:', error);
            this.displayResponse({
                success: false,
                message: `An error occurred: ${error.message}`
            });
        }
    }

    addToConversationHistory(query, response) {
        const conversation = {
            timestamp: new Date().toISOString(),
            query: query,
            response: response
        };

        this.conversationHistory.unshift(conversation);

        // Keep only last 10 conversations
        if (this.conversationHistory.length > 10) {
            this.conversationHistory = this.conversationHistory.slice(0, 10);
        }

        this.updateConversationsDisplay();
    }

    updateConversationsDisplay() {
        const conversationsList = document.getElementById('conversations-list');

        if (this.conversationHistory.length === 0) {
            conversationsList.innerHTML = '<p class="no-conversations">💡 No conversations yet. Try asking something!</p>';
            return;
        }

        const conversationsHTML = this.conversationHistory.slice(0, 5).map(conv => `
            <div class="conversation-item">
                <div class="conversation-query">${this.truncateText(conv.query, 50)}</div>
                <div class="conversation-response">${this.truncateText(conv.response.message || 'No response', 80)}</div>
                <div class="conversation-time">${this.formatTimestamp(conv.timestamp)}</div>
            </div>
        `).join('');

        conversationsList.innerHTML = conversationsHTML;
    }

    updateConversationCount() {
        this.conversationCount = this.conversationHistory.length;
        const countElement = document.getElementById('conversation-count');
        if (countElement) {
            countElement.textContent = this.conversationCount;
        }
    }

    async testAllAPIs() {
        const testBtn = document.getElementById('test-apis-btn');
        const originalText = testBtn.innerHTML;

        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
        testBtn.disabled = true;

        try {
            const response = await this.sendRequest('/test_apis', {});

            let message = 'API Test Results:\n';
            for (const [service, result] of Object.entries(response.results || {})) {
                message += `${service}: ${result}\n`;
            }

            this.showNotification(message, response.success ? 'success' : 'error');

        } catch (error) {
            this.showNotification(`Error testing APIs: ${error.message}`, 'error');
        } finally {
            testBtn.innerHTML = originalText;
            testBtn.disabled = false;
        }
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear all conversation history?')) {
            this.conversationHistory = [];
            this.updateConversationsDisplay();
            this.updateConversationCount();

            // Hide response and options cards
            document.getElementById('response-card').style.display = 'none';
            document.getElementById('options-card').style.display = 'none';

            this.showNotification('History cleared successfully!', 'success');
        }
    }

    switchLogTab(e) {
        // Remove active class from all tabs
        document.querySelectorAll('.log-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Add active class to clicked tab
        e.target.classList.add('active');

        // Update current log type
        this.currentLogType = e.target.getAttribute('data-log');

        // Fetch logs for the selected type
        this.fetchLogs();
    }

    async fetchLogs() {
        try {
            const response = await fetch(`/get_logs?type=${this.currentLogType}`);
            const data = await response.json();

            const logContent = document.getElementById('log-content');
            if (data.logs && data.logs.length > 0) {
                logContent.textContent = data.logs.join('\n');
            } else {
                logContent.textContent = 'No logs available.';
            }

            // Auto-scroll to bottom
            logContent.scrollTop = logContent.scrollHeight;

        } catch (error) {
            console.error('Error fetching logs:', error);
            document.getElementById('log-content').textContent = 'Failed to load logs.';
        }
    }

    saveUserEmail(email) {
        localStorage.setItem('nebula_user_email', email);
        if (email) {
            this.showNotification('Email updated successfully!', 'success');
        }
    }

    loadUserEmail() {
        const savedEmail = localStorage.getItem('nebula_user_email');
        if (savedEmail) {
            document.getElementById('user-email').value = savedEmail;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        // Add styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '16px 20px',
            borderRadius: '8px',
            color: 'white',
            zIndex: '10000',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            maxWidth: '400px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });

        // Set background color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        // Add to document
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Add close functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.removeNotification(notification);
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
            this.removeNotification(notification);
        }, 5000);
    }

    removeNotification(notification) {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.nebulaAI = new NebulaAI();
});

// Handle option selection - moved to end of file for clarity
document.addEventListener('click', function (e) {
    // Handle option item selection
    if (e.target.closest('.option-item')) {
        const item = e.target.closest('.option-item');
        const type = item.getAttribute('data-type');
        const index = parseInt(item.getAttribute('data-index'));

        // Remove previous selections
        document.querySelectorAll('.option-item').forEach(function (el) {
            el.classList.remove('selected');
        });

        // Mark current item as selected
        item.classList.add('selected');

        // Handle confirmation for time-slot and restaurant
        if (type === 'time-slot' || type === 'restaurant') {
            // Remove any existing confirm button
            const existingBtn = document.querySelector('.option-confirm-btn');
            if (existingBtn) {
                existingBtn.remove();
            }

            // Create new confirm button
            const confirmBtn = document.createElement('button');
            confirmBtn.className = 'send-btn option-confirm-btn';
            confirmBtn.style.marginTop = '16px';

            if (type === 'time-slot') {
                confirmBtn.innerHTML = '<i class="fas fa-check"></i> Confirm Meeting';
            } else {
                confirmBtn.innerHTML = '<i class="fas fa-check"></i> Confirm Restaurant';
            }

            // Add click handler for confirmation
            confirmBtn.onclick = function () {
                confirmSelection(type, index);
            };

            // Append button to the selected item
            item.appendChild(confirmBtn);
        }
    }
});

// Separate function to handle confirmation
async function confirmSelection(type, index) {
    try {
        console.log('Confirming selection:', type, index);

        const userEmail = document.getElementById('user-email').value || '';
        const requestData = {
            type: type,
            index: index,
            user_email: userEmail
        };

        console.log('Sending confirmation request:', requestData);

        const response = await fetch('/confirm_selection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            // Try to get the error message from the response
            let errorMessage = 'HTTP error! status: ' + response.status;
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                console.error('Could not parse error response:', e);
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('Confirmation result:', result);

        // Display the response using the existing method
        if (window.nebulaAI) {
            window.nebulaAI.displayResponse(result);
            window.nebulaAI.addToConversationHistory('Confirmed ' + type + ' selection', result);
            window.nebulaAI.updateConversationCount();
        }

        // Remove the options card after successful confirmation
        const optionsCard = document.getElementById('options-card');
        if (optionsCard) {
            optionsCard.style.display = 'none';
        }

    } catch (error) {
        console.error('Error confirming selection:', error);

        if (window.nebulaAI) {
            window.nebulaAI.showNotification('Error confirming selection: ' + error.message, 'error');
        } else {
            alert('Error confirming selection: ' + error.message);
        }
    }
}