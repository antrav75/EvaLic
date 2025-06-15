from flask import current_app
from models.ofertas_data import list_ofertas, get_oferta, create_oferta, edit_oferta, remove_oferta, list_ofertas_admitidas
from models.dao import get_db
from models.dao import list_ofertas_by_licitacion, update_admitidasobre1

def list_ofertas_logic(licitacion_id=None):
    db = get_db(current_app)
    return list_ofertas(db, licitacion_id)

def list_ofertas_admitidas_logic(licitacion_id=None):
    db = get_db(current_app)
    return list_ofertas_admitidas(db, licitacion_id)

def get_oferta_logic(app, licitacion_id, licitante_id):
    db = get_db(app)
    return get_oferta(db, licitacion_id, licitante_id)

def create_oferta_logic( data):
    db = get_db(current_app)

    return create_oferta(
        db,
        data['licitacion_id'],
        data['licitante_id'],
        data['fechapresentacion']
    )

def edit_oferta_logic(licitacion_id, licitante_id_old, data):
    db = get_db(current_app)
    return edit_oferta(db, licitacion_id, licitante_id_old, data['licitante_id'], data['fechapresentacion'])

def remove_oferta_logic( licitacion_id, licitante_id):
    db = get_db(current_app)
    return remove_oferta(db, licitacion_id, licitante_id)


def evaluate_sobre1_logic( licitacion_id, evaluaciones):
    db = get_db(current_app)
    """Evaluar ofertas de Sobre1 y marcar admitidasobre1"""
    for licitante_id, admitido in evaluaciones.items():
        val = 1 if admitido else 0
        update_admitidasobre1(db, licitacion_id, licitante_id, val)


