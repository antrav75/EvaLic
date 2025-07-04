#services/oferta_service.py

from flask import current_app
from models.ofertas_data import list_ofertas, get_oferta, create_oferta, edit_oferta, remove_oferta, list_ofertas_admitidas
from models.dao import get_db, get_username_by_id, log_event
from models.dao import list_ofertas_by_licitacion, update_admitidasobre1

# Función: list_ofertas_logic
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que queremos obtener los datos de las ofertas.
# Descripción: Esta función obtiene los datos de las ofertas de la licitación cuyo identificador coincide
#              con el parametro de la función.
# Retorna: Lista  de ofertas.
def list_ofertas_logic(licitacion_id=None):
    db = get_db(current_app)
    return list_ofertas(db, licitacion_id)

# Función: list_ofertas_admitidas_logic
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que queremos obtener los datos de las ofertas.
# Descripción: Esta función obtiene los datos de las ofertas admitidas en la fase Sobre1 y que cuyo identificador
#              de la licitación con el parametro de la función.
# Retorna: Lista  de ofertas admitidas en la fase Sobre1.
def list_ofertas_admitidas_logic(licitacion_id=None):
    db = get_db(current_app)
    return list_ofertas_admitidas(db, licitacion_id)

# Función: get_oferta_logic
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que se quieren obtener los datos de la oferta.
#   licitante_id (desconocido): Identificador de la empresa licitante de la que se quieren obtener los datos de la oferta
# Descripción: Esta función obtiene los datos de la oferta sabiendo el identificador de la licitación y el identificador
#              de la empresa que ha realizado la ofeta.
# Retorna: Lista con datos de la oferta.
def get_oferta_logic( licitacion_id, licitante_id):
    db = get_db(current_app)
    return get_oferta(db, licitacion_id, licitante_id)

# Función: create_oferta_logic
# Parámetros:
#   data (lista): Datos de la oferta a crear.
#   user_id (entero): Usuario con rol resposable que crea la oferta.
# Descripción: Con esta función se crea la oferta con los datos que ha introducido el usuario en el formulario.
#              Se registra en el log que usuario creó la oferta.
# Retorna: Ninguno
def create_oferta_logic( data, user_id):
    db = get_db(current_app)

    # Crear entrada en el log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"crear_oferta",f'Licitacion_id: {data['licitacion_id']} + Licitante_id {data['licitante_id']} + fecha: {data['fechapresentacion']}')
    
    # Obtener datos con función de la capa de datos
    return create_oferta(
        db,
        data['licitacion_id'],
        data['licitante_id'],
        data['fechapresentacion']
    )

# Función: edit_oferta_logic
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que se quieren editar los datos de la oferta.
#   licitante_id_old (entero): Identificador de la empresa licitante (antigua) asociada a la oferta.
#   data (lista): Lista conteniendo los datos de la oferta a actualizar/modificar.
#   user_id (desconocido): Identificador con rol usuario con rol responsable que realiza la actualización de los datos.
# Descripción: Esta función realiza la actualización/modificación de los datos que indica el usuario desde el formulario.
#              Además registra esta modificación en el log.
# Retorna: Lista con los datos de la oferta actualizada/ modificada
def edit_oferta_logic(licitacion_id, licitante_id_old, data, user_id):
    db = get_db(current_app)

    # Crear entrada en el log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"editar_oferta",f'Licitacion_id: {data['licitacion_id']} + Licitante_id {data['licitante_id']} + fecha: {data['fechapresentacion']}')

    # Llama a la función de la capa de datos correspondiente para editar los datos
    return edit_oferta(db, licitacion_id, licitante_id_old, data['licitante_id'], data['fechapresentacion'])

# Función: remove_oferta_logic
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación que se quiere eliminar.
#   licitante_id (entero): Identificador de la empresa licitante asociada a la oferta.
#   user_id (desconocido): Identificador con rol usuario con rol responsable que realiza la actualización de los datos.
# Descripción: Esta función implementa la lógica en la capa de datos para eliminar una oferta presentada a una licitación
#              por una empresa.
# Retorna: Lista con datos de la oferta eliminada.
def remove_oferta_logic( licitacion_id, licitante_id, user_id):
    db = get_db(current_app)

    # Crear entrada en el log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"eliminar_oferta",f'Licitacion_id: {licitacion_id} + Licitante_id {licitante_id}')

    #Utiliza la función de la capa de datos para eliminar la oferta de la tabla.
    return remove_oferta(db, licitacion_id, licitante_id)


# Función: evaluate_sobre1_logic
# Parámetros:
#   licitacion_id (entero):  Identificador de la licitación de la que se evalua su admision en la fase Sobre1.
#   evaluaciones (lista): Evaluaciones realizadas.
#   user_id (desconocido): Descripción del parámetro user_id.
# Descripción: Esta función comprueba y actualiza si las ofertas han sido admitidas en la fase Sobre1.
# Retorna: Ninguna
def evaluate_sobre1_logic( licitacion_id, evaluaciones, user_id):
    db = get_db(current_app)
    """Evaluar ofertas de Sobre1 y marcar admitidasobre1"""
    for licitante_id, admitido in evaluaciones.items():
        val = 1 if admitido else 0

        # Crear entrada en el log
        nombre_usuario = get_username_by_id(db,user_id)
        log_event(db,nombre_usuario,"evaluar_ofertas_sobre1",f'Licitacion_id: {licitacion_id} + Licitante_id {licitante_id}')
        
        # Se actualizan los datos en la tabla con la función de la capa de datos
        update_admitidasobre1(db, licitacion_id, licitante_id, val)


