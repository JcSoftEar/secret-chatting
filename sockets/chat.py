from flask_socketio import emit, join_room
from werkzeug.security import check_password_hash
from extensions import db, socketio
from models import Room, Message


@socketio.on('join')
def handle_join(data):
    room_id = data.get('room_id')
    password = data.get('password')
    username = data.get('username')

    if not room_id or not password or not username:
        emit('join_error', {'error': '房间号、密码和用户名不能为空'})
        return

    room = Room.query.get(room_id)
    if not room:
        emit('join_error', {'error': '房间不存在'})
        return

    if room.password != password:
        emit('join_error', {'error': '密码错误'})
        return

    join_room(room_id)

    join_msg = Message(
        room_id=room_id,
        sender_name='系统',
        content=f'{username} 加入了房间'
    )
    db.session.add(join_msg)
    db.session.commit()

    join_msg_data = {
        'id': join_msg.id,
        'room_id': join_msg.room_id,
        'sender_name': join_msg.sender_name,
        'content': join_msg.content,
        'timestamp': join_msg.timestamp.isoformat()
    }
    emit('new_msg', join_msg_data, room=room_id)
    emit('admin_new_msg', join_msg_data, room='admin_room')

    emit('join_success', {'room_id': room_id, 'room_name': room.name})


@socketio.on('send_msg')
def handle_send_msg(data):
    room_id = data.get('room_id')
    sender_name = data.get('sender_name')
    content = data.get('content')

    if not room_id or not sender_name or not content:
        emit('msg_error', {'error': '缺少必要参数'})
        return

    room = Room.query.get(room_id)
    if not room:
        emit('msg_error', {'error': '房间不存在'})
        return

    message = Message(
        room_id=room_id,
        sender_name=sender_name,
        content=content
    )
    db.session.add(message)
    db.session.commit()

    msg_data = {
        'id': message.id,
        'room_id': message.room_id,
        'sender_name': message.sender_name,
        'content': message.content,
        'timestamp': message.timestamp.isoformat()
    }

    emit('new_msg', msg_data, room=room_id)
    emit('admin_new_msg', msg_data, room='admin_room')
