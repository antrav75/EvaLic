import sqlite3
from datetime import datetime
from flask import g


def delete_resultados(db, licitacion_id):
    """
    Elimina resultados (técnicos y económicos) previos de una licitación.
    """
    sql = "DELETE FROM resultados WHERE licitacion_id = ?"
    db.execute(sql, (licitacion_id,))
    db.commit()

def insert_resultados_tecnicos(db, licitacion_id):
    """
    Inserta (o reemplaza) los resultados técnicos de la licitación,
    calculando la media ponderada de puntuaciones para criterios técnicos (tipocriterio_id = 2).
    """
    delete_resultados(db, licitacion_id)
    sql = """
        INSERT INTO resultados (
            licitacion_id,
            usuario_id,
            licitante_id,
            criterio_id,
            puntuacionponderada,
            ofertaAB,
            fechaResultado
        )
        SELECT
          r.licitacion_id,
          r.usuario_id,
          r.licitante_id,
          r.criterio_id,
          ROUND(r.puntuacion * c.peso) AS avg_ponderado,
          0 AS ofertaAB,
          DATETIME('now')
        FROM evaluaciones r
        JOIN criterios c ON r.criterio_id = c.id
        WHERE r.licitacion_id = ?
          AND c.tipocriterio_id = 2
        GROUP BY c.id, r.licitante_id
        ORDER BY c.id, avg_ponderado DESC
    """
    db.execute(sql, (licitacion_id,))
    db.commit()

def insert_resultados_economicos(db, licitacion_id):
    """
    Inserta (o reemplaza) los resultados económicos (Sobre 3) de la licitación.
    Usa exclusivamente `evaluaciones.puntuacion` como “precio de oferta” y
    `criterios.PrecioBase`. No intenta leer `ofertas.precio`.
    """
    from services.formulas_economicas_service import (
        inversa_proporcional,
        proporcional_baja_con_presupuesto,
        reparto_proporcional,
        es_oferta_anormalmente_baja
    )

    # 1) Obtenemos todas las evaluaciones económicas para esta licitación
    sql_eval = """
        SELECT
          e.usuario_id,
          e.licitante_id,
          e.criterio_id,
          e.puntuacion AS precio_oferta,
          c.formula_id,
          c.PrecioBase
        FROM evaluaciones e
        JOIN criterios c ON e.criterio_id = c.id
        WHERE e.licitacion_id = ?
          AND c.tipocriterio_id = 3
    """
    filas_eval = db.execute(sql_eval, (licitacion_id,)).fetchall()

    # 2) Agrupamos por criterio: { criterio_id: [(licitante_id, precio_oferta), …] }
    precios_por_criterio = {}
    for f in filas_eval:
        cid = f['criterio_id']
        lid = f['licitante_id']
        precio = f['precio_oferta']
        if precio is None:
            continue
        precios_por_criterio.setdefault(cid, []).append((lid, precio))

    # 3) Para cada criterio, calculamos puntuaciones
    for cid, lista_lprecios in precios_por_criterio.items():
        # 3.a) Lista de todos los precios para este criterio
        precios_lista = [precio for (_, precio) in lista_lprecios]
        # 3.b) Mejor precio (mínimo) para esa lista
        mejor_oferta = min(precios_lista) if precios_lista else None

        for lid, precio_oferta in lista_lprecios:
            # 3.c) Buscamos la fila base (solo una) para extraer usuario_id, formula_id y PrecioBase
            fila_base = next(
                (f for f in filas_eval
                 if f['criterio_id'] == cid and f['licitante_id'] == lid),
                None
            )
            if not fila_base:
                continue

            usuario_id = fila_base['usuario_id']
            formula_id = fila_base['formula_id']
            precio_base_criterio = fila_base['PrecioBase']

            # 3.d) Calculamos la puntuación en función de la fórmula
            if formula_id == 1:
                # Fórmula inversa proporcional: (precio_actual, mejor_precio, presupuesto_base)
                puntuacion_pond = inversa_proporcional(
                    precio_oferta,
                    mejor_oferta,        # ahora sí pasamos el mínimo real
                    precio_base_criterio # presup. base
                )
            elif formula_id == 2:
                # Fórmula proporcional con presupuesto base: (precio_actual, mejor_precio, presupuesto_base)
                puntuacion_pond = proporcional_baja_con_presupuesto(
                    precio_oferta,
                    mejor_oferta,         # corregido: mejor_precio en vez de precio_oferta
                    precio_base_criterio  # presup. base
                )
            elif formula_id == 3:
                # Reparto proporcional: reparto_proporcional(precio_actual, lista_de_precios)
                scores = reparto_proporcional(precio_oferta, precios_lista)
                try:
                    idx = precios_lista.index(precio_oferta)
                    puntuacion_pond = scores[idx]
                except ValueError:
                    puntuacion_pond = None
            else:
                puntuacion_pond = None

            # 3.e) Calculamos el indicador de oferta anormalmente baja
            flag_ab = 1 if es_oferta_anormalmente_baja(
                precio_oferta,
                precios_lista,
                presupuesto_base=precio_base_criterio
            ) else 0

            # 3.f) Redondeo y validación
            if puntuacion_pond is None:
                puntuacion_sql = None
            else:
                try:
                    puntuacion_sql = round(float(puntuacion_pond), 4)
                except (TypeError, ValueError):
                    puntuacion_sql = None

            # 4) Insertamos en la tabla resultados
            sql_ins = """
                INSERT OR REPLACE INTO resultados (
                    licitacion_id,
                    usuario_id,
                    licitante_id,
                    criterio_id,
                    puntuacionponderada,
                    ofertaAB,
                    fechaResultado
                ) VALUES (?, ?, ?, ?, ?, ?, DATETIME('now'))
            """
            db.execute(
                sql_ins,
                (
                    licitacion_id,
                    usuario_id,
                    lid,
                    cid,
                    puntuacion_sql,
                    flag_ab
                )
            )

    db.commit()
    
def fetch_informe(db, licitacion_id):
    """
    Recupera todos los resultados (técnicos y económicos) para la licitación.
    Devuelve filas ordenadas por criterio y licitante.
    """
    sql = """
        SELECT
          r.criterio_id,
          c.NombreCriterio   AS nombre_criterio,
          CASE c.tipocriterio_id
            WHEN 2 THEN 'Técnico'
            WHEN 3 THEN 'Económico'
            ELSE 'Otro'
          END                  AS tipo_criterio,
          r.licitante_id,
          l.nombreempresa     AS nombreempresa,
          r.puntuacionponderada,
          r.ofertaAB,
          r.usuario_id,
          u.username,
          r.fechaResultado
        FROM resultados r
        JOIN criterios c ON r.criterio_id = c.id
        JOIN licitantes l ON r.licitante_id = l.id
        LEFT JOIN users u ON r.usuario_id = u.id
        WHERE r.licitacion_id = ?
        ORDER BY c.id, r.licitante_id
    """
    return db.execute(sql, (licitacion_id,)).fetchall()
