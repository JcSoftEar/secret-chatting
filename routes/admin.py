from flask import Blueprint, render_template, request, jsonify
from werkzeug.security import check_password_hash
from extensions import db
from models import Room, Message, Admin

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('')
def admin_page():
    return render_template('admin.html')


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'error': '请填写完整信息'})

    admin = Admin.query.get(username)
    if not admin:
        return jsonify({'success': False, 'error': '管理员不存在'})

    if not check_password_hash(admin.password_hash, password):
        return jsonify({'success': False, 'error': '密码错误'})

    return jsonify({'success': True})


@admin_bp.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    room_list = [{'room_id': room.room_id, 'name': room.name, 'password': room.password} for room in rooms]
    return jsonify({'success': True, 'rooms': room_list})


@admin_bp.route('/rooms', methods=['POST'])
def create_room():
    data = request.get_json()
    room_id = data.get('room_id')
    name = data.get('name')
    password = data.get('password')

    if not room_id or not name or not password:
        return jsonify({'success': False, 'error': '请填写完整信息'})

    if Room.query.get(room_id):
        return jsonify({'success': False, 'error': '房间号已存在'})

    room = Room(room_id=room_id, name=name, password=password)
    db.session.add(room)
    db.session.commit()

    return jsonify({'success': True})


@admin_bp.route('/rooms/<room_id>', methods=['DELETE'])
def delete_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'success': False, 'error': '房间不存在'})

    Message.query.filter_by(room_id=room_id).delete()
    db.session.delete(room)
    db.session.commit()

    return jsonify({'success': True})


@admin_bp.route('/rooms/<room_id>/messages', methods=['GET'])
def get_room_messages(room_id):
    messages = Message.query.filter_by(room_id=room_id).order_by(Message.timestamp).all()
    msg_list = [
        {
            'id': msg.id,
            'room_id': msg.room_id,
            'sender_name': msg.sender_name,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        }
        for msg in messages
    ]
    return jsonify({'success': True, 'messages': msg_list})
