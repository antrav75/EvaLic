from flask import current_app
from models.ofertas_data import list_ofertas, get_oferta, create_oferta, edit_oferta, remove_oferta, list_ofertas_admitidas
from models.dao import get_db, get_username_by_id, log_event
from models.dao import list_ofertas_by_licitacion, update_admitidasobre1

def list_ofertas_logic(licitacion_id=None):
    db = get_db(current_app)
    return list_ofertas(db, licitacion_id)

def list_ofertas_admitidas_logic(licitacion_id=None):
    db = get_db(current_app)
    return list_ofertas_admitidas(db, licitacion_id)

def get_oferta_logic( licitacion_id, licitante_id):
    db = get_db(current_app)
    return get_oferta(db, licitacion_id, licitante_id)

def create_oferta_logic( data, user_id):
    db = get_db(current_app)

    # Crear log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"crear_oferta",f'Licitacion_id: {data['licitacion_id']} + Licitante_id {data['licitante_id']} + fecha: {data['fechapresentacion']}')
    return create_oferta(
        db,
        data['licitacion_id'],
        data['licitante_id'],
        data['fechapresentacion']
    )

def edit_oferta_logic(licitacion_id, licitante_id_old, data, user_id):
    db = get_db(current_app)

    # Crear log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"editar_oferta",f'Licitacion_id: {data['licitacion_id']} + Licitante_id {data['licitante_id']} + fecha: {data['fechapresentacion']}')

    return edit_oferta(db, licitacion_id, licitante_id_old, data['licitante_id'], data['fechapresentacion'])

def remove_oferta_logic( licitacion_id, licitante_id, user_id):
    db = get_db(current_app)

    # Crear log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"eliminar_oferta",f'Licitacion_id: {licitacion_id} + Licitante_id {licitante_id}')
    return remove_oferta(db, licitacion_id, licitante_id)


def evaluate_sobre1_logic( licitacion_id, evaluaciones, user_id):
    db = get_db(current_app)
    """Evaluar ofertas de Sobre1 y marcar admitidasobre1"""
    for licitante_id, admitido in evaluaciones.items():
        val = 1 if admitido else 0
            # Crear log
        nombre_usuario = get_username_by_id(db,user_id)
        log_event(db,nombre_usuario,"evaluar_ofertas_sobre1",f'Licitacion_id: {licitacion_id} + Licitante_id {licitante_id}')
        update_admitidasobre1(db, licitacion_id, licitante_id, val)


