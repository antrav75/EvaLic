from flask import current_app
from models.licitantes_data import list_licitantes, get_licitante, create_licitante, edit_licitante, remove_licitante,fetch_licitantes_por_licitacion
from models.dao import get_db

def list_licitantes_logic():
    db = get_db(current_app)
    return list_licitantes(db)

def get_licitante_logic( licitante_id):
    db = get_db(current_app)
    return get_licitante(db, licitante_id)

def create_licitante_logic(data):
    db = get_db(current_app)
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

def edit_licitante_logic(licitante_id, data):
    db = get_db(current_app)
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

def remove_licitante_logic(licitante_id):
    db = get_db(current_app)
    return remove_licitante(db, licitante_id)

def listar_licitantes_por_licitacion(licitacion_id):
    """
    Servicio que devuelve solo los licitantes que han participado en
    la licitación indicada (tienen evaluaciones registradas).
    """
    db = get_db(current_app)
    return fetch_licitantes_por_licitacion(db, licitacion_id)