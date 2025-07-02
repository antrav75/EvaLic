from datetime import datetime

# Función: fetch_licitaciones_by_evaluator
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   evaluator_id (entero): Identificador del evaluador.
# Descripción: Esta función obtiene los datos necesario de la licitaciones en las que participa
#              el evaluador con el identificador que se ha pasado.
# Retorna: Lista de licitaciones
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

# Función: fetch_evaluaciones
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación que se está evaluando.
#   usuario_id (entero): Descripción del parámetro usuario_id.
# Descripción: A partir del identificador de la licitación y del identificador del usuario que evalua se obtiene
#              el listado de evaluaciones en las que participa.
# Retorna: Lista de evaluaciones
def fetch_evaluaciones(db, licitacion_id, usuario_id):
    sql = """
        SELECT e.licitacion_id,e.usuario_id,e.licitante_id, e.criterio_id, e.puntuacion, c.preciobase, e.fechaevaluacion, e.comentarios,c.puntuacionmaxima
        FROM evaluaciones e JOIN criterios c ON e.criterio_id = c.id
        WHERE e.licitacion_id=? AND usuario_id=?
    """
    return db.execute(sql, (licitacion_id, usuario_id)).fetchall()


# Función: save_evaluacion
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación que se está evaluando.
#   usuario_id (entero): Descripción del parámetro usuario_id.
#   licitante_id (entero): Identificador del licitante al que pertenece la oferta.
#   criterio_id (entero): Identificador del criterio que es evaluado.
#   puntuacion (entero): Puntuación asignada a la evaluación del criterio.
#   comentarios (cadena): Comentarios para aclarar la evaluación.
# Descripción: Esta función almacena en la tabla evaluaciones la evaluación realizada sobre una 
#              determinada oferta dentro del contexto de una evaluación.
# Retorna: Ninguno
def save_evaluacion(db, licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios):
    db.execute(
        """
        INSERT OR REPLACE INTO evaluaciones
        (licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion,comentarios, fechaevaluacion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (licitacion_id, usuario_id, licitante_id, criterio_id, puntuacion, comentarios,datetime.now())
    )
    db.commit()

# Función: guardar_o_actualizar_evaluacion_economica
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación de la que se va a guardar la evaluacion.
#   licitante_id (entero): Identificador del licitante que ha presentado la oferta.
#   criterio_id (entero): Criterio a evaluar.
#   puntuacion (entero): Puntuación otorgada por el evaluador.
#   formula_id (entero): identificador de la fórmula económica con la que se va a evaluar.
#   comentarios (cadena): Comentarios para aclarar la evaluación.
#   usuario_id (entero): Usuario con perfil evaluador o responsable que evalua la licitación.
#   puntuacionmaxima (entero): Puntuacion máxima a calcular cuando se usa una fórmula económica.
# Descripción: Esta función guarda o actualiza una evaluación económica de una oferta realizada a una licitación
#              Primero comprueba si existe y si no existe la crea, si existe la modifica.
# Retorna: desconocido - Descripción del valor devuelto.
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
