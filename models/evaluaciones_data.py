def fetch_licitaciones_by_evaluator(db, evaluator_id):
    sql = '''
        SELECT l.id, l.external_id, l.title, l.description, l.fecha_inicio, l.fecha_adjudicacion
        FROM licitaciones l
        JOIN licitaciones_evaluadores le ON l.id = le.licitacion_id
        
        WHERE le.usuario_id = ?
        ORDER BY l.fecha_inicio DESC
    '''
    return db.execute(sql, (evaluator_id,)).fetchall()

def fetch_evaluaciones(db, licitacion_id, usuario_id):
    sql = """
        SELECT oferta_id, criterio_id, puntuacion, comentarios
        FROM evaluaciones
        WHERE licitacion_id=? AND usuario_id=?
    """
    return db.execute(sql, (licitacion_id, usuario_id)).fetchall()


def save_evaluacion(db, licitacion_id, usuario_id, oferta_id, criterio_id, puntuacion, comentarios):
    db.execute(
        """
        INSERT OR REPLACE INTO evaluaciones
        (licitacion_id, usuario_id, oferta_id, criterio_id, puntuacion, comentarios, fechaevaluacion)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (licitacion_id, usuario_id, oferta_id, criterio_id, puntuacion, comentarios)
    )
    db.commit()