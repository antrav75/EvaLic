from models.dao import get_db

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
