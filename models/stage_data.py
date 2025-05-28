# models/stage_data.py

from sqlite3 import Connection

def create_stage(db: Connection, tender_id: int, phase_id: int, start_date: str, end_date: str = None):
    """Inserta una nueva etapa en la tabla ‘etapas’."""
    db.execute(
        "INSERT INTO etapas (licitacion_id, fase_id, fecha_inicio, fecha_fin) VALUES (?,?,?,?)",
        (tender_id, phase_id, start_date, end_date)
    )
    db.commit()

def get_latest_stage_name(db: Connection, tender_id: int) -> str:
    """Devuelve el nombre de la fase más reciente (por fecha_inicio) de una licitación."""
    cur = db.execute(
        """
        SELECT f.nombre
          FROM etapas e
          JOIN fases f ON e.fase_id = f.id
         WHERE e.licitacion_id = ?
         ORDER BY e.fecha_inicio DESC
         LIMIT 1
        """,
        (tender_id,)
    )
    row = cur.fetchone()
    return row["nombre"] if row else None

def get_current_stage(db: Connection, tender_id: int) -> dict:
    """
    Devuelve la fila de la etapa activa (fecha_fin IS NULL) para la licitación dada.
    Alias ‘identificador’ como ‘id’ para mantener coherencia.
    """
    cur = db.execute(
        "SELECT identificador AS id, fase_id, fecha_inicio AS start_date, fecha_fin AS end_date "
        "FROM etapas "
        "WHERE licitacion_id = ? AND fecha_fin IS NULL",
        (tender_id,)
    )
    row = cur.fetchone()
    return dict(row) if row else None

def update_stage_end_date(db: Connection, tender_id: int, end_date: str):
    """Marca como cerrada la etapa activa poniendo fecha_fin."""
    db.execute(
        "UPDATE etapas SET fecha_fin = ? WHERE licitacion_id = ? AND fecha_fin IS NULL",
        (end_date, tender_id)
    )
    db.commit()

def delete_stages_by_tender(db: Connection, tender_id: int):
    """Elimina todas las etapas asociadas a una licitación."""
    db.execute(
        "DELETE FROM etapas WHERE licitacion_id = ?",
        (tender_id,)
    )
    db.commit()

def get_all_phases(db: Connection) -> list:
    """
    Devuelve la lista de todas las fases del catálogo
    como dicts ordenados por su id: [{'id':…, 'name':…}, …].
    """
    cur = db.execute("SELECT id, nombre FROM fases ORDER BY id")
    return [{"id": row["id"], "name": row["nombre"]} for row in cur.fetchall()]

def get_phase_id_by_name(db: Connection, name: str) -> int:
    """Dado un nombre de fase, devuelve su id o None si no existe."""
    cur = db.execute("SELECT id FROM fases WHERE nombre = ?", (name,))
    row = cur.fetchone()
    return row["id"] if row else None