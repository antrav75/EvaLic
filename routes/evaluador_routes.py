from flask import Blueprint, render_template, session, redirect, url_for, current_app
from services.evaluaciones_service import listar_por_evaluador
from models.dao import get_db

evaluador_bp = Blueprint('evaluador', __name__, url_prefix='/evaluador')

@evaluador_bp.route('/')
def index():
    # Comprobar sesión y rol
    if 'user_id' not in session or session.get('role_id') != 3:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    licitaciones = listar_por_evaluador(db, session['user_id'])
    return render_template('evaluador/index.html', licitaciones=licitaciones)