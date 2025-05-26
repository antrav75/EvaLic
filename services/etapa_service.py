# services/etapa_service.py
from models.etapas_data import get_current_etapa, create_etapa as data_create_etapa
from models.dao import get_db
from datetime import datetime

def get_current_stage(db, lic_id):
    """Devuelve la fase actual de la licitación"""
    return get_current_etapa(db, lic_id)

def advance_etapa(db, lic_id, fecha_avance):
    """
    Avanza la licitación a la siguiente fase.
    Valida que la fecha_avance sea posterior a fecha_inicio de la etapa actual,
    actualiza fecha_fin de la etapa actual y crea la nueva etapa.
    Devuelve el nombre de la nueva fase.
    """
    # Obtener fecha_inicio de la etapa actual
    row_current = db.execute(
        "SELECT fecha_inicio FROM etapas WHERE licitacion_id=? AND fecha_fin IS NULL",
        (lic_id,)
    ).fetchone()
    if not row_current or not row_current['fecha_inicio']:
        raise ValueError("No existe etapa actual o fecha de inicio inválida")
    # Parsear fechas
    fmt = "%Y-%m-%d"
    inicio = datetime.strptime(row_current['fecha_inicio'], fmt).date()
    avance = datetime.strptime(fecha_avance, fmt).date()
    if avance <= inicio:
        raise ValueError("La fecha de avance debe ser posterior a la fecha de inicio de la etapa actual")
    # Obtener fase actual y siguiente
    current_name = get_current_etapa(db, lic_id)
    fases = ['Borrador','Iniciada','Sobre1','Sobre2','Sobre3','Evaluada','Cerrada']
    try:
        idx = fases.index(current_name)
        next_name = fases[idx+1]
    except (ValueError, IndexError):
        raise ValueError("No se puede avanzar de fase")
    # Obtener id de siguiente fase
    row = db.execute("SELECT id FROM fases WHERE nombre=?", (next_name,)).fetchone()
    if not row:
        raise ValueError("Fase no encontrada")
    fase_id = row['id']
    # Cerrar etapa actual
    db.execute(
        "UPDATE etapas SET fecha_fin=? WHERE licitacion_id=? AND fecha_fin IS NULL",
        (fecha_avance, lic_id)
    )
    db.commit()
    # Crear nueva etapa
    data_create_etapa(db, lic_id, fase_id, fecha_avance)
    return next_name
