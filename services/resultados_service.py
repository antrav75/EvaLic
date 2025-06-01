# services/resultados_service.py
from models.dao import get_db
from models.resultados_data import (
    insert_resultados_tecnicos,
    fetch_informe,
    fetch_evaluadores
)

def generar_informe(app, licitacion_id):
    """Genera y devuelve el informe técnico, sobrescribiendo resultados previos"""
    db = get_db(app)
    # Siempre sobrescribimos resultados antes de obtener el informe
    insert_resultados_tecnicos(db, licitacion_id)
    # Obtener datos del informe
    informe = fetch_informe(db, licitacion_id)
    evaluadores = fetch_evaluadores(db, licitacion_id)
    return [dict(r) for r in informe], [dict(u) for u in evaluadores]
