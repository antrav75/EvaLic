from models.dao import get_db

# Función: list_licitaciones
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
# Descripción: Obtiene todos los datos de la tabla licitaciones.
# Retorna: lista de licitaciones
def list_licitaciones(db):
    cur = db.execute("SELECT * FROM licitaciones ORDER BY id")
    return cur.fetchall()

# Función: get_licitacion
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   lic_id (entero): Identificado de la licitación que queremos obtener.
# Descripción: Busca una licitación que tenga el identificador especificado por lic_id
# Retorna: Todos los datos de la licitación
def get_licitacion(db, lic_id):
    cur = db.execute("SELECT * FROM licitaciones WHERE id=?", (lic_id,))
    return cur.fetchone()

# Función: create_licitacion
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   external_id (cadena): Identificador externo de la licitación, por ejemplo de otro SI.
#   title (cadena): Titulo de la licitación 
#   description (cadena): Descripción larga de la licitación.
#   fecha_inicio (date): Fecha de inicio de prepración de la licitación.
#   fecha_adjudicacion (date): Fecha fin, cuando se adjudica la licitación.
#   user_id (desconocido): Usuario con rol responsable que tramita la licitación.
# Descripción: Almacena en la tabla licitaciones los valores de una licitación dada por el identificador.
# Retorna: Los datos de la licitación
def create_licitacion(db, external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id):
    """
    Inserta una nueva licitación y devuelve su ID.
    """
    cur = db.execute(
        "INSERT INTO licitaciones (external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id) VALUES (?,?,?,?,?,?)",
        (external_id, title, description, fecha_inicio, fecha_adjudicacion, user_id)
    )
    db.commit()
    return cur.lastrowid

# Función: edit_licitacion
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   external_id (cadena): Identificador externo de la licitación, por ejemplo de otro SI.
#   title (cadena): Titulo de la licitación 
#   description (cadena): Descripción larga de la licitación.
#   fecha_inicio (date): Fecha de inicio de prepración de la licitación.
#   fecha_adjudicacion (date): Fecha fin, cuando se adjudica la licitación.
#   user_id (desconocido): Usuario con rol responsable que tramita la licitación.
# Descripción: Actualiza en la tabla licitaciones los valores de una licitación dada por el identificador.
# Retorna: Niguna
def edit_licitacion(db, lic_id, external_id, title, description, fecha_inicio, fecha_adjudicacion):
    db.execute(
        "UPDATE licitaciones SET external_id=?, title=?, description=?, fecha_inicio=?, fecha_adjudicacion=? WHERE id=?",
        (external_id, title, description, fecha_inicio, fecha_adjudicacion, lic_id)
    )
    db.commit()

# Función: remove_licitacion
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   lic_id (entero): Identificado de la licitación que queremos obtener.
# Descripción: Borra una licitación que tenga el identificador especificado por lic_id
# Retorna: Ninguno
def remove_licitacion(db, lic_id):
    db.execute("DELETE FROM licitaciones WHERE id=?", (lic_id,))
    db.commit()


# Función: fetch_licitacion_by_id
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   lic_id (entero): Identificado de la licitación que queremos obtener.
# Descripción: Obtiene una licitación que tenga el identificador especificado por lic_id
# Retorna: Datos de la licitación
def fetch_licitacion_by_id(db, licitacion_id):
    """Devuelve una fila de la licitación según su ID"""
    sql = """
        SELECT *
        FROM licitaciones
        WHERE id = ?
    """
    return db.execute(sql, (licitacion_id,)).fetchone()

