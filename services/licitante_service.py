# services/licitante_service.py

from flask import current_app
from models.licitantes_data import list_licitantes, get_licitante, create_licitante, edit_licitante, remove_licitante,fetch_licitantes_por_licitacion
from models.dao import get_db,get_username_by_id,log_event

# Función: list_licitantes_logic
# Parámetros: Ninguno
# Descripción: Obtiene todos los datos de las empresas que pueden participar en una licitación.
# Retorna: lista de datos de las empresas que pueden participar en una licitación.
def list_licitantes_logic():
    db = get_db(current_app)
    return list_licitantes(db)

# Función: get_licitante_logic
# Parámetros:
#   licitante_id (entero): Identificador del licitante del qu queremos obtener los datos
# Descripción: Obtiene los datos de la empresa licitante que coincide con el valor del parámetro
#              de esta función.
# Retorna: lista de datos de la empresa licitante.
def get_licitante_logic( licitante_id):
    db = get_db(current_app)
    return get_licitante(db, licitante_id)

# Función: create_licitante_logic
# Parámetros:
#   data (lista): Datos de la empresa licitante que se va a dar de alta en el sistema.
#   user_id (entero): Usuario que realiza la introducción de los datos del licitante en el sistema.
# Descripción: Esta función da de alta en el sistema a la empresa licitante cuyos datos ha introducido
#              un usuario. Esta creación además se registrará en el log de actividades.
# Retorna: Datos de la empresa licitante
def create_licitante_logic(data,user_id):
    db = get_db(current_app)

    # Crear entrada en el log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"crear_licitante",f'Nombre empresa: {data['nombreempresa']}')

    return create_licitante(
        db,
        data['nombreempresa'],
        data.get('cif'),
        data.get('direccion'),
        data.get('ciudad'),
        data.get('provincia'),
        data.get('telefono'),
        data.get('email')
    )

# Función: edit_licitante_logic
# Parámetros:
#   licitante_id(entero): identificador de la empresa licitante que queremos actualizar/modificar.
#   data (lista): Datos de la empresa licitante que se va a actualizar en el sistema.
#   user_id (entero): Identificador del usuario que realiza la actualización de los datos del licitante en el sistema.
# Descripción: Esta función da de alta en el sistema a la empresa licitante cuyos datos ha introducido
#              un usuario. Esta creación además se registrará en el log de actividades.
# Retorna: Datos de la empresa licitante
def edit_licitante_logic(licitante_id, data,user_id):
    db = get_db(current_app)
    
    # Crear log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"editar_licitante",f'ID: {licitante_id} Nombre empresa: {data['nombreempresa']}')

    return edit_licitante(
        db,
        licitante_id,
        data['nombreempresa'],
        data.get('cif'),
        data.get('direccion'),
        data.get('ciudad'),
        data.get('provincia'),
        data.get('telefono'),
        data.get('email')
    )

# Función: remove_licitante_logic
# Parámetros:
#   licitante_id(entero): identificador de la empresa licitante que queremos borrar.
#   user_id (entero): Identificador del usuario que realiza el borrado de los datos del licitante en el sistema.
# Descripción: Esta función da de alta en el sistema a la empresa licitante cuyos datos ha introducido
#              un usuario. Esta creación además se registrará en el log de actividades.
# Retorna: Datos de la empresa licitante
def remove_licitante_logic(licitante_id,user_id):
    db = get_db(current_app)

    # Crear log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"borrar_licitante",f'ID: {licitante_id}')
    
    return remove_licitante(db, licitante_id)

# Función: listar_licitantes_por_licitacion
# Parámetros: 
#   licitacion_id(entero):
# Descripción: Función que devuelve los licitantes que participan en una licitación determinada.
# Retorna: lista de datos de las empresas que participan en la licitación.
def listar_licitantes_por_licitacion(licitacion_id):
    """
    Servicio que devuelve solo los licitantes que han participado en
    la licitación indicada (tienen evaluaciones registradas).
    """
    db = get_db(current_app)
    return fetch_licitantes_por_licitacion(db, licitacion_id)
