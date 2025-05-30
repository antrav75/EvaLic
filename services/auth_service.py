from werkzeug.security import check_password_hash
from models.dao import get_user_by_username, log_event

def authenticate(db, username, password):
    user = get_user_by_username(db, username)
    if user and not user['active']:
        log_event(db, username, user['id'], 'login_inactive', success=0)
        return None
    ok = user and check_password_hash(user['password'], password)
    event = 'login_success' if ok else 'login_failure'
    log_event(db, username, user['id'] if user else None, event, success=1 if ok else 0)
    return user if ok else None

def logout(db, session):
    if 'user_id' in session:
        log_event(
            db, session['username'], session['user_id'],
            'logout', success=1
        )
    session.clear()
