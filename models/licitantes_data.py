from models.dao import get_db

def list_licitantes(db):
    cur = db.execute(
        "SELECT id, nombreempresa, cif, direccion, ciudad, provincia, telefono, email FROM licitantes ORDER BY id"
    )
    return cur.fetchall()

def get_licitante(db, licitante_id):
    cur = db.execute(
        "SELECT id, nombreempresa, cif, direccion, ciudad, provincia, telefono, email FROM licitantes WHERE id=?",
        (licitante_id,)
    )
    return cur.fetchone()

def create_licitante(db, nombreempresa, cif, direccion, ciudad, provincia, telefono, email):
    cur = db.execute(
        "INSERT INTO licitantes (nombreempresa, cif, direccion, ciudad, provincia, telefono, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (nombreempresa, cif, direccion, ciudad, provincia, telefono, email)
    )
    db.commit()
    return cur.lastrowid

def edit_licitante(db, licitante_id, nombreempresa, cif, direccion, ciudad, provincia, telefono, email):
    db.execute(
        "UPDATE licitantes SET nombreempresa=?, cif=?, direccion=?, ciudad=?, provincia=?, telefono=?, email=? WHERE id=?",
        (nombreempresa, cif, direccion, ciudad, provincia, telefono, email, licitante_id)
    )
    db.commit()

def remove_licitante(db, licitante_id):
    db.execute("DELETE FROM licitantes WHERE id=?", (licitante_id,))
    db.commit()

def fetch_licitantes_por_licitacion(db, licitacion_id):
    """
    Devuelve todos los licitantes (id y nombreempresa) que tienen al menos
    una evaluación registrada en la licitación `licitacion_id`.
    """
    sql = """
        SELECT DISTINCT l.id, l.nombreempresa
        FROM licitantes l
        JOIN evaluaciones e ON l.id = e.licitante_id
        WHERE e.licitacion_id = ?
        ORDER BY l.nombreempresa
    """
    filas = db.execute(sql, (licitacion_id,)).fetchall()
    # Convertir sqlite3.Row a dict para uso en plantilla
    return [ {'id': fila['id'], 'nombreempresa': fila['nombreempresa']} for fila in filas ]
