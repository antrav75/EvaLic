from flask import current_app
# services/evaluaciones_service.py
from models.evaluaciones_data import (
    fetch_licitaciones_by_evaluator, fetch_evaluaciones, save_evaluacion, guardar_o_actualizar_evaluacion_economica
)
from models.dao import get_db

def listar_por_evaluador( evaluador_id):
    db = get_db(current_app)
    # Devuelve lista de diccionarios con los campos de licitaciones
    # print(dict(fetch_licitaciones_by_evaluator(db, evaluador_id)))
    return fetch_licitaciones_by_evaluator(db, evaluador_id)

def obtener_evaluaciones(licitacion_id, usuario_id):
    db = get_db(current_app)
    return fetch_evaluaciones(db, licitacion_id, usuario_id)


def guardar_evaluacion(licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios):
    db = get_db(current_app)
    save_evaluacion(db, licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios)

def guardar_o_actualizar_evaluacion_economica_logic(licitacion_id, lid,cid,puntuacion,comentarios,usuario_id):

    db = get_db(current_app)

    return guardar_o_actualizar_evaluacion_economica(
        db,
        licitacion_id,
        lid,
        cid,
        puntuacion,
        comentarios,
        usuario_id
    )

