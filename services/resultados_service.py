# services/resultados_service.py
from models.dao import get_db
from models.resultados_data import insert_resultados_tecnicos, insert_resultados_economicos, fetch_informe
from services.licitacion_service import get_evaluadores_for_licitacion as fetch_evaluadores  # Assuming this exists

def generar_informe(app, licitacion_id):
    """Genera y devuelve el informe técnico y económico, sobrescribiendo resultados previos"""
    db = get_db(app)
    # Inserción de resultados técnicos y económicos
    insert_resultados_tecnicos(db, licitacion_id)
    insert_resultados_economicos(db, licitacion_id)
    # Obtención de todas las filas del informe
    informe = fetch_informe(db, licitacion_id)
    # Convertir filas a dicts
    rows = [dict(r) for r in informe]
    # Obtener evaluadores
    evaluadores = fetch_evaluadores(db, licitacion_id)

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
