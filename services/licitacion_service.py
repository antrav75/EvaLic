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
# Descripción: Obtiene los datos de todas las licitaciones del sistema.
# Retorna: lista con los datos de todas las licitaciones
def list_licitaciones():
    db = get_db(current_app)
    return data_list(db)

# Función: get_licitacion
# Parámetros:
#   lic_id (entero): Identificador de licitación para buscar los datos.
# Descripción: Esta función busca los datos de una licitación concreta cuyo
#              identificador se ha proporcionado en el parámetro.
# Retorna: lista de datos de la licitación.
def get_licitacion(lic_id):
    db = get_db(current_app)
    return data_get(db, lic_id)

# Función: create_licitacion
# Parámetros:
#   external_id (cadena): Identificador externo de la licitación, por ejemplo de otro SI.
#   title (cadena): Título de la licitación
#   description (cadena): Descripción de la licitación. Por ejemplo aqui se incluye el objeto.
#   fecha_inicio (date): Fecha de inicio cuando se comienza a preparar la licitación.
#   fecha_adjudicacion (date): Fehaa de adjudicación o finalización de la licitación.
#   user_id (entero): Usuario responsable de la licitación.
# Descripción: La función licitación crea una licitación a partir de los datos introducidos en el formulario
#              por el usuario responsable.
# Retorna: Identificador de la licitación (entero)
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
#   lic_id (entero): Identificador de la licitación a modificar.
#   external_id (cadena): Identificador externo de la licitación, por ejemplo de otro SI.
#   title (cadena): Título de la licitación
#   description (cadena): Descripción de la licitación. Por ejemplo aqui se incluye el objeto.
#   fecha_inicio (date): Fecha de inicio cuando se comienza a preparar la licitación.
#   fecha_adjudicacion (date): Fehaa de adjudicación o finalización de la licitación.
#   user_id (entero): Usuario responsable de la licitación.
# Descripción: La función licitación edita una licitación a partir de los datos introducidos en el formulario
#              por el usuario responsable.
# Retorna: Ninguno
def edit_licitacion( lic_id, external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id):
    db = get_db(current_app)

    # Actualiza la licitación
    data_update(db, lic_id, external_id, title, description, fecha_inicio, fecha_adjudicacion)

    # Crear registro en el log de licitación editada
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"editar_licitacion",f'Id: {lic_id} External_ID: {external_id} Titulo: {title}')

# Función: remove_licitacion
# Parámetros:
#   lic_id (entero): Identificador de la licitación que queremos borrar.
#   user_id (entero): Identificador del usuario con rol reponsable que va a borrar la licitación.
# Descripción: Esta función elimina una icitación, siempre y cuando no haya pasado de la etapa
#              "Borrador".
# Retorna: Ninguno.
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
# Descripción: Esta función obtiene todos los usuarios con rol evaluador para mostrarla en la ventana
#              de selección evaluadores de una licitación.
# Retorna: lista de datos de evaluadores
def list_evaluadores_logic():
    db = get_db(current_app)
    return list_evaluadores(db)

# Función: get_evaluadores_for_licitacion
# Parámetros:
#   lic_id (entero): Identificador de la licitación que se está tramitando.
# Descripción: Esta función obtiene todos los usuarios con el rol evaluador para mostrarlos en la ventana
#              de evaluadores seleccionados para una licitación.
# Retorna: lista de identificadores asociados a la licitación.
def get_evaluadores_for_licitacion( lic_id):
    db = get_db(current_app)
    return list_evaluadores_by_licitacion(db, lic_id)

# Función: assign_evaluadores
# Parámetros:
#   lic_id (entero): Identificador de la licitación que se está tramitando.
#   user_ids (lista): Lista de identificadores de usuarios .
#   user_id (entero): Identificador del usuario que realiza el cambio.
# Descripción: Esta función se utiliza para asignar los evaluadores a una licitación dada. En 
#              este caso se registrará en el log el evento de asignar usuarios.
# Retorna: lista de datos de los usuarios asignados.
def assign_evaluadores( lic_id, user_ids,user_id):
    db = get_db(current_app)
    
    # Se guarda en el log quien asignó los evaluadores a una licitación
    nombre_usuario=get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"asignar_evaluadores",f'evaluadores_id: {user_ids}')
    
    # Se llama a la función de la capa de datos para asignar los usuarios
    return _assign_evaluadores(db, lic_id, user_ids)

# Función: obtener_licitacion_por_id
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que queremos obtener los datos.
# Descripción: Esta función obtiene los datos de una licitación a partir del identificador de la licitación
#              comunicada en el parámetro.
# Retorna: diccionario de datos de la licitación.
def obtener_licitacion_por_id(licitacion_id):
    """Devuelve la licitación como dict"""
    db = get_db(current_app)
    row = fetch_licitacion_by_id(db, licitacion_id)
    return dict(row) if row else None

# Función: get_formulas_logic
# Parámetros: Ninguno
# Descripción: Obtiene las fórmulas que se pueden aplicar a los criterios económicos de una licitación.
# Retorna: lista de formulas de.
def get_formulas_logic():
    """Devuelve las fórmulas de evaluación disponibles"""
    db = get_db(current_app)

    return get_formulas(db)
