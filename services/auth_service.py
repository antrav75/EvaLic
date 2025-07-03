from flask import current_app
from werkzeug.security import check_password_hash
from models.dao import get_user_by_username, log_event,get_db

# Función: authenticate
# Parámetros:
#   username (cadena): Nombre del usuario que quiere acceder al sistema.
#   password (cadena): Contraseña del usuario que quiere acceder al sistema.
# Descripción: Esta función se encarga de validar si el usuario y la contraseña introducidos
#              están definidos en el sistema, permitiendo el acceso si es así y denegandolo si
#              no se encuentra registrador.
# Retorna: indetificador del usuario (entero).
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
#   session (desconocido): Identificador de sesión del sistema.
# Descripción: Esta función se encarga de cerrar la sesión abierta en el sistema .
# Retorna: Ninguno.
def logout( session):
    db = get_db(current_app)
    if 'user_id' in session:
        log_event(
            db, session['username'],
            'logout', None
        )
    session.clear()
