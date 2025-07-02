# services/stage_service.py

from flask import current_app
from models.dao import get_db,get_username_by_id,log_event
from models.stage_data import (
    get_current_stage,
    get_latest_stage_name,
    create_stage,
    update_stage_end_date,
    get_all_phases
)
from datetime import datetime

def get_current_stage_name( tender_id: int) -> str:
    """
    Devuelve el nombre de la fase actual para la licitación dada.
    """

    db = get_db(current_app)
    name = get_latest_stage_name(db, tender_id)
    if not name:
        raise ValueError(f"No se encontró ninguna fase para la licitación {tender_id}")
    return name

def advance_stage( tender_id: int, advance_date: str, user_id: int) -> str:
    """
    Avanza la licitación a la siguiente fase:
      1. Comprueba que la fecha de avance sea posterior a la de inicio.
      2. Obtiene la lista ordenada de fases desde la capa de datos.
      3. Determina la fase siguiente, cierra la actual y crea la nueva.
    Devuelve el nombre de la fase a la que se ha avanzado.
    """
    db = get_db(current_app)
    # 1) Obtener la etapa activa
    stage = get_current_stage(db,tender_id)

    if not stage or not stage.get("start_date"):
        raise ValueError(f"No hay ninguna etapa activa para la licitación {tender_id}")

    # 2) Validar fechas
    fmt = "%Y-%m-%d"
    start = datetime.strptime(stage["start_date"], fmt).date()
    adv   = datetime.strptime(advance_date, fmt).date()
    if adv <= start:
        raise ValueError(
            f"La fecha de avance ({advance_date}) debe ser posterior "
            f"a la fecha de inicio ({stage['start_date']})"
        )

    # 3) Cargar fases desde data layer
    phases = get_all_phases(db)
    if not phases:
        raise ValueError("No hay fases definidas en el catálogo")

    # 4) Buscar el índice de la fase actual en la lista
    current_name = get_latest_stage_name(db, tender_id)
    idx = next((i for i,p in enumerate(phases) if p["name"] == current_name), None)
    if idx is None or idx + 1 >= len(phases):
        raise ValueError(f"No se puede avanzar desde la fase '{current_name}'")

    next_phase = phases[idx + 1]

    # 5) Cerrar la etapa actual y abrir la nueva
    update_stage_end_date(db, tender_id, advance_date)
    create_stage(db, tender_id, next_phase["id"], advance_date)

    # 6) Crear log
    nombre_usuario = get_username_by_id(db,user_id)
    log_event(db,nombre_usuario,"avanzar_estado",f'Licitacion_id: {tender_id} + fase_actual: {stage["fase_id"]} + fase_proxima: {next_phase["id"]} + fecha: {advance_date}')

    return next_phase["name"]
