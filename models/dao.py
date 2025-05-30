
import sqlite3
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash
import math

def get_db(app):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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

    CREATE TABLE IF NOT EXISTS event_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor_username TEXT NOT NULL,
        actor_user_id INTEGER,
        event_type TEXT NOT NULL,
        target_username TEXT,
        target_user_id INTEGER,
        success INTEGER NOT NULL,
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
        oferta_id INTEGER NOT NULL,
        criterio_id INTEGER,
        PRIMARY KEY (licitacion_id, usuario_id, oferta_id, criterio_id)
        FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)                                       
        FOREIGN KEY (usuario_id) REFERENCES users(id)
        FOREIGN KEY (oferta_id) REFERENCES ofertas(id)
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
        licitacion_id,
        usuario_id,
        PRIMARY KEY (licitacion_id,usuario_id)
        FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)
        FOREIGN KEY (usuario_id) REFERENCES users(id)
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

# ... resto de funciones (no modificadas)

def get_roles(db):
    return db.execute("SELECT id,description FROM roles").fetchall()

def get_role_id(db, description):
    row = db.execute(
        "SELECT id FROM roles WHERE LOWER(description)=LOWER(?)",
        (description,)
    ).fetchone()
    return row['id'] if row else None

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

def get_user_by_username(db, username):
    return db.execute(
        "SELECT * FROM users WHERE username=?",(username,)
    ).fetchone()

def get_user_by_id(db, user_id):
    return db.execute(
        "SELECT * FROM users WHERE id=?",(user_id,)
    ).fetchone()

def add_user(db, username, email, password_hash, role_id, active=True):
    cur = db.execute(
        "INSERT INTO users(username,email,password,role_id,active) VALUES(?,?,?,?,?)",
        (username, email, password_hash, role_id, int(active))
    )
    db.commit()
    return cur.lastrowid

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

def delete_user(db, user_id):
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()

def log_event(db, actor_username, actor_user_id, event_type,
              target_username=None, target_user_id=None, success=1):
    db.execute(
        """INSERT INTO event_audit
           (actor_username,actor_user_id,event_type,
            target_username,target_user_id,success)
           VALUES(?,?,?,?,?,?)""",
        (actor_username,actor_user_id,event_type,
         target_username,target_user_id,success)
    )
    db.commit()


def list_ofertas_by_licitacion(app, licitacion_id):
    db = get_db(app)
    query = """
    SELECT o.licitante_id, o.licitacion_id, o.fechapresentacion, o.admitidasobre1, l.nombreempresa
    FROM ofertas o
    JOIN licitantes l ON o.licitante_id = l.id
    WHERE o.licitacion_id = ?
    """
    return db.execute(query, (licitacion_id,)).fetchall()

def update_admitidasobre1(app, licitacion_id, licitante_id, admitido):
    db = get_db(app)
    db.execute(
        "UPDATE ofertas SET admitidasobre1 = ? WHERE licitacion_id = ? AND licitante_id = ?",
        (admitido, licitacion_id, licitante_id)
    )
    db.commit()
