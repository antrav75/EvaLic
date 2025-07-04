#services/user_service.py

from flask import current_app
from werkzeug.security import generate_password_hash
from models.dao import (
    fetch_users, get_roles, get_db,
    add_user, update_user, delete_user, log_event,get_username_by_id,get_user_by_username
)

# Función: list_users
# Parámetros:
#   search (cadena): Parametro utilizado para la busqueda en el filtro.
#   role_id (desconocido): Identificador del rol de usuario.
#   page (integer): Parámetro page utilizado para la paginación .
# Descripción: Esta función devuelve los datos de los usuarios de la aplicación para que se muestren
# en la página principal de forma paginada (max.5 por página) y se permita el filtro de usuarios por 
# los datos.
# Retorna: lista de datos de lo usuarios paginada.
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
#   session (lista): Datos de la sesión del usuario actual.
#   username (cadena): Nombre de usuario a crear.
#   email (cadena): Correo electrónico del usuario a crear.
#   password (cadena): Contraseña del usuario a crear
#   role_id (entero): Identificador del rol asignado al nuevo usuario.
#   active (entero): Indica si el usuario está activo para hacer login o no.
# Descripción: Esta función se encarga de dar de alta a un usario en el sistema a partir
#              de los datos que el administrador haya introducido en el formulario
#              correspondiente. Convierte la contraseña en valor numérico hash
#              para que no se vea la contraseña almacenada. Por último se registra
#              en el log la creación del usuario.
# Retorna: Ninguno.
def create_user( session, username, email, password, role_id, active=True):
    db = get_db(current_app)

    if get_user_by_username(db, username) is None:
        if ' ' in username:
            raise ValueError("El nombre de usuario no debe contener espacios")
        pwd_hash = generate_password_hash(password)

        # Se accede a la función de la capa de datos que almacena el usuario en la tabla
        new_id = add_user(db, username, email, pwd_hash, role_id, active)
        
        # Se registra la creación del usuario en el log
        log_event(db, session['username'], 'create_user', username)
    else:
        raise ValueError("El nombre de usuario ya existe")
    
# Función: edit_user
# Parámetros:
#   session (lista): Datos de la sesión del usuario actual.
#   user_id(entero): Identificador del usuario a modificar.
#   username (cadena): Nombre de usuario a modificar.
#   email (cadena): Correo electrónico del usuario a modificar.
#   password (cadena): Contraseña del usuario a modificar
#   role_id (entero): Identificador del rol asignado al usuario.
#   active (entero): Indica si el usuario está activo para hacer login o no.
# Descripción: Esta función se encarga de modificar los datos de  un usario en el 
#              sistema a partir de los datos que el administrador haya introducido
#              en el formulario correspondiente. Además se registra
#              en el log la modificación del usuario.
# Retorna: Ninguno.
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
#   session (lista): Datos de la sesión del usuario actual.
#   user_id(entero): Identificador del usuario a borrar.
# Descripción: Esta función se utiliza para borrar un usuario del sistema.
# Retornar: Ninguno
def remove_user(session, user_id):
    db = get_db(current_app)

    username = get_username_by_id(db,user_id)
    delete_user(db, user_id)
    log_event(db, session['username'], 'delete_user', username)
