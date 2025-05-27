def fetch_licitaciones_by_evaluator(db, evaluator_id):
    sql = '''
        SELECT l.external_id, l.title, l.description, l.fecha_inicio, l.fecha_adjudicacion
        FROM licitaciones l
        JOIN licitaciones_evaluadores le ON l.id = le.licitacion_id
        
        WHERE le.usuario_id = ?
        ORDER BY l.fecha_inicio DESC
    '''
    return db.execute(sql, (evaluator_id,)).fetchall()