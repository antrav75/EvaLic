from datetime import datetime

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
        SELECT e.licitacion_id,e.usuario_id,e.licitante_id, e.criterio_id, e.puntuacion, c.preciobase, e.fechaevaluacion, e.comentarios,c.puntuacionmaxima
        FROM evaluaciones e JOIN criterios c ON e.criterio_id = c.id
        WHERE e.licitacion_id=? AND usuario_id=?
    """
    return db.execute(sql, (licitacion_id, usuario_id)).fetchall()


def save_evaluacion(db, licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios):
    db.execute(
        """
        INSERT OR REPLACE INTO evaluaciones
        (licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion,comentarios, fechaevaluacion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios,datetime.now())
    )
    db.commit()

