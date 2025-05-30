from models.ofertas_data import list_ofertas, get_oferta, create_oferta, edit_oferta, remove_oferta
from models.dao import get_db
from models.dao import list_ofertas_by_licitacion, update_admitidasobre1
from models.ofertas_data import fetch_ofertas_by_licitacion

def list_ofertas_logic(app, licitacion_id=None):
    db = get_db(app)
    return list_ofertas(db, licitacion_id)

def get_oferta_logic(app, licitacion_id, licitante_id):
    db = get_db(app)
    return get_oferta(db, licitacion_id, licitante_id)

def create_oferta_logic(app, data):
    db = get_db(app)
    return create_oferta(
        db,
        data['licitacion_id'],
        data['licitante_id'],
        data['fechapresentacion']
    )

def edit_oferta_logic(app, licitacion_id, licitante_id_old, data):
    db = get_db(app)
    return edit_oferta(db, licitacion_id, licitante_id_old, data['licitante_id'], data['fechapresentacion'])

def remove_oferta_logic(app, licitacion_id, licitante_id):
    db = get_db(app)
    return remove_oferta(db, licitacion_id, licitante_id)


def evaluate_sobre1_logic(app, licitacion_id, evaluaciones):
    """Evaluar ofertas de Sobre1 y marcar admitidasobre1"""
    for licitante_id, admitido in evaluaciones.items():
        val = 1 if admitido else 0
        update_admitidasobre1(app, licitacion_id, licitante_id, val)

def listar_ofertas_por_licitacion(app, licitacion_id):
    """Devuelve lista de ofertas con nombre de licitante"""
    db = get_db(app)
    rows = fetch_ofertas_by_licitacion(db, licitacion_id)
    return [dict(r) for r in rows]
