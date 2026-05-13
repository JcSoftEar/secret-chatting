from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from config import Config
from models import db, Room, Message, Admin
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import os

socketio = SocketIO(cors_allowed_origins="*")

def is_db_initialized():
    try:
        return Admin.query.first() is not None
    except Exception:
        return False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_path.startswith('sqlite:////'):
        db_dir = os.path.dirname(db_path.replace('sqlite:////', '/'))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    elif db_path.startswith('sqlite:///'):
        db_dir = os.path.dirname(db_path.replace('sqlite:///', ''))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    
    db.init_app(app)
    socketio.init_app(app)
    
    @app.before_request
    def check_initialized():
        if request.path.startswith('/static') or request.path == '/setup':
            return None
        if not is_db_initialized():
            return redirect('/setup')
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/setup')
    def setup():
        if is_db_initialized():
            return redirect('/admin')
        return render_template('setup.html')
    
    @app.route('/setup', methods=['POST'])
    def create_admin():
        if is_db_initialized():
            return jsonify({'success': False, 'error': '系统已初始化'})
        
        db.create_all()
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': '请填写完整信息'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': '密码长度不能少于6位'})
        
        admin = Admin(username=username, password_hash=generate_password_hash(password))
        db.session.add(admin)
        db.session.commit()
        
        return jsonify({'success': True})
    
    @app.route('/admin')
    def admin():
        return render_template('admin.html')
    
    @app.route('/admin/login', methods=['POST'])
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
    
    @app.route('/admin/rooms', methods=['GET'])
    def get_rooms():
        rooms = Room.query.all()
        room_list = [{'room_id': room.room_id, 'name': room.name, 'password': room.password} for room in rooms]
        return jsonify({'success': True, 'rooms': room_list})
    
    @app.route('/admin/rooms', methods=['POST'])
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
    
    @app.route('/admin/rooms/<room_id>', methods=['DELETE'])
    def delete_room(room_id):
        room = Room.query.get(room_id)
        if not room:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        Message.query.filter_by(room_id=room_id).delete()
        db.session.delete(room)
        db.session.commit()
        
        return jsonify({'success': True})
    
    @app.route('/admin/rooms/<room_id>/messages', methods=['GET'])
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
    
    return app

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
    
    from werkzeug.security import check_password_hash
    if not check_password_hash(admin.password_hash, password):
        emit('admin_error', {'error': '密码错误'})
        return
    
    room = Room.query.get(room_id)
    if not room:
        emit('admin_error', {'error': '房间不存在'})
        return
    
    join_room(room_id)
    
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

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
