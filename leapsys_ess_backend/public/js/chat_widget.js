(function() {
    let chatState = {
        isOpen: false,
        activeRoom: null,
        rooms: [],
        messages: [],
        pollingInterval: null
    };

    // SVG Icons
    const icons = {
        chat: `<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 9h12v2H6V9zm8 5H6v-2h8v2zm4-6H6V6h12v2z"/></svg>`,
        close: `<svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>`,
        back: `<svg viewBox="0 0 24 24"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" fill="white"/></svg>`,
        send: `<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>`
    };

    // Build DOM
    function buildWidget() {
        const wrapper = document.createElement('div');
        wrapper.id = 'leapsys-chat-widget';
        wrapper.innerHTML = `
            <div class="chat-widget-window" id="chat-window">
                <div class="chat-widget-header">
                    <div class="chat-widget-back" id="chat-back-btn" style="display:none; margin-right: 12px;">
                        ${icons.back}
                    </div>
                    <h4 id="chat-header-title">Messages</h4>
                    <div style="flex:1"></div>
                </div>
                
                <!-- Chat List View -->
                <div class="chat-widget-body chat-list-view" id="chat-list-view">
                    <div id="chat-list-container" style="padding-bottom: 20px;">
                        <div style="padding: 20px; text-align: center; color: #94a3b8;">Loading...</div>
                    </div>
                </div>

                <!-- Chat Room View -->
                <div class="chat-widget-body chat-room-view" id="chat-room-view">
                    <div class="chat-messages-container" id="chat-messages-container"></div>
                    <div class="chat-input-area">
                        <input type="text" id="chat-input-field" placeholder="Type a message..." />
                        <button class="chat-send-btn" id="chat-send-btn">
                            ${icons.send}
                        </button>
                    </div>
                </div>
            </div>

            <div class="chat-widget-fab" id="chat-fab">
                <div id="chat-fab-icon">${icons.chat}</div>
                <div class="chat-widget-badge" id="chat-unread-badge" style="display:none">0</div>
            </div>
        `;
        document.body.appendChild(wrapper);

        bindEvents();
        startPolling();
    }

    function bindEvents() {
        document.getElementById('chat-fab').addEventListener('click', toggleWidget);
        document.getElementById('chat-back-btn').addEventListener('click', showChatList);
        
        const sendBtn = document.getElementById('chat-send-btn');
        const inputField = document.getElementById('chat-input-field');
        
        sendBtn.addEventListener('click', sendMessage);
        inputField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    }

    function toggleWidget() {
        chatState.isOpen = !chatState.isOpen;
        const win = document.getElementById('chat-window');
        const icon = document.getElementById('chat-fab-icon');
        
        if (chatState.isOpen) {
            win.classList.add('open');
            icon.innerHTML = icons.close;
            document.getElementById('chat-unread-badge').style.display = 'none'; // Clear badge
            if (!chatState.activeRoom) {
                fetchRooms();
            }
        } else {
            win.classList.remove('open');
            icon.innerHTML = icons.chat;
        }
    }

    function showChatList() {
        chatState.activeRoom = null;
        document.getElementById('chat-list-view').classList.remove('hidden');
        document.getElementById('chat-room-view').classList.remove('active');
        document.getElementById('chat-back-btn').style.display = 'none';
        document.getElementById('chat-header-title').innerText = 'Messages';
        fetchRooms();
    }

    function openRoom(roomId, roomName) {
        chatState.activeRoom = roomId;
        document.getElementById('chat-list-view').classList.add('hidden');
        document.getElementById('chat-room-view').classList.add('active');
        document.getElementById('chat-back-btn').style.display = 'flex';
        document.getElementById('chat-header-title').innerText = roomName;
        
        document.getElementById('chat-messages-container').innerHTML = '<div style="padding: 20px; text-align: center; color: #94a3b8;">Loading...</div>';
        fetchMessages();
    }

    // API Calls
    function fetchRooms() {
        frappe.call({
            method: 'leapsys_ess_backend.api.chat.get_rooms',
            callback: function(r) {
                if (r.message && r.message.success) {
                    chatState.rooms = r.message.data || [];
                    renderRooms();
                }
            }
        });
    }

    function fetchMessages() {
        if (!chatState.activeRoom) return;
        frappe.call({
            method: 'leapsys_ess_backend.api.chat.get_messages',
            args: { room_id: chatState.activeRoom },
            callback: function(r) {
                if (r.message && r.message.success) {
                    chatState.messages = r.message.data || [];
                    renderMessages();
                }
            }
        });
    }

    function sendMessage() {
        const input = document.getElementById('chat-input-field');
        const text = input.value.trim();
        if (!text || !chatState.activeRoom) return;
        
        input.value = '';
        // Optimistic UI
        chatState.messages.push({
            sender: frappe.session.user,
            content: text,
            timestamp: new Date().toISOString()
        });
        renderMessages();

        frappe.call({
            method: 'leapsys_ess_backend.api.chat.send_message',
            args: {
                room_id: chatState.activeRoom,
                content: text
            },
            callback: function(r) {
                fetchMessages(); // Sync back
            }
        });
    }

    // Rendering
    function renderRooms() {
        const container = document.getElementById('chat-list-container');
        if (!chatState.rooms.length) {
            container.innerHTML = '<div style="padding: 40px 20px; text-align: center; color: #94a3b8;">No messages yet. Use the mobile app to start a conversation!</div>';
            return;
        }

        let html = '';
        chatState.rooms.forEach(room => {
            const preview = room.latest_message ? room.latest_message.content : 'New chat';
            const initial = room.room_name ? room.room_name.charAt(0).toUpperCase() : 'G';
            html += `
                <div class="chat-room-item" data-id="${room.room_id}" data-name="${room.room_name}">
                    <div class="chat-room-avatar">${initial}</div>
                    <div class="chat-room-info">
                        <div class="chat-room-name">${room.room_name}</div>
                        <div class="chat-room-preview">${preview}</div>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;

        // Attach clicks
        container.querySelectorAll('.chat-room-item').forEach(el => {
            el.addEventListener('click', function() {
                openRoom(this.getAttribute('data-id'), this.getAttribute('data-name'));
            });
        });
    }

    function renderMessages() {
        const container = document.getElementById('chat-messages-container');
        let html = '';
        
        chatState.messages.forEach((msg, idx) => {
            const isMe = msg.sender === frappe.session.user;
            const time = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            html += `
                <div class="chat-message ${isMe ? 'sent' : 'received'}">
                    ${!isMe ? `<div style="font-size:10px; color:#94a3b8; margin-bottom:2px; margin-left:4px;">${msg.sender_name || msg.sender}</div>` : ''}
                    <div class="chat-message-bubble">${msg.content}</div>
                    <div class="chat-message-time">${time}</div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        container.scrollTop = container.scrollHeight;
    }

    function startPolling() {
        setInterval(() => {
            if (chatState.isOpen) {
                if (chatState.activeRoom) {
                    fetchMessages();
                } else {
                    fetchRooms();
                }
            } else {
                // Background poll to check for new messages to show badge
                frappe.call({
                    method: 'leapsys_ess_backend.api.chat.get_rooms',
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            // Simple logic: if latest message time changed, show a generic dot
                            // A real implementation would store lastRead locally.
                            const latestRooms = r.message.data;
                            if (chatState.rooms.length > 0 && latestRooms.length > 0) {
                                const oldLatest = chatState.rooms[0].latest_message;
                                const newLatest = latestRooms[0].latest_message;
                                if (newLatest && oldLatest && newLatest.timestamp !== oldLatest.timestamp) {
                                    document.getElementById('chat-unread-badge').style.display = 'flex';
                                }
                            }
                            chatState.rooms = latestRooms;
                        }
                    }
                });
            }
        }, 5000);
    }

    // Initialize only when Frappe Desk is ready
    if (typeof $(document) !== 'undefined') {
        $(document).on('app_ready', function() {
            if (!document.getElementById('leapsys-chat-widget') && frappe.session && frappe.session.user !== "Guest") {
                buildWidget();
            }
        });
    }
    
    // Fallback if already loaded
    setTimeout(() => {
        if (!document.getElementById('leapsys-chat-widget') && frappe && frappe.session && frappe.session.user !== "Guest") {
            buildWidget();
        }
    }, 2000);
})();
