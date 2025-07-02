# services/licitacion_service.py
from flask import current_app
from models.licitaciones_data import (
    list_licitaciones as data_list,
    get_licitacion as data_get,
    create_licitacion as data_create,
    edit_licitacion as data_update,
    remove_licitacion as data_delete
)
from models.stage_data import create_stage, delete_stages_by_tender
from services.stage_service import get_current_stage_name
from models.licitaciones_data import fetch_licitacion_by_id
from models.dao import get_db,get_formulas,get_username_by_id,log_event

# Función: list_licitaciones
# Parámetros: Ninguno
# Descripción: Breve descripción de lo que hace la función list_licitaciones.
# Retorna: desconocido - Descripción del valor devuelto.
def list_licitaciones():
    db = get_db(current_app)
    return data_list(db)

# Función: get_licitacion
# Parámetros:
#   lic_id (desconocido): Descripción del parámetro lic_id.
# Descripción: Breve descripción de lo que hace la función get_licitacion.
# Retorna: desconocido - Descripción del valor devuelto.
def get_licitacion(lic_id):
    db = get_db(current_app)
    return data_get(db, lic_id)

# Función: create_licitacion
# Parámetros:
#   external_id (desconocido): Descripción del parámetro external_id.
#   title (desconocido): Descripción del parámetro title.
#   description (desconocido): Descripción del parámetro description.
#   fecha_inicio (desconocido): Descripción del parámetro fecha_inicio.
#   fecha_adjudicacion (desconocido): Descripción del parámetro fecha_adjudicacion.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Breve descripción de lo que hace la función create_licitacion.
# Retorna: desconocido - Descripción del valor devuelto.
def create_licitacion( external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id):
    db = get_db(current_app)

    if not title:
        raise ValueError("El título es obligatorio")
    if not fecha_inicio:
        raise ValueError("La fecha de inicio es obligatorio")
    # 1) Crear la licitación y obtener su ID
    lic_id = data_create(db, external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id)
    # 2) Crear la etapa inicial (fase "Borrador", id=1)
    create_stage(db, lic_id, 1, fecha_inicio)
    # 3) Crear registro en el log de licitación creada
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"crear_licitacion",f'Id: {lic_id} External_ID: {external_id} Titulo: {title}')

    return lic_id

# Función: edit_licitacion
# Parámetros:
#   lic_id (desconocido): Descripción del parámetro lic_id.
#   external_id (desconocido): Descripción del parámetro external_id.
#   title (desconocido): Descripción del parámetro title.
#   description (desconocido): Descripción del parámetro description.
#   fecha_inicio (desconocido): Descripción del parámetro fecha_inicio.
#   fecha_adjudicacion (desconocido): Descripción del parámetro fecha_adjudicacion.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Breve descripción de lo que hace la función edit_licitacion.
# Retorna: desconocido - Descripción del valor devuelto.
def edit_licitacion( lic_id, external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id):
    db = get_db(current_app)

    # Actualiza la licitación
    data_update(db, lic_id, external_id, title, description, fecha_inicio, fecha_adjudicacion)

    # Crear registro en el log de licitación editada
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"editar_licitacion",f'Id: {lic_id} External_ID: {external_id} Titulo: {title}')

# Función: remove_licitacion
# Parámetros:
#   lic_id (desconocido): Descripción del parámetro lic_id.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Breve descripción de lo que hace la función remove_licitacion.
# Retorna: desconocido - Descripción del valor devuelto.
def remove_licitacion( lic_id, user_id):
    db = get_db(current_app)

    """
    Elimina una licitación solo si está en estado Borrador, 
    borrando primero sus etapas y luego la licitación.
    """
    lic = data_get(db, lic_id)
    if not lic:
        raise ValueError("Licitación no encontrada")
    # Verifica permiso del usuario
    if lic['user_id'] != user_id:
        raise PermissionError("No tienes permiso para eliminar esta licitación")
    current_stage = get_current_stage_name(lic_id)
    if current_stage != 'Borrador':
        raise ValueError("Solo se pueden eliminar licitaciones en estado Borrador")
    # Borrar etapas asociadas
    delete_stages_by_tender(db, lic_id)
    # Borrar la licitación
    data_delete(db, lic_id)
    # Crear registro en el log de licitación borrada
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"borrar_licitacion",f'Id: {lic_id}')

# Funciones para evaluadores de licitaciones
from models.licitaciones_evaluadores_data import (
    list_evaluadores, list_evaluadores_by_licitacion, assign_evaluadores as _assign_evaluadores
)

# Función: list_evaluadores_logic
# Parámetros: Ninguno
# Descripción: Breve descripción de lo que hace la función list_evaluadores_logic.
# Retorna: desconocido - Descripción del valor devuelto.
def list_evaluadores_logic():
    db = get_db(current_app)
    return list_evaluadores(db)

# Función: get_evaluadores_for_licitacion
# Parámetros:
#   lic_id (desconocido): Descripción del parámetro lic_id.
# Descripción: Breve descripción de lo que hace la función get_evaluadores_for_licitacion.
# Retorna: desconocido - Descripción del valor devuelto.
def get_evaluadores_for_licitacion( lic_id):
    db = get_db(current_app)
    return list_evaluadores_by_licitacion(db, lic_id)

# Función: assign_evaluadores
# Parámetros:
#   lic_id (desconocido): Descripción del parámetro lic_id.
#   user_ids (desconocido): Descripción del parámetro user_ids.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Breve descripción de lo que hace la función assign_evaluadores.
# Retorna: desconocido - Descripción del valor devuelto.
def assign_evaluadores( lic_id, user_ids,user_id):
    db = get_db(current_app)
    nombre_usuario=get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"asignar_evaluadores",f'evaluadores_id: {user_ids}')
    return _assign_evaluadores(db, lic_id, user_ids)

# Función: obtener_licitacion_por_id
# Parámetros:
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
# Descripción: Breve descripción de lo que hace la función obtener_licitacion_por_id.
# Retorna: desconocido - Descripción del valor devuelto.
def obtener_licitacion_por_id(licitacion_id):
    """Devuelve la licitación como dict"""
    db = get_db(current_app)
    row = fetch_licitacion_by_id(db, licitacion_id)
    return dict(row) if row else None

# Función: get_formulas_logic
# Parámetros: Ninguno
# Descripción: Breve descripción de lo que hace la función get_formulas_logic.
# Retorna: desconocido - Descripción del valor devuelto.
def get_formulas_logic():
    """Devuelve las fórmulas de evaluación disponibles"""
    db = get_db(current_app)

    return get_formulas(db)
