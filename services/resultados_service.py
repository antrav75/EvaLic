# services/resultados_service.py
from models.dao import get_db
from models.resultados_data import insert_resultados_tecnicos, insert_resultados_economicos, fetch_informe
from services.licitacion_service import get_evaluadores_for_licitacion as fetch_evaluadores  # Assuming this exists

def generar_informe(app, licitacion_id):
    """Genera y devuelve el informe técnico y económico, sobrescribiendo resultados previos"""
    db = get_db(app)
    insert_resultados_tecnicos(db, licitacion_id)
    insert_resultados_economicos(db, licitacion_id)
    informe = fetch_informe(db, licitacion_id)
    evaluadores = fetch_evaluadores(db, licitacion_id)
    return [dict(r) for r in informe], [dict(u) for u in evaluadores]
