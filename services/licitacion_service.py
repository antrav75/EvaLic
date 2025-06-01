# services/licitacion_service.py
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
from models.dao import get_db

def list_licitaciones(db):
    return data_list(db)

def get_licitacion(db, lic_id):
    return data_get(db, lic_id)

def create_licitacion(db, external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id):
    if not title:
        raise ValueError("El título es obligatorio")
    if not fecha_inicio:
        raise ValueError("La fecha de inicio es obligatorio")
    # 1) Crear la licitación y obtener su ID
    lic_id = data_create(db, external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id)
    # 2) Crear la etapa inicial (fase "Borrador", id=1)
    create_stage(db, lic_id, 1, fecha_inicio)
    return lic_id

def edit_licitacion(db, lic_id, external_id, title, description, fecha_inicio, fecha_adjudicacion):
    # Actualiza la licitación
    data_update(db, lic_id, external_id, title, description, fecha_inicio, fecha_adjudicacion)

def remove_licitacion(db, lic_id, user_id):
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
    current_stage = get_current_stage_name(db, lic_id)
    if current_stage != 'Borrador':
        raise ValueError("Solo se pueden eliminar licitaciones en estado Borrador")
    # Borrar etapas asociadas
    delete_stages_by_tender(db, lic_id)
    # Borrar la licitación
    data_delete(db, lic_id)


# Funciones para evaluadores de licitaciones
from models.licitaciones_evaluadores_data import (
    list_evaluadores, list_evaluadores_by_licitacion, assign_evaluadores as _assign_evaluadores
)

def list_evaluadores_logic(db):
    return list_evaluadores(db)

def get_evaluadores_for_licitacion(db, lic_id):
    return list_evaluadores_by_licitacion(db, lic_id)

def assign_evaluadores(db, lic_id, user_ids):
    return _assign_evaluadores(db, lic_id, user_ids)

def obtener_licitacion_por_id(app, licitacion_id):
    """Devuelve la licitación como dict"""
    db = get_db(app)
    row = fetch_licitacion_by_id(db, licitacion_id)
    return dict(row) if row else None

