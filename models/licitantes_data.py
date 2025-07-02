from models.dao import get_db

# Función: list_licitantes
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
# Descripción: Obtener/listar licitantes almacenados en el sistema.
# Retorna: lista con los datos de las empresas licitantes
def list_licitantes(db):
    cur = db.execute(
        "SELECT id, nombreempresa, cif, direccion, ciudad, provincia, telefono, email FROM licitantes ORDER BY id"
    )
    return cur.fetchall()

# Función: get_licitante
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitante_id (entero): Identificador de la empresa licitante que queremos obtener.
# Descripción: Esta función obtiene los datos de la empresa licitante a partir del identificador que se le ha pasado. 
# Retorna: Datos de la empresa licitante.
def get_licitante(db, licitante_id):
    cur = db.execute(
        "SELECT id, nombreempresa, cif, direccion, ciudad, provincia, telefono, email FROM licitantes WHERE id=?",
        (licitante_id,)
    )
    return cur.fetchone()

# Función: create_licitante
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   nombreempresa (cadena): Nombre de la empresa licitante a crear.
#   cif (cadena): CIF de la empresa licitante a crear.
#   direccion (cadena): Dirección postal de la empresa licitante.
#   ciudad (cadena): Ciudad de la empresa licitante.
#   provincia (cadena): Provincia de la empresa licitante.
#   telefono (entero): Teléfono de contacto de la empresa licitante.
#   email (cadena): E-mail de contacto de la empresa licitante
# Descripción: Esta función almacena en la tabla licitantes los datos de la empresa licitante que va a participar.
# Retorna: Datos de la empresa.
def create_licitante(db, nombreempresa, cif, direccion, ciudad, provincia, telefono, email):
    cur = db.execute(
        "INSERT INTO licitantes (nombreempresa, cif, direccion, ciudad, provincia, telefono, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (nombreempresa, cif, direccion, ciudad, provincia, telefono, email)
    )
    db.commit()
    return cur.lastrowid

# Función: edit_licitante
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitante_id: Identificador de la empresa licitante a editar.
#   nombreempresa (cadena): Nombre de la empresa licitante a editar.
#   cif (cadena): CIF de la empresa licitante a crear.
#   direccion (cadena): Dirección postal de la empresa licitante.
#   ciudad (cadena): Ciudad de la empresa licitante.
#   provincia (cadena): Provincia de la empresa licitante.
#   telefono (entero): Teléfono de contacto de la empresa licitante.
#   email (cadena): E-mail de contacto de la empresa licitante
# Descripción: Esta función edita en la tabla licitantes los datos de la empresa licitante que va a participar.
# Retorna: Ninguno
def edit_licitante(db, licitante_id, nombreempresa, cif, direccion, ciudad, provincia, telefono, email):
    db.execute(
        "UPDATE licitantes SET nombreempresa=?, cif=?, direccion=?, ciudad=?, provincia=?, telefono=?, email=? WHERE id=?",
        (nombreempresa, cif, direccion, ciudad, provincia, telefono, email, licitante_id)
    )
    db.commit()

# Función: remove_licitante
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitante_id(entero): Identificador de la empresa licitante a borrar.
# Descripción: Función para borrar una empresa licitante.
# Retorna: Ninguno
def remove_licitante(db, licitante_id):
    db.execute("DELETE FROM licitantes WHERE id=?", (licitante_id,))
    db.commit()

# Función: fetch_licitantes_por_licitacion
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   licitante_id(entero): Identificador de la empresa licitante .
# Descripción: Obtiene los datos de todos las empresas licitantes que participan en una determinada licitación.
# Retorna: desconocido - Descripción del valor devuelto.
def fetch_licitantes_por_licitacion(db, licitacion_id):
    """
    Devuelve todos los licitantes (id y nombreempresa) que tienen al menos
    una evaluación registrada en la licitación `licitacion_id`.
    """
    sql = """
        SELECT DISTINCT l.id, l.nombreempresa
        FROM licitantes l
        JOIN evaluaciones e ON l.id = e.licitante_id
        WHERE e.licitacion_id = ?
        ORDER BY l.nombreempresa
    """
    filas = db.execute(sql, (licitacion_id,)).fetchall()
    # Convertir sqlite3.Row a dict para uso en plantilla
    return [ {'id': fila['id'], 'nombreempresa': fila['nombreempresa']} for fila in filas ]
