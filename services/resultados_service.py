# services/resultados_service.py

from flask import current_app
from models.dao import get_db
from models.resultados_data import insert_resultados_tecnicos, insert_resultados_economicos, fetch_informe
from services.licitacion_service import get_evaluadores_for_licitacion

# Función: generar_informe
# Parámetros:
#   licitacion_id (entero): Identificador de la licitación de la cual se va a generar el informe. 
# Descripción: Obtiene y elabora el informe que se va a presentar en pantalla con los resultados 
#              de las distintos sobres de una licitación (Sobre2- criterios técnicos y Sobre 3 - 
#              criterios económicos) obteniendo los resultados totales e indicando cuando una oferta
#              se puede considerar anormalmente baja.
# Retorna: lista con los datos del informe
def generar_informe(licitacion_id):
    """Genera y devuelve el informe técnico y económico, sobrescribiendo resultados previos"""
    db = get_db(current_app)
    # Inserción de resultados técnicos y económicos
    insert_resultados_tecnicos(db, licitacion_id)
    insert_resultados_economicos(db, licitacion_id)
    # Obtención de todas las filas del informe
    informe = fetch_informe(db, licitacion_id)
    # Convertir filas a dicts
    rows = [dict(r) for r in informe]
    # Obtener evaluadores
    evaluadores = get_evaluadores_for_licitacion(licitacion_id)

    #print(rows)
    
    # Calcular puntuaciones totales
    from collections import defaultdict
    totals = defaultdict(lambda: {'punt_tecnica': 0, 'punt_economica': 0})
    for row in rows:
        lid = row['licitante_id']
        p = row['puntuacionponderada'] if row['puntuacionponderada'] is not None else 0
        if row['tipo_criterio'] == 'Técnico':
            totals[lid]['punt_tecnica'] += p
        elif row['tipo_criterio'] == 'Económico':
            totals[lid]['punt_economica'] += p
    # Calcular puntacion global
    for lid, vals in totals.items():
        vals['total'] = vals['punt_tecnica'] + vals['punt_economica']

    return rows, [dict(u) for u in evaluadores], totals
