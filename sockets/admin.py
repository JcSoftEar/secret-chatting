from flask_socketio import emit, join_room
from werkzeug.security import check_password_hash
from extensions import db, socketio
from models import Room, Message, Admin


@socketio.on('admin_connect')
def handle_admin_connect(data):
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return

    admin = Admin.query.get(username)
    if not admin:
        return

    if not check_password_hash(admin.password_hash, password):
        return

    join_room('admin_room')


@socketio.on('admin_join')
def handle_admin_join(data):
    username = data.get('username')
    password = data.get('password')
    room_id = data.get('room_id')

    if not username or not password or not room_id:
        emit('admin_error', {'error': '缺少必要参数'})
        return

    admin = Admin.query.get(username)
    if not admin:
        emit('admin_error', {'error': '管理员不存在'})
        return

    if not check_password_hash(admin.password_hash, password):
        emit('admin_error', {'error': '密码错误'})
        return

    room = Room.query.get(room_id)
    if not room:
        emit('admin_error', {'error': '房间不存在'})
        return

    join_room(room_id)
    join_room('admin_room')

    messages = Message.query.filter_by(room_id=room_id).order_by(Message.timestamp).all()
    history = [
        {
            'id': msg.id,
            'room_id': msg.room_id,
            'sender_name': msg.sender_name,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        }
        for msg in messages
    ]

    emit('admin_success', {'room_id': room_id, 'history': history})
