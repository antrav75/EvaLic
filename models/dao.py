
import sqlite3
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash
import math
from datetime import datetime

# Función: get_db
# Parámetros:
#   app (cadena): Nombre de la aplicación 
# Descripción: La función get_db obtiene el nombre de la base de  datos asociado a la aplicación del parametro app.
# Retorna: desconocido - Descripción del valor devuelto.
def get_db(app):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

# Función: close_connection
# Parámetros:
#   exception (entero): Valor de vuelto para indicar si todo ha salido bien o no.
# Descripción: Cierra la conexión de la aplicación web
# Retorna: Ninguno
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Función: init_db
# Parámetros:
#   app (cadena): Nombre de la aplicación.
# Descripción: Esta función inicializa los valores de la Base de Datos en caso de que no exista. Se
#              crea la base de datos, se crean las tablas necesarias para la aplicación y se crean
#              los valores por defecto para la ejecución perfecta de la aplicación desde su primera
#              ejecución.
# Retorna: Ninguno.
def init_db(app):
    db = get_db(app)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        active INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(role_id) REFERENCES roles(id)
    );

    CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombreUsuario TEXT NOT NULL,
        tipoEvento TEXT NOT NULL,
        descripcionEvento TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS licitaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        external_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        fecha_inicio TEXT NOT NULL,
        fecha_adjudicacion TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
                     
     CREATE TABLE IF NOT EXISTS fases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE CHECK(nombre IN ('Borrador','Iniciada','Sobre1','Sobre2','Sobre3','Evaluada','Cerrada'))
    );
                     
     CREATE TABLE IF NOT EXISTS etapas (
        identificador INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT ,
        fase_id INTEGER NOT NULL,
        licitacion_id INTEGER NOT NULL,
        FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)                         
        FOREIGN KEY (fase_id) REFERENCES fases(id)
    );
                     
     CREATE TABLE IF NOT EXISTS tipo_criterios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        TipoCriterio TEXT NOT NULL UNIQUE CHECK(TipoCriterio IN ('Técnico','Económico'))
    );   

     CREATE TABLE IF NOT EXISTS formulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        NombreFormula NOT NULL UNIQUE                                                              
    );
                     
     CREATE TABLE IF NOT EXISTS criterios (
        id  INTEGER PRIMARY KEY AUTOINCREMENT,
        NombreCriterio TEXT NOT NULL,
        descripcion TEXT,
        peso INTEGER,
        PrecioBase INTEGER,
        PuntuacionMaxima INTEGER,                          
        tipocriterio_id INTEGER NOT NULL,
        licitacion_id INTEGER NOT NULL,
        formula_id INTEGER,                          
        FOREIGN KEY (tipocriterio_id) REFERENCES tipo_criterios(id)
        FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)
        FOREIGN KEY (formula_id) REFERENCES formulas(id)                                                             
    );

      CREATE TABLE IF NOT EXISTS evaluaciones (
        puntuacion INTEGER,                         
        comentarios TEXT,
        fechaevaluacion TEXT ,
        licitacion_id INTEGER NOT NULL,             
        usuario_id INTEGER NOT NULL,
        licitante_id INTEGER NOT NULL,
        criterio_id INTEGER,             
        PRIMARY KEY (licitacion_id, usuario_id, licitante_id, criterio_id)
        FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)                                       
        FOREIGN KEY (usuario_id) REFERENCES users(id)
        FOREIGN KEY (licitante_id) REFERENCES licitantes(id)
        FOREIGN KEY (criterio_id) REFERENCES criterio(id)                                                                          
    );   

      CREATE TABLE IF NOT EXISTS ofertas (
        fechapresentacion TEXT NOT NULL,
        admitidasobre1 INTEGER,             
        licitacion_id INTEGER NOT NULL,
        licitante_id INTEGER NOT NULL,
        PRIMARY KEY (licitacion_id,licitante_id)                                       
        FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)
        FOREIGN KEY (licitante_id) REFERENCES licitantes(id)                                                           
    );                   

      CREATE TABLE IF NOT EXISTS licitantes (
        id  INTEGER PRIMARY KEY AUTOINCREMENT,
        nombreempresa TEXT NOT NULL,
        cif text NOT NULL,
        direccion text,
        ciudad text,
        provincia text,
        telefono text,
        email text                                                                                                                            
    );

      CREATE TABLE IF NOT EXISTS licitaciones_evaluadores (
        licitacion_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        PRIMARY KEY (licitacion_id,usuario_id)
        FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)
        FOREIGN KEY (usuario_id) REFERENCES users(id)
    );
                     
      CREATE TABLE IF NOT EXISTS resultados (
        puntuacionponderada INTEGER,
        ofertaAB INTEGER NOT NULL,
        fechaResultado TEXT NOT NULL,
        licitacion_id INTEGER NOT NULL,
        licitante_id INTEGER NOT NULL,
        criterio_id INTEGER NOT NULL,
        PRIMARY KEY (licitacion_id, licitante_id,criterio_id)
        FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)
        FOREIGN KEY (licitante_id) REFERENCES licitantes(id)
        FOREIGN KEY (criterio_id) REFERENCES criterios(id)             
    );
                                                                                                                   
    """)
    
    db.commit()
    # Insertar roles por defecto
    roles = ['Administrador', 'Responsable', 'Evaluador']
    for rol in roles:
        db.execute(
            "INSERT OR IGNORE INTO roles (description) VALUES (?);", (rol,)
        )
    db.commit()  

    # Insertar fases por defecto
    fases = ['Borrador', 'Iniciada', 'Sobre1', 'Sobre2', 'Sobre3', 'Evaluada', 'Cerrada']
    for nombre in fases:
        db.execute(
            "INSERT OR IGNORE INTO fases (nombre) VALUES (?);", (nombre,)
        )
    db.commit()   

    # Insertar tipos de criterio por defecto
    TipoCriterios = ['Administrativo','Técnico','Económico']
    for TipoCriterio in TipoCriterios:
        db.execute(
            "INSERT OR IGNORE INTO tipo_criterios (TipoCriterio) VALUES (?);", (TipoCriterio,)
        )
    db.commit()            

    # Insertar tipos de formula por defecto
    Formulas_habituales = ['Formula inversa proporcional','Formula proporcional por baja','Formula proporcional reparto de puntos']
    for Formula in Formulas_habituales:
        db.execute(
            "INSERT OR IGNORE INTO formulas (NombreFormula) VALUES (?);", (Formula,)
        )
    db.commit()           

    # Insertar usuario administrador por defecto
    cur = db.execute("SELECT id FROM users WHERE username='admin'")
    if cur.fetchone() is None:
        admin_role = db.execute(
            "SELECT id FROM roles WHERE id='1'"
        ).fetchone()[0]
        db.execute(
            "INSERT INTO users(username,email,password,role_id,active) VALUES(?,?,?,?,?)",
            ('admin','', generate_password_hash('tfg_unir'), admin_role, 1)
        )
        db.commit()

# Función: get_roles
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
# Descripción: Obtiene los datos de la tabla roles para la lista.
# Retorna: lista de valores de la tabla roles
def get_roles(db):
    return db.execute("SELECT id,description FROM roles").fetchall()

# Función: get_role_id
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   description (cadena): Descripción del role.
# Descripción: Obtiene el identificador a partir de la descripción del rol
# Retorna: Identificador (Entero)
def get_role_id(db, description):
    row = db.execute(
        "SELECT id FROM roles WHERE LOWER(description)=LOWER(?)",
        (description,)
    ).fetchone()
    return row['id'] if row else None

# Función: fetch_users
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   search (cadena): Cadena de búsqueda para el filtro.
#   role_id (entero): Identificador del rol.
#   page (entero): Valor de página para la identificación.
#   per_page (entero): Número de usuarios por página que se pueden mostrar.
# Descripción: Esta función se encarga de obtener de la tabla de usuarios los
#              valores de los usuarios que se van a mostrar paginados de 5 
#              en 5.
# Retorna: lista de datos de los usuarios, total y número de páginas. 
def fetch_users(db, search='', role_id=None, page=1, per_page=5):
    base = "FROM users u LEFT JOIN roles r ON u.role_id=r.id WHERE 1=1"
    params = []
    if search:
        base += " AND u.username LIKE ?"
        params.append(f"%{search}%")
    if role_id:
        base += " AND u.role_id=?"
        params.append(role_id)
    total = db.execute("SELECT COUNT(*) "+base, params).fetchone()[0]
    pages = math.ceil(total/per_page)
    data = db.execute(
        "SELECT u.id,u.username,u.email,u.role_id,u.active,r.description AS role_description "
        + base + " LIMIT ? OFFSET ?",
        params+[per_page,(page-1)*per_page]
    ).fetchall()
    return data, total, pages

# Función: get_user_by_username
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   username (cadena): Nombre de usuario.
# Descripción: Retorna los datos de un usuario a partir del nombre de usuario consultado.
# Retorna: lista de datos del usuario.
def get_user_by_username(db, username):
    return db.execute(
        "SELECT * FROM users WHERE username=?",(username,)
    ).fetchone()

# Función: get_username_by_id
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   user_id (entero): Identificador del usuario.
# Descripción: Obtiene el nombre del usuario a partir del identificador consultado.
# Retorna: lista de datos del usuario.
def get_username_by_id(db, user_id):
    users= db.execute(
        "SELECT username FROM users WHERE id=?",(user_id,)
    ).fetchone()
    return users['username']

# Función: get_user_by_id
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   user_id (entero): Identificador del usuario.
# Descripción: Obtiene todos los datos del usuario a partir del identificador consultado.
# Retorna: desconocido - Lista de datos.
def get_user_by_id(db, user_id):
    return db.execute(
        "SELECT * FROM users WHERE id=?",(user_id,)
    ).fetchone()

# Función: add_user
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   username (cadena): Nombre del usuario a crear.
#   email (cadena): Correo electrónico del usuario a crear.
#   password_hash (cadena): Hash obtenido a partir de la contraseña .
#   role_id (entero): Identificador del rol asignado.
#   active (entero): Indica si el usuario está activo para el login o no.
# Descripción: Está función se utiliza para crear un usuario en la tabla de usuarios.
# Retorna: Ninguno
def add_user(db, username, email, password_hash, role_id, active=True):
    cur = db.execute(
        "INSERT INTO users(username,email,password,role_id,active) VALUES(?,?,?,?,?)",
        (username, email, password_hash, role_id, int(active))
    )
    db.commit()
    return cur.lastrowid

# Función: update_user
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   user_id (entero): Identificador del usuario a editar.
#   username (cadena): Nombre del usuario a crear.
#   email (cadena): Correo electrónico del usuario a crear.
#   password_hash (cadena): Hash obtenido a partir de la contraseña .
#   role_id (entero): Identificador del rol asignado.
#   active (entero): Indica si el usuario está activo para el login o no.
# Descripción: Está función se utiliza para cmodficar los datos de  un usuario en la tabla de usuarios.
# Retorna: Ninguno
def update_user(db, user_id, username, email, password_hash, role_id, active):
    if password_hash:
        db.execute(
            "UPDATE users SET username=?, email=?, password=?, role_id=?, active=? WHERE id=?",
            (username, email, password_hash, role_id, active, user_id)
        )
    else:
        db.execute(
            "UPDATE users SET username=?, email=?, role_id=?, active=? WHERE id=?",
            (username, email, role_id, active, user_id)
        )
    db.commit()

# Función: delete_user
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   user_id (entero): Identificador del usuario a borrar.
# Descripción: Esta función borra los datos del usuario seleccionado.
# Retorna: Ninguno
def delete_user(db, user_id):
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()

# Función: log_event
# Parámetros:
#   db (conexión): Nombre de la conexión a la base de datos.
#   nombreUsuario (cadena): Nombre del usuario que ha generado el evento.
#   TipoEvento (cadena): Tipo de evento registrado.
#   DescripcionEvento (cadena): Descripción del evento registrado.
#   success (entero): Indica si el evento se almacenó correctamente.
# Descripción: La función log_event registra las acciones o eventos que los usuarios
#              van realizando en la aplicación como el CRUD de usuarios, criterios,
#              licitaciones, etc. por si hay que realizar auditoría. 
# Retorna: Ninguno
def log_event(db, nombreUsuario, TipoEvento, DescripcionEvento,success=1):
    db.execute(
        """INSERT INTO auditoria
           (nombreUsuario,tipoEvento,
            descripcionEvento)
           VALUES(?,?,?)""",
        (nombreUsuario,TipoEvento,DescripcionEvento)
    )
    db.commit()


# Función: list_ofertas_by_licitacion
# Parámetros:
#   app (cadena): Nombre de la aplicación.
#   licitacion_id (entero): identificador de la licitación de la que se va a obtener las ofertas.
# Descripción: Esta función obtiene a partir de una licitación las ofertas que se han presentado.
# Retorna: Lista de ofertas.
def list_ofertas_by_licitacion(app, licitacion_id):
    db = get_db(app)
    query = """
    SELECT o.licitante_id, o.licitacion_id, o.fechapresentacion, o.admitidasobre1, l.nombreempresa
    FROM ofertas o
    JOIN licitantes l ON o.licitante_id = l.id
    WHERE o.licitacion_id = ?
    """
    return db.execute(query, (licitacion_id,)).fetchall()

# Función: update_admitidasobre1
# Parámetros:
#   db (desconocido): Descripción del parámetro db.
#   licitacion_id (desconocido): Descripción del parámetro licitacion_id.
#   licitante_id (desconocido): Descripción del parámetro licitante_id.
#   admitido (desconocido): Descripción del parámetro admitido.
# Descripción: Breve descripción de lo que hace la función update_admitidasobre1.
# Retorna: desconocido - Descripción del valor devuelto.
def update_admitidasobre1(db, licitacion_id, licitante_id, admitido):
    db.execute(
        "UPDATE ofertas SET admitidasobre1 = ? WHERE licitacion_id = ? AND licitante_id = ?",
        (admitido, licitacion_id, licitante_id)
    )
    db.commit()

# Función: get_formulas
# Parámetros:
#   db (desconocido): Descripción del parámetro db.
# Descripción: Breve descripción de lo que hace la función get_formulas.
# Retorna: desconocido - Descripción del valor devuelto.
def get_formulas(db):
    """
    Recupera todas las fórmulas de la tabla formulas.
    Devuelve lista de dicts con claves 'id' y 'nombre'.
    """
    # Ejecutar la consulta para obtener las fórmulas    
    filas = db.execute("SELECT id, NombreFormula FROM formulas").fetchall()
    return [ {'id': f['id'], 'NombreFormula': f['NombreFormula']} for f in filas ]

