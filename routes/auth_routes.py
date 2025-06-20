
from flask import Blueprint, render_template, request, redirect, url_for, session
from services.auth_service import authenticate, logout

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        user = authenticate( request.form['username'].strip(),
                                 request.form['password'].strip())
        if user:
            session.update({
                'user_id': user['id'],
                'username': user['username'],
                'role_id': user['role_id']
            })

            session.permanent = True # Mantener la sesión activa

            if user['role_id'] == 1:
                return redirect(url_for('user.dashboard'))  # Administrador
            elif user['role_id'] == 2:
                return redirect(url_for('licitaciones.index'))  # Responsable
            elif user['role_id'] == 3:
                return redirect(url_for('evaluador.index')) # Evaluador
            else:
                return redirect(url_for('auth.login'))  # Evaluador o Desconocido
        error = 'Credenciales inválidas'
    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def do_logout():
    logout( session)
    return redirect(url_for('auth.login'))
