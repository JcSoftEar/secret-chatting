let socket = null;
let currentRoom = null;
let currentUser = null;

function generateRandomName() {
    const randomId = Math.floor(Math.random() * 9000) + 1000;
    return `匿名者${randomId}`;
}

function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 3000);
}

function initEntryPage() {
    const form = document.getElementById('entryForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const roomId = document.getElementById('roomId').value.trim();
        const password = document.getElementById('password').value.trim();
        const nickname = document.getElementById('nickname').value.trim();

        if (!roomId || !password) {
            showError('entryError', '请填写完整信息');
            return;
        }

        if (nickname) {
            currentUser = nickname;
        } else {
            currentUser = generateRandomName();
        }
        connectSocket(roomId, password);
    });
}

function connectSocket(roomId, password) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}`;
    
    socket = io(url);

    socket.on('connect', () => {
        socket.emit('join', {
            room_id: roomId,
            password: password,
            username: currentUser
        });
    });

    socket.on('join_success', (data) => {
        currentRoom = data.room_id;
        showChatPage(data.room_name);
    });

    socket.on('join_error', (data) => {
        showError('entryError', data.error);
        socket.disconnect();
    });

    socket.on('new_msg', (data) => {
        addMessage(data);
    });

    socket.on('disconnect', () => {
        console.log('已断开连接');
    });
}

function showChatPage(roomName) {
    document.getElementById('entryPage').style.display = 'none';
    document.getElementById('chatPage').style.display = 'flex';
    document.getElementById('roomName').textContent = roomName;

    const backBtn = document.getElementById('backBtn');
    backBtn.addEventListener('click', () => {
        socket.disconnect();
        location.reload();
    });

    initChatInput();
}

function initChatInput() {
    const textarea = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');

    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 84) + 'px';
        sendBtn.disabled = textarea.value.trim() === '';
    });

    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);
}

function sendMessage() {
    const textarea = document.getElementById('messageInput');
    const content = textarea.value.trim();

    if (!content || !socket) return;

    socket.emit('send_msg', {
        room_id: currentRoom,
        sender_name: currentUser,
        content: content
    });

    textarea.value = '';
    textarea.style.height = 'auto';
    document.getElementById('sendBtn').disabled = true;
}

function addMessage(data) {
    const messagesContainer = document.getElementById('chatMessages');

    if (data.sender_name === '系统') {
        const systemDiv = document.createElement('div');
        systemDiv.className = 'system-message';
        systemDiv.textContent = data.content;
        messagesContainer.appendChild(systemDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return;
    }

    const isSelf = data.sender_name !== '管理员';

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isSelf ? 'self' : ''}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = data.sender_name.charAt(0);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const senderName = document.createElement('div');
    senderName.className = 'sender-name';
    senderName.textContent = data.sender_name;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = data.content;

    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    const time = new Date(data.timestamp);
    timestamp.textContent = `${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`;

    contentDiv.appendChild(senderName);
    contentDiv.appendChild(bubble);
    contentDiv.appendChild(timestamp);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

document.addEventListener('DOMContentLoaded', () => {
    initEntryPage();
    checkUrlParams();
});

function checkUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const roomId = params.get('room');
    const password = params.get('pwd');

    if (roomId && password) {
        document.getElementById('roomId').value = roomId;
        document.getElementById('password').value = password;
    }
}
