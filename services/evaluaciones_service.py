from flask import current_app
# services/evaluaciones_service.py
from models.evaluaciones_data import (
    fetch_licitaciones_by_evaluator, fetch_evaluaciones, save_evaluacion, guardar_o_actualizar_evaluacion_economica
)
from models.dao import get_db,log_event,get_username_by_id

# Función: listar_por_evaluador
# Parámetros:
#   evaluador_id (desconocido): Descripción del parámetro evaluador_id.
# Descripción: Breve descripción de lo que hace la función listar_por_evaluador.
# Retorna: desconocido - Descripción del valor devuelto.
def listar_por_evaluador( evaluador_id):
    db = get_db(current_app)
    # Devuelve lista de diccionarios con los campos de licitaciones
    # print(dict(fetch_licitaciones_by_evaluator(db, evaluador_id)))
    return fetch_licitaciones_by_evaluator(db, evaluador_id)

# Función: obtener_evaluaciones
# Parámetros:
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
#   usuario_id (desconocido): Descripción del parámetro usuario_id.
# Descripción: Breve descripción de lo que hace la función obtener_evaluaciones.
# Retorna: desconocido - Descripción del valor devuelto.
def obtener_evaluaciones(licitacion_id, usuario_id):
    db = get_db(current_app)
    return fetch_evaluaciones(db, licitacion_id, usuario_id)


# Función: guardar_evaluacion
# Parámetros:
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
#   usuario_id (desconocido): Descripción del parámetro usuario_id.
#   licitante_id (desconocido): Descripción del parámetro licitante_id.
#   criterio_id (desconocido): Descripción del parámetro criterio_id.
#   puntuacion (desconocido): Descripción del parámetro puntuacion.
#   comentarios (desconocido): Descripción del parámetro comentarios.
# Descripción: Breve descripción de lo que hace la función guardar_evaluacion.
# Retorna: desconocido - Descripción del valor devuelto.
def guardar_evaluacion(licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios):
    db = get_db(current_app)
    nombre_usuario = get_username_by_id(db, usuario_id)
    log_event(db, nombre_usuario, 'guardar_evaluacion_tecnica', f'Licitación: {licitacion_id} + Criterio: {criterio_id} + Licitante: {licitante_id} + Puntuacion: {puntuacion}')
    # Guarda la evaluación en la base de datos
    save_evaluacion(db, licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios)

# Función: guardar_o_actualizar_evaluacion_economica_logic
# Parámetros:
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
#   lid (desconocido): Descripción del parámetro lid.
#   cid (desconocido): Descripción del parámetro cid.
#   puntuacion (desconocido): Descripción del parámetro puntuacion.
#   comentarios (desconocido): Descripción del parámetro comentarios.
#   usuario_id (desconocido): Descripción del parámetro usuario_id.
# Descripción: Breve descripción de lo que hace la función guardar_o_actualizar_evaluacion_economica_logic.
# Retorna: desconocido - Descripción del valor devuelto.
def guardar_o_actualizar_evaluacion_economica_logic(licitacion_id, lid,cid,puntuacion,comentarios,usuario_id):

    db = get_db(current_app)
    nombre_usuario = get_username_by_id(db, usuario_id)
    licitante_id = lid
    criterio_id = cid
    log_event(db, nombre_usuario, 'guardar_evaluacion_economica', f'Licitación: {licitacion_id} + Criterio: {criterio_id} + Licitante: {licitante_id} + Puntuacion: {puntuacion}')
    return guardar_o_actualizar_evaluacion_economica(
        db,
        licitacion_id,
        lid,
        cid,
        puntuacion,
        comentarios,
        usuario_id
    )

