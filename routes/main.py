from flask import Blueprint, render_template, request, jsonify, redirect
from werkzeug.security import generate_password_hash
from extensions import db
from models import Admin
from utils import is_db_initialized

main_bp = Blueprint('main', __name__)


@main_bp.before_app_request
def check_initialized():
    if request.path.startswith('/static') or request.path == '/setup':
        return None
    if not is_db_initialized():
        return redirect('/setup')


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/setup')
def setup():
    if is_db_initialized():
        return redirect('/admin')
    return render_template('setup.html')


@main_bp.route('/setup', methods=['POST'])
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
