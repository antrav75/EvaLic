from werkzeug.security import generate_password_hash
from models.dao import (
    fetch_users, get_roles, get_role_id,
    add_user, update_user, delete_user, log_event
)

def list_users(db, search, role_id, page):
    users, total, pages = fetch_users(db, search, role_id, page)
    roles = get_roles(db)
    return {
        'users': users,
        'roles': roles,
        'total': total,
        'pages': pages
    }

def create_user(db, session, username, email, password, role_id, active=True):
    if ' ' in username:
        raise ValueError("El nombre de usuario no debe contener espacios")
    pwd_hash = generate_password_hash(password)
    new_id = add_user(db, username, email, pwd_hash, role_id, active)
    log_event(db, session['username'], session['user_id'],
              'create_user', username, new_id, 1)

def edit_user(db, session, user_id, username, email, password, role_id, active):
    if ' ' in username:
        raise ValueError("El nombre de usuario no debe contener espacios")
    pwd_hash = generate_password_hash(password) if password else None
    update_user(db, user_id, username, email, pwd_hash, role_id, active)
    log_event(db, session['username'], session['user_id'],
              'edit_user', username, user_id, 1)

def remove_user(db, session, user_id):
    user = db.execute("SELECT username FROM users WHERE id=?", (user_id,)).fetchone()
    if user:
        delete_user(db, user_id)
        log_event(db, session['username'], session['user_id'],
                  'delete_user', user['username'], user_id, 1)
