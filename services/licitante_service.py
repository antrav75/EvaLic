from flask import current_app
from models.licitantes_data import list_licitantes, get_licitante, create_licitante, edit_licitante, remove_licitante,fetch_licitantes_por_licitacion
from models.dao import get_db,get_username_by_id,log_event

# Función: list_licitantes_logic
# Parámetros: Ninguno
# Descripción: Breve descripción de lo que hace la función list_licitantes_logic.
# Retorna: desconocido - Descripción del valor devuelto.
def list_licitantes_logic():
    db = get_db(current_app)
    return list_licitantes(db)

# Función: get_licitante_logic
# Parámetros:
#   licitante_id (desconocido): Descripción del parámetro licitante_id.
# Descripción: Breve descripción de lo que hace la función get_licitante_logic.
# Retorna: desconocido - Descripción del valor devuelto.
def get_licitante_logic( licitante_id):
    db = get_db(current_app)
    return get_licitante(db, licitante_id)

# Función: create_licitante_logic
# Parámetros:
#   data (desconocido): Descripción del parámetro data.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Breve descripción de lo que hace la función create_licitante_logic.
# Retorna: desconocido - Descripción del valor devuelto.
def create_licitante_logic(data,user_id):
    db = get_db(current_app)

    # Crear log
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
#   licitante_id (desconocido): Descripción del parámetro licitante_id.
#   data (desconocido): Descripción del parámetro data.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Breve descripción de lo que hace la función edit_licitante_logic.
# Retorna: desconocido - Descripción del valor devuelto.
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
#   licitante_id (desconocido): Descripción del parámetro licitante_id.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Breve descripción de lo que hace la función remove_licitante_logic.
# Retorna: desconocido - Descripción del valor devuelto.
def remove_licitante_logic(licitante_id,user_id):
    db = get_db(current_app)

    # Crear log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"borrar_licitante",f'ID: {licitante_id}')
    
    return remove_licitante(db, licitante_id)

# Función: listar_licitantes_por_licitacion
# Parámetros:
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
# Descripción: Breve descripción de lo que hace la función listar_licitantes_por_licitacion.
# Retorna: desconocido - Descripción del valor devuelto.
def listar_licitantes_por_licitacion(licitacion_id):
    """
    Servicio que devuelve solo los licitantes que han participado en
    la licitación indicada (tienen evaluaciones registradas).
    """
    db = get_db(current_app)
    return fetch_licitantes_por_licitacion(db, licitacion_id)
