import sqlite3
from flask import g

# Función: list_criterios
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos
#   licitacion_id (entero): Es el identificador de la licitación que se está procesando actualmente
# Descripción: A partir del identificador de la licitación que se está procesando actualmente
#              obtiene los criterios con los que se va evaluar.
# Retorna: lista con todos los criterios que se va evaluar
def list_criterios(db, licitacion_id):
    return db.execute("""
        SELECT c.*, t.TipoCriterio, f.NombreFormula, c.PrecioBase
        FROM criterios c
        JOIN tipo_criterios t ON c.tipocriterio_id=t.id
        LEFT JOIN formulas f ON c.formula_id=f.id
        WHERE c.licitacion_id=?
        ORDER BY c.id
    """, (licitacion_id,)).fetchall()

# Función: get_criterio
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   criterio_id (desconocido): Identificador del criterio a obtener.
# Descripción: Se obtiene el criterio que coincida con el valor del id de la tabla criterios.
# Retorna: criterio seleccionado.
def get_criterio(db, criterio_id):
    return db.execute("SELECT * FROM criterios WHERE id=?", (criterio_id,)).fetchone()

# Función: create_criterio
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   nombre (cadena): Nombre del criterio.
#   descripcion (cadena): Descripción del criterio.
#   peso (entero): Peso del criterio si es técnico.
#   tipo_id (entero): Identificador del tipo de criterio.
#   lic_id (entero): Identificador de la licitación selecciionada.
#   formula_id (entero): Fórmula del valor a utilizar si el criterio es económico.
#   precio_base (entero): Precio base si el criterio es económico.
#   puntuacion_maxima (entero): Puntuación máxima del criterio.
# Descripción: Introduce los valores del criterio a crear en la tabla criterios.
# Retorna: Ninguno.
def create_criterio(db, nombre, descripcion, peso, tipo_id, lic_id, formula_id, precio_base,puntuacion_maxima):
    db.execute("""
        INSERT INTO criterios 
        (NombreCriterio, Descripcion, Peso, tipocriterio_id, licitacion_id, formula_id, PrecioBase, PuntuacionMaxima)
        VALUES(?,?,?,?,?,?,?,?)
    """, (nombre, descripcion, peso, tipo_id, lic_id, formula_id, precio_base,puntuacion_maxima))
    db.commit()

# Función: edit_criterio
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   nombre (cadena): Nombre del criterio.
#   descripcion (cadena): Descripción del criterio.
#   peso (entero): Peso del criterio si es técnico.
#   tipo_id (entero): Identificador del tipo de criterio.
#   lic_id (entero): Identificador de la licitación selecciionada.
#   formula_id (entero): Fórmula del valor a utilizar si el criterio es económico.
#   precio_base (entero): Precio base si el criterio es económico.
#   puntuacion_maxima (entero): Puntuación máxima del criterio.
# Descripción: Introduce los valores del criterio a editar en la tabla criterios.
# Retorna: Ninguno.
def edit_criterio(db, criterio_id, nombre, descripcion, peso, tipo_id, formula_id, precio_base, puntuacion_maxima):
    db.execute("""
        UPDATE criterios
        SET NombreCriterio=?, Descripcion=?, Peso=?, tipocriterio_id=?, formula_id=?, PrecioBase=?, PuntuacionMaxima=?
        WHERE id=?
    """, (nombre, descripcion, peso, tipo_id, formula_id, precio_base,puntuacion_maxima,criterio_id))
    db.commit()

# Función: delete_criterio
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   criterio_id (entero): Criterio a borrar.
# Descripción: Borra ek criterio indicado de la tabla criterios.
# Retorna: Ninguno
def delete_criterio(db, criterio_id):
    db.execute("DELETE FROM criterios WHERE id=?", (criterio_id,))
    db.commit()

# Función: list_tipo_criterios
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
# Descripción: Devuelve todos los valores de la table tipo_criterios.
# Retorna: lista con todos los valores
def list_tipo_criterios(db):
    return db.execute("SELECT * FROM tipo_criterios").fetchall()

# Función: list_formulas
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
# Descripción: Devuelve todos los valores de la table fórmulas.
# Retorna: lista con todos los valores de la tabla fórmulas.
def list_formulas(db):
    return db.execute("SELECT * FROM formulas").fetchall()

# Función: fetch_criterios_tecnicos
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación de la que se qieren obtener los criterios técnicos .
# Descripción: A partir del identificador de la licitación se obtienen los criterios técnicos asociadas a esta.
# Retorna: lista con los valores de los criterios técnicos
def fetch_criterios_tecnicos(db, licitacion_id):
    sql = """
        SELECT *
        FROM criterios
        WHERE licitacion_id = ? AND tipocriterio_id = 2
    """
    return db.execute(sql, (licitacion_id,)).fetchall()

# Función: fetch_criterios_economicos
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitacion_id (entero): Identificador de la licitación de la que se qieren obtener los criterios económicos .
# Descripción: A partir del identificador de la licitación se obtienen los criterios económicos asociadas a esta.
# Retorna: lista con los valores de los criterios técnicos
def fetch_criterios_economicos(db, licitacion_id):
    sql = """
        SELECT *
        FROM criterios
        WHERE licitacion_id = ? AND tipocriterio_id = 3
    """
    return db.execute(sql, (licitacion_id,)).fetchall()
