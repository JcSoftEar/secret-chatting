import os
from flask import Flask
from config import Config
from extensions import db, socketio


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

    from routes.main import main_bp
    from routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    import sockets.chat
    import sockets.admin

    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
