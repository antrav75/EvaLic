# models/stage_data.py

from sqlite3 import Connection

# Función: create_stage
# Parámetros:
#   db (conexión): Nombre de la base de datos.
#   licitacion_id (entero): Identificador de la licitación que estamos tratando.
#   fase_id (entero): Identificador de la fase en la que se encuentra la licitación
#   fecha_inicio (date): Fecha de inicio de la etapa 
#   fecha_fin (date): Fecha fin de la etapa.
# Descripción: Esta función inserta en la tabla etapas una nueva etapa en una licitación dada.
#              Esta etapa puede ser Iniciada, Preparada, Sobre1, Sobre2, Sobre 3... La última
#              etapa marcará en que punto se encuentra actualmente la licitación.
# Retorna: Ninguno
def create_stage(db: Connection, licitacion_id: int, fase_id: int, fecha_inicio: str, fecha_fin: str = None):
    """Inserta una nueva etapa en la tabla ‘etapas’."""
    db.execute(
        "INSERT INTO etapas (licitacion_id, fase_id, fecha_inicio, fecha_fin) VALUES (?,?,?,?)",
        (licitacion_id, fase_id, fecha_inicio, fecha_fin)
    )
    db.commit()

# Función: get_latest_stage_name
# Parámetros:
#   db (conexión): Nombre de la base de datos.
#   licitacion_id (entero): Identificador de la licitación que estamos tratando.
# Descripción: Esta función obtiene la última etapa de una licitación, que marcará en que punto 
# se encuentra actualmente la licitación.
# Retorna: Nombre de la etapa(cadena)
def get_latest_stage_name(db: Connection, licitacion_id: int) -> str:
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
        (licitacion_id,)
    )
    row = cur.fetchone()
    return row["nombre"] if row else None

# Función: get_current_stage
# Parámetros:
#   db (conexión): Nombre de la base de datos.
#   licitacion_id (entero): Identificador de la licitación que estamos tratando.
# Descripción: Esta función obtiene la etapa  actual de una licitación, y devuelve
#              los datos de dicha etapa.
# Retorna: Diccionario con datos de la etapa
def get_current_stage(db: Connection, licitacion_id: int) -> dict:
    """
    Devuelve la fila de la etapa activa (fecha_fin IS NULL) para la licitación dada.
    Alias ‘identificador’ como ‘id’ para mantener coherencia.
    """
    cur = db.execute(
        "SELECT identificador AS id, fase_id, fecha_inicio AS start_date, fecha_fin AS end_date "
        "FROM etapas "
        "WHERE licitacion_id = ? AND fecha_fin IS NULL",
        (licitacion_id,)
    )
    row = cur.fetchone()
    return dict(row) if row else None

# Función: update_stage_end_date
# Parámetros:
#   db (conexión): Nombre de la conexión de la base de datos.
#   licitacion_id (entero): Identificador de la licitación que estamos tratando.
#   fecha_fin (date): Fecha fin de la etapa.
# Descripción: Esta función da por finalizada una etapa insertando la fecha indicada como fecha de fin
#              de etapa.
# Retorna: Ninguno
def update_stage_end_date(db: Connection, licitacion_id: int, fecha_fin: str):
    """Marca como cerrada la etapa activa poniendo fecha_fin."""
    db.execute(
        "UPDATE etapas SET fecha_fin = ? WHERE licitacion_id = ? AND fecha_fin IS NULL",
        (fecha_fin, licitacion_id)
    )
    db.commit()

# Función: delete_stages_by_tender
# Parámetros:
#   db (conexión): Nombre de la conexión de la base de datos.
#   licitacion_id (entero): Identificador de la licitación que estamos tratando.
#   fecha_fin (date): Fecha fin de la etapa.
# Descripción: Esta función borra una etapa (solo cuando está en etapa Borrador)
# Retorna: Ninguno
def delete_stages_by_tender(db: Connection, licitacion_id: int):
    """Elimina todas las etapas asociadas a una licitación."""
    db.execute(
        "DELETE FROM etapas WHERE licitacion_id = ?",
        (licitacion_id,)
    )
    db.commit()

# Función: get_all_phases
# Parámetros:
#   db (conexión): Nombre de la base de datos.
#   Descripción: Esta función obtiene los nombres de todas las fase para mostrarlas
#                como diccionarios.
# Retorna: Diccionario con todas las fases.
def get_all_phases(db: Connection) -> list:
    """
    Devuelve la lista de todas las fases del catálogo
    como dicts ordenados por su id: [{'id':…, 'name':…}, …].
    """
    cur = db.execute("SELECT id, nombre FROM fases ORDER BY id")
    return [{"id": row["id"], "name": row["nombre"]} for row in cur.fetchall()]

# Función: get_phase_id_by_name
# Parámetros:
#   db (conexión): Nombre de la base de datos.
#   Descripción: Esta función obtiene el identificador de la fase en función de su nombre
# Retorna: Identificador de la fase (entero)
def get_phase_id_by_name(db: Connection, name: str) -> int:
    """Dado un nombre de fase, devuelve su id o None si no existe."""
    cur = db.execute("SELECT id FROM fases WHERE nombre = ?", (name,))
    row = cur.fetchone()
    return row["id"] if row else None