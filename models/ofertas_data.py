from .dao import get_db

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

def create_oferta(db, licitacion_id, licitante_id, fechapresentacion):
    cur = db.execute(
        "INSERT INTO ofertas (licitacion_id, licitante_id, fechapresentacion) VALUES (?,?,?)",
        (licitacion_id, licitante_id, fechapresentacion)
    )
    db.commit()
    return licitacion_id, licitante_id

def edit_oferta(db, licitacion_id, licitante_id_old, new_licitante_id, fechapresentacion):
    db.execute(
        "UPDATE ofertas SET licitante_id=?, fechapresentacion=? WHERE licitacion_id=? AND licitante_id=?",
        (new_licitante_id, fechapresentacion, licitacion_id, licitante_id_old)
    )
    db.commit()

def remove_oferta(db, licitacion_id, licitante_id):
    db.execute("DELETE FROM ofertas WHERE licitacion_id=? AND licitante_id=?", (licitacion_id, licitante_id))
    db.commit()
