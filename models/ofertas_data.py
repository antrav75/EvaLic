from .dao import get_db

# Función: list_ofertas
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación sobre la que queremos obtener ofertas.
# Descripción: Esta función obtiene las ofertas de la licitación de la que se le ha pasado el identificador.
# Retorna: lista de ofertas
def list_ofertas(db, licitacion_id=None):
    query = """
        SELECT o.licitacion_id, o.licitante_id, o.fechapresentacion, o.admitidasobre1, l.nombreempresa
        FROM ofertas o
        JOIN licitantes l ON o.licitante_id = l.id
    """
    params = ()
    if licitacion_id:
        query += " WHERE o.licitacion_id=?"
        params = (licitacion_id,)
    query += " ORDER BY o.licitacion_id, o.licitante_id"
    cur = db.execute(query, params)
    return cur.fetchall()

# Función: list_ofertas_admitidas
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación sobre la que queremos obtener ofertas admitidas en la etapa Sobre1.
# Descripción: Esta función obtiene las ofertas de la licitación de la que se le ha pasado el identificador y que han sido
#              admitidas en la etapa de licitación Sobre1.
# Retorna: lista de ofertas admitidas
def list_ofertas_admitidas(db, licitacion_id=None):
    query = """
        SELECT o.licitacion_id, o.licitante_id, o.fechapresentacion, o.admitidasobre1, l.nombreempresa
        FROM ofertas o
        JOIN licitantes l ON o.licitante_id = l.id
    """
    params = ()
    if licitacion_id:
        query += " WHERE o.admitidasobre1 =1 AND o.licitacion_id=?"
        params = (licitacion_id,)
    query += " ORDER BY o.licitacion_id, o.licitante_id"
    cur = db.execute(query, params)
    return cur.fetchall()

# Función: get_oferta
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación sobre la que queremos obtener ofertas.
#   licitante_id (entero): Identificador de la empresa licitante.
# Descripción: Esta función obtiene la oferta realizada por una determinada empresa licitante en una licitación
#              dada por el identificador.
# Retorna: Datos de la oferta
def get_oferta(db, licitacion_id, licitante_id):
    cur = db.execute(
        """
        SELECT o.licitacion_id, o.licitante_id, o.fechapresentacion, o.admitidasobre1, l.nombreempresa
        FROM ofertas o
        JOIN licitantes l ON o.licitante_id = l.id
        WHERE o.licitacion_id=? AND o.licitante_id=?
        """, (licitacion_id, licitante_id)
    )
    return cur.fetchone()

# Función: create_oferta
# Parámetros:
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación que queremos crear.
#   licitante_id (entero): Identificador de la empresa licitante.
#   fechapresentacion (date): Fecha de presentación de la oferta.
# Descripción: Esta función almacena en la tabla ofertas una oferta realizada por una empresa licitante en una 
#              licitación dada.
# Retorna: licitacion_id(entero) y licitante_id(entero)
def create_oferta(db, licitacion_id, licitante_id, fechapresentacion):
    cur = db.execute(
        "INSERT INTO ofertas (licitacion_id, licitante_id, fechapresentacion) VALUES (?,?,?)",
        (licitacion_id, licitante_id, fechapresentacion)
    )
    db.commit()
    return licitacion_id, licitante_id

# Función: edit_oferta
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación que queremos actualizar.
#   old_licitante_id (entero): Identificador de la empresa licitante antigua.
#   new_licitante_id (entero): Identificador de la empresa licitante nueva.
#   fechapresentacion (date): Fecha de presentación de la oferta.
# Descripción: Esta función actualiza en la tabla ofertas una oferta realizada por una empresa licitante en una 
#              licitación dada. Se incluye el posible cambio de empresa que haya realizado la licitación.
# Retorna: Ninguno
def edit_oferta(db, licitacion_id, licitante_id_old, new_licitante_id, fechapresentacion):
    db.execute(
        "UPDATE ofertas SET licitante_id=?, fechapresentacion=? WHERE licitacion_id=? AND licitante_id=?",
        (new_licitante_id, fechapresentacion, licitacion_id, licitante_id_old)
    )
    db.commit()

# Función: remove_oferta
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación que queremos actualizar.
#   licitante_id (entero): Identificador de la empresa licitante.
# Descripción: Esta función borra la oferta realizada por una determinada empresa licitante en una licitación.
# Retorna: Ninguno
def remove_oferta(db, licitacion_id, licitante_id):
    db.execute("DELETE FROM ofertas WHERE licitacion_id=? AND licitante_id=?", (licitacion_id, licitante_id))
    db.commit()



