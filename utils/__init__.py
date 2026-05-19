from models import Admin

def is_db_initialized():
    try:
        return Admin.query.first() is not None
    except Exception:
        return False
