# services/evaluaciones_service.py

from flask import current_app
from models.evaluaciones_data import (
    fetch_licitaciones_by_evaluator, fetch_evaluaciones, save_evaluacion, guardar_o_actualizar_evaluacion_economica
)
from models.dao import get_db,log_event,get_username_by_id

# Función: listar_por_evaluador
# Parámetros:
#   evaluador_id (entero): Descripción del parámetro evaluador_id.
# Descripción: Esta función obtiene la lista de datos de las licitaciones en las que
#              participa un usuario con un rol de evaluador.
# Retorna: lista con los datos de licitciones 
def listar_por_evaluador( evaluador_id):
    db = get_db(current_app)
    # Devuelve lista de diccionarios con los campos de licitaciones
    return fetch_licitaciones_by_evaluator(db, evaluador_id)

# Función: obtener_evaluaciones
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que se quieren obtener sus evaluaciones.
#   usuario_id (entero): Usuario con rol evaluador que realizar la evaluación
# Descripción: Esta función obtiene de las funciones de la capa de datos los datos correspondientes de las evaluaciones
#              de una licitación que ha realizado un usuario con un perfil de evaluador.
# Retorna: lista de datos de evaluaciones
def obtener_evaluaciones(licitacion_id, usuario_id):
    db = get_db(current_app)
    return fetch_evaluaciones(db, licitacion_id, usuario_id)


# Función: guardar_evaluacion
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que se quiere guardar su evaluación.
#   usuario_id (entero): Usuario con rol evaluador que guarda la evaluación
#   licitante_id (entero): Descripción de la empresa licitante de la que se evalua su oferta.
#   criterio_id (entero): Criterio (técnico o económico) evaluado.
#   puntuacion (entero): Puntuación que otorga el usuario con rol evaluador.
#   comentarios (desconocido): Comentarios para aclarar la puntuacion.
# Descripción: Esta función procesa y guarda los valores de una evaluación de un criterio que se ha realizado.
# Retorna: Ninguno
def guardar_evaluacion(licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios):
    db = get_db(current_app)
    
    # Se registra la evaluación guardada en el log
    nombre_usuario = get_username_by_id(db, usuario_id)
    log_event(db, nombre_usuario, 'guardar_evaluacion_tecnica', f'Licitación: {licitacion_id} + Criterio: {criterio_id} + Licitante: {licitante_id} + Puntuacion: {puntuacion}')
    
    # Guarda la evaluación en la base de datos usando una función de la capa de datos
    save_evaluacion(db, licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios)

# Función: guardar_o_actualizar_evaluacion_economica_logic
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que se quiere guardar su evaluación.
#   usuario_id (entero): Usuario con rol evaluador que guarda la evaluación
#   licitante_id (entero): Descripción de la empresa licitante de la que se evalua su oferta.
#   criterio_id (entero): Criterio (técnico o económico) evaluado.
#   puntuacion (entero): Puntuación que otorga el usuario con rol evaluador.
#   comentarios (desconocido): Comentarios para aclarar la puntuacion.
# Descripción: Esta función procesa y guarda o actualiza los valores de una evaluación de un criterio que se ha realizado.
# Retorna: Ninguno
def guardar_o_actualizar_evaluacion_economica_logic(licitacion_id, licitante_id,criterio_id,puntuacion,comentarios,usuario_id):

    db = get_db(current_app)
    
    # Registro de la actualización en el log
    nombre_usuario = get_username_by_id(db, usuario_id)
    log_event(db, nombre_usuario, 'guardar_evaluacion_economica', f'Licitación: {licitacion_id} + Criterio: {criterio_id} + Licitante: {licitante_id} + Puntuacion: {puntuacion}')

    # Guarda o actualiza la evaluación en la base de datos usando una función de la capa de datos
    return guardar_o_actualizar_evaluacion_economica(
        db,
        licitacion_id,
        licitante_id,
        criterio_id,
        puntuacion,
        comentarios,
        usuario_id
    )

