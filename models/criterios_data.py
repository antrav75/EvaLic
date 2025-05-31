import sqlite3
from flask import g

def get_db(app):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def list_criterios(db, licitacion_id):
    return db.execute("""
        SELECT c.*, t.TipoCriterio, f.NombreFormula, c.PrecioBase
        FROM criterios c
        JOIN tipo_criterios t ON c.tipocriterio_id=t.id
        LEFT JOIN formulas f ON c.formula_id=f.id
        WHERE c.licitacion_id=?
        ORDER BY c.id
    """, (licitacion_id,)).fetchall()

def get_criterio(db, criterio_id):
    return db.execute("SELECT * FROM criterios WHERE id=?", (criterio_id,)).fetchone()

def create_criterio(db, nombre, descripcion, peso, tipo_id, lic_id, formula_id, precio_base):
    db.execute("""
        INSERT INTO criterios 
        (NombreCriterio, Descripcion, Peso, tipocriterio_id, licitacion_id, formula_id, PrecioBase)
        VALUES(?,?,?,?,?,?,?)
    """, (nombre, descripcion, peso, tipo_id, lic_id, formula_id, precio_base))
    db.commit()

def edit_criterio(db, criterio_id, nombre, descripcion, peso, tipo_id, formula_id, precio_base):
    db.execute("""
        UPDATE criterios
        SET NombreCriterio=?, Descripcion=?, Peso=?, tipocriterio_id=?, formula_id=?, PrecioBase=?
        WHERE id=?
    """, (nombre, descripcion, peso, tipo_id, formula_id, precio_base, criterio_id))
    db.commit()

def delete_criterio(db, criterio_id):
    db.execute("DELETE FROM criterios WHERE id=?", (criterio_id,))
    db.commit()

def list_tipo_criterios(db):
    return db.execute("SELECT * FROM tipo_criterios").fetchall()

def list_formulas(db):
    return db.execute("SELECT * FROM formulas").fetchall()

def fetch_criterios_tecnicos(db, licitacion_id):
    sql = """
        SELECT *
        FROM criterios
        WHERE licitacion_id = ? AND tipocriterio_id = 2
    """
    return db.execute(sql, (licitacion_id,)).fetchall()

def fetch_criterios_economicos(db, licitacion_id):
    sql = """
        SELECT *
        FROM criterios
        WHERE licitacion_id = ? AND tipocriterio_id = 3
    """
    return db.execute(sql, (licitacion_id,)).fetchall()