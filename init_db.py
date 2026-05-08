from werkzeug.security import generate_password_hash
from app import create_app
from models import db, Room, Admin

def init_test_data():
    app = create_app()
    
    with app.app_context():
        room1 = Room(
            room_id='room123',
            password='password123',
            name='测试聊天室1'
        )
        
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123')
        )
        
        existing_room = Room.query.get('room123')
        existing_admin = Admin.query.get('admin')
        
        if not existing_room:
            db.session.add(room1)
            print('创建测试房间: room123 / password123')
        
        if not existing_admin:
            db.session.add(admin)
            print('创建管理员: admin / admin123')
        
        db.session.commit()
        print('初始化完成!')

if __name__ == '__main__':
    init_test_data()
