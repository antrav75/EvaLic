# models/etapas_data.py
from sqlite3 import Connection

def create_etapa(db: Connection, id_licitacion: int, id_fase: int, fecha_inicio: str, fecha_fin: str = None):
    """
    Inserta una nueva entrada en la tabla etapas.
    """
    db.execute(
        "INSERT INTO etapas (licitacion_id, fase_id, fecha_inicio, fecha_fin) VALUES (?,?,?,?)",
        (id_licitacion, id_fase, fecha_inicio, fecha_fin)
    )
    db.commit()

def get_current_etapa(db: Connection, id_licitacion: int) -> str:
    """
    Devuelve la descripción de la fase de la última entrada
    (por fecha_inicio) de la tabla etapas para la licitación dada.
    """
    cur = db.execute(
        """
        SELECT f.nombre
          FROM etapas e
          JOIN fases f ON e.fase_id = f.id
         WHERE e.licitacion_id = ?
         ORDER BY e.fecha_inicio DESC
         LIMIT 1
        """,
        (id_licitacion,)
    )
    row = cur.fetchone()
    return row['nombre'] if row else None


def delete_etapas_by_licitacion(db: Connection, id_licitacion: int):
    """
    Elimina todas las entradas de etapas asociadas a la licitación.
    """
    db.execute("DELETE FROM etapas WHERE licitacion_id=?", (id_licitacion,))
    db.commit()
