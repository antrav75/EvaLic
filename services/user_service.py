from flask import current_app
from werkzeug.security import generate_password_hash
from models.dao import (
    fetch_users, get_roles, get_db,
    add_user, update_user, delete_user, log_event,get_username_by_id,get_user_by_username
)

# Función: list_users
# Parámetros:
#   search (desconocido): Descripción del parámetro search.
#   role_id (desconocido): Descripción del parámetro role_id.
#   page (desconocido): Descripción del parámetro page.
# Descripción: Breve descripción de lo que hace la función list_users.
# Retorna: desconocido - Descripción del valor devuelto.
def list_users(search, role_id, page):
    db = get_db(current_app)
    users, total, pages = fetch_users(db, search, role_id, page)
    roles = get_roles(db)
    return {
        'users': users,
        'roles': roles,
        'total': total,
        'pages': pages
    }

# Función: create_user
# Parámetros:
#   session (desconocido): Descripción del parámetro session.
#   username (desconocido): Descripción del parámetro username.
#   email (desconocido): Descripción del parámetro email.
#   password (desconocido): Descripción del parámetro password.
#   role_id (desconocido): Descripción del parámetro role_id.
#   active (desconocido): Descripción del parámetro active.
# Descripción: Breve descripción de lo que hace la función create_user.
# Retorna: desconocido - Descripción del valor devuelto.
def create_user( session, username, email, password, role_id, active=True):
    db = get_db(current_app)

    if get_user_by_username(db, username) is None:
        if ' ' in username:
            raise ValueError("El nombre de usuario no debe contener espacios")
        pwd_hash = generate_password_hash(password)
        new_id = add_user(db, username, email, pwd_hash, role_id, active)
        log_event(db, session['username'], 'create_user', username)
    else:
        raise ValueError("El nombre de usuario ya existe")
    
# Función: edit_user
# Parámetros:
#   session (desconocido): Descripción del parámetro session.
#   user_id (desconocido): Descripción del parámetro user_id.
#   username (desconocido): Descripción del parámetro username.
#   email (desconocido): Descripción del parámetro email.
#   password (desconocido): Descripción del parámetro password.
#   role_id (desconocido): Descripción del parámetro role_id.
#   active (desconocido): Descripción del parámetro active.
# Descripción: Breve descripción de lo que hace la función edit_user.
# Retorna: desconocido - Descripción del valor devuelto.
def edit_user(session, user_id, username, email, password, role_id, active):
    db = get_db(current_app)

    if get_user_by_username(db, username) is None:
        if ' ' in username:
            raise ValueError("El nombre de usuario no debe contener espacios")
        pwd_hash = generate_password_hash(password) if password else None
        update_user(db, user_id, username, email, pwd_hash, role_id, active)
        log_event(db, session['username'], 'edit_user', username)
    else:
        raise ValueError("El nombre de usuario ya existe")
    
# Función: remove_user
# Parámetros:
#   session (desconocido): Descripción del parámetro session.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Breve descripción de lo que hace la función remove_user.
# Retorna: desconocido - Descripción del valor devuelto.
def remove_user(session, user_id):
    db = get_db(current_app)

    username = get_username_by_id(db,user_id)
    delete_user(db, user_id)
    log_event(db, session['username'], 'delete_user', username)
