from datetime import datetime

def fetch_licitaciones_by_evaluator(db, evaluator_id):
    sql = '''
        SELECT 
            l.id, 
            l.external_id, 
            l.title, 
            l.description, 
            l.fecha_inicio, 
            l.fecha_adjudicacion,
            sub.nombre AS etapa_actual
        FROM licitaciones l
        INNER JOIN licitaciones_evaluadores le ON l.id = le.licitacion_id
        LEFT JOIN (
            SELECT e.licitacion_id, f.nombre
            FROM etapas e
            INNER JOIN fases f ON e.fase_id = f.id
            WHERE e.fecha_inicio = (
                SELECT MAX(e2.fecha_inicio)
                FROM etapas e2
                WHERE e2.licitacion_id = e.licitacion_id
            )
        ) sub ON l.id = sub.licitacion_id
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

def guardar_o_actualizar_evaluacion_economica(
        db,
        licitacion_id,
        licitante_id,
        criterio_id,
        puntuacion,
        comentarios,
        usuario_id
    ):
    """
    Inserta o actualiza una evaluación económica.
    La tabla 'evaluaciones' NO tiene campo 'id' ni 'puntuacionmaxima';
    se identifica la fila por la combinación:
      (licitacion_id, licitante_id, criterio_id, usuario_id).
    """

    # 1) Comprobar si existe ya esa evaluación
    existing = db.execute(
        """
        SELECT 1
        FROM evaluaciones
        WHERE
          licitacion_id = ?
          AND licitante_id = ?
          AND criterio_id = ?
          AND usuario_id = ?
        """,
        (licitacion_id, licitante_id, criterio_id, usuario_id)
    ).fetchone()

    if existing:
        # 2a) Si existe, actualizar los campos necesarios
        db.execute(
            """
            UPDATE evaluaciones
            SET
              puntuacion      = ?,
              comentarios     = ?,
              fechaevaluacion = ?
            WHERE
              licitacion_id = ?
              AND licitante_id = ?
              AND criterio_id = ?
              AND usuario_id = ?
            """,
            (
                puntuacion,
                comentarios,
                datetime.now(),
                licitacion_id,
                licitante_id,
                criterio_id,
                usuario_id
            )
        )
    else:
        # 2b) Si no existe, insertar nueva fila (sin puntuacionmaxima)
        db.execute(
            """
            INSERT INTO evaluaciones (
              licitacion_id,
              licitante_id,
              criterio_id,
              puntuacion,
              comentarios,
              usuario_id,
              fechaevaluacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                licitacion_id,
                licitante_id,
                criterio_id,
                puntuacion,
                comentarios,
                usuario_id,
                datetime.now()
            )
        )

    db.commit()