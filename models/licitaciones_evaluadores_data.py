from models.dao import get_db

# Función: list_evaluadores
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
# Descripción: Obtiene/lista los evaluadores que tienen el rol evaluador.
# Retorna: datos de los usuarios con rol evaluador
def list_evaluadores(db):
    # Lista todos los usuarios con rol evaluador
    cur = db.execute(
        """
        SELECT u.* FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE r.description = 'Evaluador'
        """
    )
    return cur.fetchall()

# Función: list_evaluadores_by_licitacion
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   lic_id (entero): Identificador de la licitación que queremos obtener los evaluadores.
# Descripción: A partir del identificador pasado a la función se obtienen los evaluadores que participan en dicha licitación.
# Retorna: lista  de evaluadores que participan en la licitación
def list_evaluadores_by_licitacion(db, lic_id):
    # Lista evaluadores asignados a la licitación
    cur = db.execute(
        """
        SELECT u.* FROM users u
        JOIN licitaciones_evaluadores le ON u.id = le.usuario_id
        WHERE le.licitacion_id = ?
        """, (lic_id,)
    )
    return cur.fetchall()

# Función: assign_evaluadores
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   lic_id (entero): Identificador de la licitación que queremos asignar los evaluadores.
#   user_ids (lista): Lista de usuarios que van a intervenir como evaluadores en la liacitación.
# Descripción: Esta función asigna los evaluadores que van a realizar la evaluación técnica de una licitación
#              determinada. 
# Retorna: Ninguno.
def assign_evaluadores(db, lic_id, user_ids):
    # Reemplaza la lista de evaluadores de la licitación
    db.execute(
        "DELETE FROM licitaciones_evaluadores WHERE licitacion_id = ?", (lic_id,)
    )
    for uid in user_ids:
        db.execute(
            "INSERT INTO licitaciones_evaluadores (licitacion_id, usuario_id) VALUES (?,?)",
            (lic_id, uid)
        )
    db.commit()
