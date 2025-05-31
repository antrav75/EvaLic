# models/resultados_data.py

def delete_resultados(db, licitacion_id):
    """Elimina resultados previos de una licitación"""
    sql = """
        DELETE FROM resultados
        WHERE licitacion_id = ?
    """
    db.execute(sql, (licitacion_id,))
    db.commit()

def insert_resultados_tecnicos(db, licitacion_id):
    """Inserta resultados técnicos para la licitación sobreescribiendo previos"""
    # Borra resultados previos
    delete_resultados(db, licitacion_id)
    # Inserta nuevos resultados
    sql = """
        INSERT INTO resultados
        (licitacion_id, usuario_id, licitante_id, criterio_id, puntuacionponderada, ofertaAB, fecharesultado)
        SELECT
            e.licitacion_id,
            e.usuario_id,
            e.licitante_id,
            e.criterio_id,
            e.puntuacion * c.peso AS puntuacionponderada,
            0 AS ofertaAB,
            datetime('now')
        FROM evaluaciones e
        JOIN criterios c ON e.criterio_id = c.id
        WHERE e.licitacion_id = ? AND c.tipocriterio_id = 2
    """
    db.execute(sql, (licitacion_id,))
    db.commit()

def fetch_informe_tecnico(db, licitacion_id):
    """Devuelve la media ponderada por criterio y oferta"""
    sql = """
        SELECT
            c.id AS criterio_id,
            c.NombreCriterio AS criterio_nombre,
            o.licitante_id AS licitante_id,
            AVG(r.puntuacionponderada) AS avg_ponderado
        FROM resultados r
        JOIN criterios c ON r.criterio_id = c.id
        JOIN ofertas o ON r.licitante_id = o.licitante_id AND o.licitacion_id = ?
        WHERE r.licitacion_id = ?
        GROUP BY c.id, o.licitante_id
        ORDER BY c.id, avg_ponderado DESC
    """
    return db.execute(sql, (licitacion_id, licitacion_id)).fetchall()

def fetch_evaluadores(db, licitacion_id):
    """Obtiene la lista de evaluadores que han participado"""
    sql = """
        SELECT DISTINCT u.id, u.username
        FROM resultados r
        JOIN users u ON r.usuario_id = u.id
        WHERE r.licitacion_id = ?
    """
    return db.execute(sql, (licitacion_id,)).fetchall()
