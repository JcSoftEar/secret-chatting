let socket = null;
let currentRoom = null;
let isLoggedIn = false;
let adminCredentials = null;

function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 3000);
}

function initLoginPage() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();

            if (!username || !password) {
                showError('loginError', '请填写完整信息');
                return;
            }

            try {
                const response = await fetch('/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                if (data.success) {
                    isLoggedIn = true;
                    adminCredentials = { username, password };
                    showAdminPage();
                } else {
                    showError('loginError', data.error);
                }
            } catch (error) {
                showError('loginError', '登录失败，请稍后重试');
            }
        });
}

async function showAdminPage() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('adminPage').style.display = 'flex';
    await loadRoomList();
    initSocket();
    initSettings();
}

async function loadRoomList() {
    try {
        const response = await fetch('/admin/rooms');
        const data = await response.json();
        if (data.success) {
            renderRoomList(data.rooms);
        }
    } catch (error) {
        console.error('加载房间列表失败', error);
    }
}

function renderRoomList(rooms) {
    const listEl = document.getElementById('roomList');
    listEl.innerHTML = '';

    rooms.forEach(room => {
        const item = document.createElement('div');
        item.className = 'room-item';
        item.dataset.roomId = room.room_id;
        item.innerHTML = `
            <div class="room-name">${room.name}</div>
            <div class="room-id">${room.room_id}</div>
        `;
        item.addEventListener('click', () => selectRoom(room));
        listEl.appendChild(item);
    });
}

function initSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}`;
    socket = io(url);
}

async function selectRoom(room) {
    document.querySelectorAll('.room-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.roomId === room.room_id) {
            item.classList.add('active');
        }
    });

    currentRoom = room;
    document.getElementById('currentRoomName').textContent = room.name;
    document.getElementById('selectedRoomId').textContent = room.room_id;
    document.getElementById('selectedRoomName').textContent = room.name;

    await loadRoomHistory(room.room_id);
    joinSocketRoom(room.room_id);
    showRoomSettings();
    generateQRCode(room);
    
    document.getElementById('messagesInput').style.display = 'flex';
    initMessageInput();
}

function generateQRCode(room) {
    const qrcodeEl = document.getElementById('qrcode');
    qrcodeEl.innerHTML = '';
    
    const baseUrl = window.location.origin;
    const link = `${baseUrl}/?room=${encodeURIComponent(room.room_id)}&pwd=${encodeURIComponent(room.password)}`;
    
    new QRCode(qrcodeEl, {
        text: link,
        width: 180,
        height: 180,
        colorDark: '#333333',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.M
    });
}

async function loadRoomHistory(roomId) {
    try {
        const response = await fetch(`/admin/rooms/${roomId}/messages`);
        const data = await response.json();
        if (data.success) {
            renderMessages(data.messages);
        }
    } catch (error) {
        console.error('加载历史消息失败', error);
    }
}

function renderMessages(messages) {
    const container = document.getElementById('messagesContent');
    container.innerHTML = '';

    messages.forEach(msg => {
        addMessageToView(msg);
    });

    container.scrollTop = container.scrollHeight;
}

function addMessageToView(data) {
    const container = document.getElementById('messagesContent');

    if (data.sender_name === '系统') {
        const systemDiv = document.createElement('div');
        systemDiv.className = 'system-message';
        systemDiv.textContent = data.content;
        container.appendChild(systemDiv);
        container.scrollTop = container.scrollHeight;
        return;
    }

    const isSelf = data.sender_name === '管理员';
    
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
    timestamp.textContent = `${time.getFullYear()}-${(time.getMonth() + 1).toString().padStart(2, '0')}-${time.getDate().toString().padStart(2, '0')} ${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`;

    contentDiv.appendChild(senderName);
    contentDiv.appendChild(bubble);
    contentDiv.appendChild(timestamp);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function joinSocketRoom(roomId) {
    if (!socket || !adminCredentials) return;

    socket.off('new_msg');

    socket.emit('admin_join', {
        username: adminCredentials.username,
        password: adminCredentials.password,
        room_id: roomId
    });

    socket.on('new_msg', (data) => {
        if (data.room_id === currentRoom.room_id) {
            addMessageToView(data);
        }
    });
}

function showRoomSettings() {
    document.getElementById('settingsPlaceholder').style.display = 'none';
    document.getElementById('roomSettings').style.display = 'block';
}

function initMessageInput() {
    const textarea = document.getElementById('adminMessageInput');
    const sendBtn = document.getElementById('adminSendBtn');
    
    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 84) + 'px';
        sendBtn.disabled = textarea.value.trim() === '';
    });
    
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendAdminMessage();
        }
    });
    
    sendBtn.addEventListener('click', sendAdminMessage);
}

function sendAdminMessage() {
    const textarea = document.getElementById('adminMessageInput');
    const content = textarea.value.trim();
    
    if (!content || !socket || !currentRoom) return;
    
    socket.emit('send_msg', {
        room_id: currentRoom.room_id,
        sender_name: '管理员',
        content: content
    });
    
    textarea.value = '';
    textarea.style.height = 'auto';
    document.getElementById('adminSendBtn').disabled = true;
}

function initSettings() {
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn.addEventListener('click', () => {
        location.reload();
    });

    const createRoomForm = document.getElementById('createRoomForm');
    createRoomForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const roomId = document.getElementById('newRoomId').value.trim();
        const roomName = document.getElementById('newRoomName').value.trim();
        const password = document.getElementById('newRoomPassword').value.trim();

        if (!roomId || !roomName || !password) {
            alert('请填写完整信息');
            return;
        }

        try {
            const response = await fetch('/admin/rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ room_id: roomId, name: roomName, password })
            });

            const data = await response.json();
            if (data.success) {
                alert('创建成功');
                createRoomForm.reset();
                loadRoomList();
            } else {
                alert(data.error);
            }
        } catch (error) {
            alert('创建失败，请稍后重试');
        }
    });

    const deleteRoomBtn = document.getElementById('deleteRoomBtn');
    deleteRoomBtn.addEventListener('click', async () => {
        if (!currentRoom) {
            alert('请先选择一个房间');
            return;
        }

        if (!confirm(`确定要删除房间 "${currentRoom.name}" 吗？此操作不可恢复。`)) {
            return;
        }

        try {
            const response = await fetch(`/admin/rooms/${currentRoom.room_id}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            if (data.success) {
                alert('删除成功');
                currentRoom = null;
                document.getElementById('currentRoomName').textContent = '请选择房间';
                document.getElementById('settingsPlaceholder').style.display = 'flex';
                document.getElementById('roomSettings').style.display = 'none';
                document.getElementById('messagesContent').innerHTML = '';
                document.getElementById('messagesInput').style.display = 'none';
                loadRoomList();
            } else {
                alert(data.error);
            }
        } catch (error) {
            alert('删除失败，请稍后重试');
        }
    });

    const copyLinkBtn = document.getElementById('copyLinkBtn');
    copyLinkBtn.addEventListener('click', async () => {
        if (!currentRoom) {
            alert('请先选择一个房间');
            return;
        }

        const baseUrl = window.location.origin;
        const link = `${baseUrl}/?room=${encodeURIComponent(currentRoom.room_id)}&pwd=${encodeURIComponent(currentRoom.password)}`;

        try {
            await navigator.clipboard.writeText(link);
            alert('邀请链接已复制到剪贴板');
        } catch (error) {
            const textarea = document.createElement('textarea');
            textarea.value = link;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            alert('邀请链接已复制到剪贴板');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initLoginPage();
});
