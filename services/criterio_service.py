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
#   lic_id (desconocido): Descripción del parámetro lic_id.
# Descripción: Breve descripción de lo que hace la función listar.
# Retorna: desconocido - Descripción del valor devuelto.
def listar(lic_id):
    db = get_db(current_app)
    return list_criterios(db, lic_id)

# Función: obtener
# Parámetros:
#   crit_id (desconocido): Descripción del parámetro crit_id.
# Descripción: Breve descripción de lo que hace la función obtener.
# Retorna: desconocido - Descripción del valor devuelto.
def obtener(crit_id):
    db = get_db(current_app)
    return get_criterio(db, crit_id)

# Función: crear
# Parámetros:
#   data (desconocido): Descripción del parámetro data.
#   usuario_id (desconocido): Descripción del parámetro usuario_id.
# Descripción: Breve descripción de lo que hace la función crear.
# Retorna: desconocido - Descripción del valor devuelto.
def crear( data, usuario_id):
    db = get_db(current_app)

    # Calculamos peso (0 si no se envía), fórmula (None si no aplica)
    # y precio base (None si no aplica)
    peso = int(data.get('Peso') or 0)
    tip_id = int(data['tipocriterio_id'])
    formula = int(data.get('formula_id')) if data.get('formula_id') else None
    precio_base = float(data.get('PrecioBase')) if data.get('PrecioBase') else None
    puntuacion_maxima = float(data.get('PuntuacionMaxima')) if data.get('PuntuacionMaxima') else None

    nombre_usuario = get_username_by_id(db, usuario_id)
    log_event(db,nombre_usuario,"crear_criterio",f'Licitación: {int(data['licitacion_id'])} + Criterio: {data['NombreCriterio']}')
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
#   crit_id (desconocido): Descripción del parámetro crit_id.
#   data (desconocido): Descripción del parámetro data.
#   usuario_id (desconocido): Descripción del parámetro usuario_id.
# Descripción: Breve descripción de lo que hace la función actualizar.
# Retorna: desconocido - Descripción del valor devuelto.
def actualizar(crit_id, data, usuario_id):
    db = get_db(current_app)

    # Calculamos peso (0 si no se envía), fórmula (None si no aplica)
    # y precio base (None si no aplica)
    peso = int(data.get('Peso') or 0)
    tip_id = int(data['tipocriterio_id'])
    formula = int(data.get('formula_id')) if data.get('formula_id') else None
    precio_base = float(data.get('PrecioBase')) if data.get('PrecioBase') else None
    puntuacion_maxima = float(data.get('PuntuacionMaxima')) if data.get('PuntuacionMaxima') else None

    nombre_usuario = get_username_by_id(db,usuario_id)
    log_event(db,nombre_usuario,"editar_criterio",f'Licitación: {int(data['licitacion_id'])} + Criterio: {data['NombreCriterio']}')
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
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
#   crit_id (desconocido): Descripción del parámetro crit_id.
#   usuario_id (desconocido): Descripción del parámetro usuario_id.
# Descripción: Breve descripción de lo que hace la función borrar.
# Retorna: desconocido - Descripción del valor devuelto.
def borrar(licitacion_id,crit_id,usuario_id):
    db = get_db(current_app)

    nombre_usuario = get_username_by_id(db,usuario_id)
    log_event(db,nombre_usuario,"borrar_criterio",f'Licitación: {licitacion_id} + Criterio: {crit_id}')
    delete_criterio(db, crit_id)

# Función: tipos
# Parámetros: Ninguno
# Descripción: Breve descripción de lo que hace la función tipos.
# Retorna: desconocido - Descripción del valor devuelto.
def tipos():
    db = get_db(current_app)
    return list_tipo_criterios(db)

# Función: formulas
# Parámetros: Ninguno
# Descripción: Breve descripción de lo que hace la función formulas.
# Retorna: desconocido - Descripción del valor devuelto.
def formulas():
    db = get_db(current_app)
    return list_formulas(db)

# Función: listar_tecnicos
# Parámetros:
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
# Descripción: Breve descripción de lo que hace la función listar_tecnicos.
# Retorna: desconocido - Descripción del valor devuelto.
def listar_tecnicos(licitacion_id):
    db = get_db(current_app)
    return fetch_criterios_tecnicos(db, licitacion_id)

# Función: listar_economicos
# Parámetros:
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
# Descripción: Breve descripción de lo que hace la función listar_economicos.
# Retorna: desconocido - Descripción del valor devuelto.
def listar_economicos(licitacion_id):
    db = get_db(current_app)
    return fetch_criterios_economicos(db, licitacion_id)
