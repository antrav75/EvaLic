from models.dao import get_db

def list_licitaciones(db):
    cur = db.execute("SELECT * FROM licitaciones ORDER BY id")
    return cur.fetchall()

def get_licitacion(db, lic_id):
    cur = db.execute("SELECT * FROM licitaciones WHERE id=?", (lic_id,))
    return cur.fetchone()

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

def edit_licitacion(db, lic_id, external_id, title, description, fecha_inicio, fecha_adjudicacion):
    db.execute(
        "UPDATE licitaciones SET external_id=?, title=?, description=?, fecha_inicio=?, fecha_adjudicacion=? WHERE id=?",
        (external_id, title, description, fecha_inicio, fecha_adjudicacion, lic_id)
    )
    db.commit()

def remove_licitacion(db, lic_id):
    db.execute("DELETE FROM licitaciones WHERE id=?", (lic_id,))
    db.commit()


def fetch_licitacion_by_id(db, licitacion_id):
    """Devuelve una fila de la licitación según su ID"""
    sql = """
        SELECT *
        FROM licitaciones
        WHERE id = ?
    """
    return db.execute(sql, (licitacion_id,)).fetchone()

