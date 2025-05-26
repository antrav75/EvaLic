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
