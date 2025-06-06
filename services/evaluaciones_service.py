# services/evaluaciones_service.py
from models.evaluaciones_data import (
    fetch_licitaciones_by_evaluator, fetch_evaluaciones, save_evaluacion
)
from models.dao import get_db

def listar_por_evaluador(db, evaluador_id):
    # Devuelve lista de diccionarios con los campos de licitaciones
    # print(dict(fetch_licitaciones_by_evaluator(db, evaluador_id)))
    return fetch_licitaciones_by_evaluator(db, evaluador_id)

def obtener_evaluaciones(app, licitacion_id, usuario_id):
    db = get_db(app)
    return fetch_evaluaciones(db, licitacion_id, usuario_id)


def guardar_evaluacion(app, licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios):
    db = get_db(app)
    save_evaluacion(db, licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios)