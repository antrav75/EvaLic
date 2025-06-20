from flask import current_app
from models.criterios_data import (
    list_criterios, get_criterio, create_criterio,
    edit_criterio, delete_criterio,
    list_tipo_criterios, list_formulas
)
from models.criterios_data import fetch_criterios_tecnicos, fetch_criterios_economicos
from models.dao import get_db, log_event,get_username_by_id

def listar(lic_id):
    db = get_db(current_app)
    return list_criterios(db, lic_id)

def obtener(crit_id):
    db = get_db(current_app)
    return get_criterio(db, crit_id)

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

def borrar(licitacion_id,crit_id,usuario_id):
    db = get_db(current_app)

    nombre_usuario = get_username_by_id(db,usuario_id)
    log_event(db,nombre_usuario,"borrar_criterio",f'Licitación: {licitacion_id} + Criterio: {crit_id}')
    delete_criterio(db, crit_id)

def tipos():
    db = get_db(current_app)
    return list_tipo_criterios(db)

def formulas():
    db = get_db(current_app)
    return list_formulas(db)

def listar_tecnicos(licitacion_id):
    db = get_db(current_app)
    return fetch_criterios_tecnicos(db, licitacion_id)

def listar_economicos(licitacion_id):
    db = get_db(current_app)
    return fetch_criterios_economicos(db, licitacion_id)