from models.evaluaciones_data import fetch_licitaciones_by_evaluator

def listar_por_evaluador(db, evaluador_id):
    # Devuelve lista de diccionarios con los campos de licitaciones
    return fetch_licitaciones_by_evaluator(db, evaluador_id)