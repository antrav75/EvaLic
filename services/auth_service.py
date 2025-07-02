from flask import current_app
from werkzeug.security import check_password_hash
from models.dao import get_user_by_username, log_event,get_db

# Función: authenticate
# Parámetros:
#   username (desconocido): Descripción del parámetro username.
#   password (desconocido): Descripción del parámetro password.
# Descripción: Breve descripción de lo que hace la función authenticate.
# Retorna: desconocido - Descripción del valor devuelto.
def authenticate(username, password):
    db = get_db(current_app)
    user = get_user_by_username(db, username)
    if user and not user['active']:
        log_event(db, username,'login_inactive',None)
        return None
    ok = user and check_password_hash(user['password'], password)
    event = 'login_success' if ok else 'login_failure'
    log_event(db, username, event, None)
    return user if ok else None

# Función: logout
# Parámetros:
#   session (desconocido): Descripción del parámetro session.
# Descripción: Breve descripción de lo que hace la función logout.
# Retorna: desconocido - Descripción del valor devuelto.
def logout( session):
    db = get_db(current_app)
    if 'user_id' in session:
        log_event(
            db, session['username'],
            'logout', None
        )
    session.clear()
