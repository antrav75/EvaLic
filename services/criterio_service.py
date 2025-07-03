from flask import current_app
from models.criterios_data import (
    list_criterios, get_criterio, create_criterio,
    edit_criterio, delete_criterio,
    list_tipo_criterios, list_formulas
)
from models.criterios_data import fetch_criterios_tecnicos, fetch_criterios_economicos
from models.dao import get_db, log_event,get_username_by_id

# Función: listar
# Parámetros:
#   lic_id (entero): Identificador de la licitación de la que se quiere obtener los datos de los criterios .
# Descripción: Esta función obtiene los datos de los criterios asociados a la licitación consultada.
# Retorna: lista de criterios de la licitación.
def listar(lic_id):
    db = get_db(current_app)
    return list_criterios(db, lic_id)

# Función: obtener
# Parámetros:
#   crit_id (entero): Identificador del criterio del que queremos obtener los datos.
# Descripción: Esta función obtiene los datos del criterio que tiene el identificador que coincide
#              el parámetro buscado.
# Retorna: lista de datos del criterio buscado
def obtener(crit_id):
    db = get_db(current_app)
    return get_criterio(db, crit_id)

# Función: crear
# Parámetros:
#   data (lista): Son los datos del criterio a crear.
#   usuario_id (entero): Identificador del usuario que crea el parámetro.
# Descripción: Esta función crea un criterio a partir de los datos introducidos
#              en el formulario correspondiente.
# Retorna: Ninguno
def crear( data, usuario_id):
    db = get_db(current_app)

    # Calculamos peso (0 si no se envía), fórmula (None si no aplica)
    # y precio base (None si no aplica)
    peso = int(data.get('Peso') or 0)
    tip_id = int(data['tipocriterio_id'])
    formula = int(data.get('formula_id')) if data.get('formula_id') else None
    precio_base = float(data.get('PrecioBase')) if data.get('PrecioBase') else None
    puntuacion_maxima = float(data.get('PuntuacionMaxima')) if data.get('PuntuacionMaxima') else None

    # Se registra la creación del criterio en el log
    nombre_usuario = get_username_by_id(db, usuario_id)
    log_event(db,nombre_usuario,"crear_criterio",f'Licitación: {int(data['licitacion_id'])} + Criterio: {data['NombreCriterio']}')
    
    #Se llama a la función de la capa de datos para almacenarlo en la tabla correspondiente
    create_criterio(
        db,
        data['NombreCriterio'],
        data.get('Descripcion'),
        peso,
        tip_id,
        int(data['licitacion_id']),
        formula,
        precio_base,
        puntuacion_maxima
    )

# Función: actualizar
# Parámetros:
#   crit_id (entero): Identificador del criterio del que queremos actualizar.
#   data (lista): Son los datos del criterio a crear.
#   usuario_id (entero): Identificador del usuario que actualiza el parámetro.
# Descripción: Esta función actualiza un criterio a partir de los datos introducidos en el 
#              formulario correspondiente.
# Retorna: Ninguno
def actualizar(crit_id, data, usuario_id):
    db = get_db(current_app)

    # Calculamos peso (0 si no se envía), fórmula (None si no aplica)
    # y precio base (None si no aplica)
    peso = int(data.get('Peso') or 0)
    tip_id = int(data['tipocriterio_id'])
    formula = int(data.get('formula_id')) if data.get('formula_id') else None
    precio_base = float(data.get('PrecioBase')) if data.get('PrecioBase') else None
    puntuacion_maxima = float(data.get('PuntuacionMaxima')) if data.get('PuntuacionMaxima') else None

    # Se registra en el log la modificación del criterio
    nombre_usuario = get_username_by_id(db,usuario_id)
    log_event(db,nombre_usuario,"editar_criterio",f'Licitación: {int(data['licitacion_id'])} + Criterio: {data['NombreCriterio']}')
    
    # Se modifica en la tabla correspondiente la edición del criterio
    edit_criterio(
        db,
        crit_id,
        data['NombreCriterio'],
        data.get('Descripcion'),
        peso,
        tip_id,
        formula,
        precio_base,
        puntuacion_maxima
    )

# Función: borrar
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que se quiere borrar un criterio. 
#   crit_id (entero): Identificador del criterio a borrar.
#   usuario_id (entero): Identificador del usuario que borra criterio.
# Descripción: Breve descripción de lo que hace la función borrar.
# Retorna: Ninguno
def borrar(licitacion_id,crit_id,usuario_id):
    db = get_db(current_app)

    # Se registra el borrado en el log
    nombre_usuario = get_username_by_id(db,usuario_id)
    log_event(db,nombre_usuario,"borrar_criterio",f'Licitación: {licitacion_id} + Criterio: {crit_id}')
    
    # Se llama a la función borrar criterio para borrar el criterio
    delete_criterio(db, crit_id)

# Función: tipos
# Parámetros: Ninguno
# Descripción: Obtiene la lista de los tipos de criterios 
# Retorna: lista de tipos de criterios
def tipos():
    db = get_db(current_app)
    return list_tipo_criterios(db)

# Función: formulas
# Parámetros: Ninguno
# Descripción: Obtiene la lista de las fórmulas económicas que se pueden utilizar para evaluar los criterios económicos 
# Retorna: lista de tipos de formulas
def formulas():
    db = get_db(current_app)
    return list_formulas(db)

# Función: listar_tecnicos
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que se quiere obtener los criterios técnicos.
# Descripción: Esta función obtiene los criterios técnicos que están asociados a la licitación 
#              cuyo identificador se ha pasado como parámetro.
# Retorna: lista de criterios técnicos.
def listar_tecnicos(licitacion_id):
    db = get_db(current_app)
    return fetch_criterios_tecnicos(db, licitacion_id)

# Función: listar_económicos
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la que se quiere obtener los criterios económicos.
# Descripción: Esta función obtiene los criterios económicos que están asociados a la licitación 
#              cuyo identificador se ha pasado como parámetro.
# Retorna: lista de criterios económicos.
def listar_economicos(licitacion_id):
    db = get_db(current_app)
    return fetch_criterios_economicos(db, licitacion_id)
