from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models.dao import get_db, get_role_id
from services.user_service import (
    list_users, create_user, edit_user, remove_user
)

user_bp = Blueprint('user', __name__, url_prefix='/')

@user_bp.route('useradmin')
def dashboard():
    if 'user_id' not in session or session.get('role_id') != 1:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    admin_id = get_role_id(db, 'administrador')
    if session.get('role_id') != admin_id:
        return "Acceso denegado", 403

    search = request.args.get('search','').strip()
    selected = request.args.get('role_id','')
    role_id = int(selected) if selected.isdigit() else None
    page = int(request.args.get('page',1))

    data = list_users(db, search, role_id, page)
    return render_template('usuarios/useradmin.html',
        users=data['users'],
        roles=data['roles'],
        page=page,
        total_pages=data['pages'],
        search=search,
        selected_role=selected
    )

@user_bp.route('add_user', methods=['POST'])
def add_user():
    db = get_db(current_app)
    admin_id = get_role_id(db, 'administrador')
    if session.get('role_id') != admin_id:
        return redirect(url_for('auth.login'))
    try:
        username = request.form['username'].strip()
        email    = request.form['email']
        pwd      = request.form['password']
        confirm  = request.form['confirm_password']
        if pwd != confirm:
            flash("Las contraseñas no coinciden", 'danger')
            return redirect(url_for('user.dashboard'))
        active   = bool(request.form.get('active'))
        create_user(db, session, username, email, pwd,
                    int(request.form['role_id']), active)
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('user.dashboard'))

@user_bp.route('edit_user/<int:user_id>', methods=['POST'])
def edit_user_route(user_id):
    db = get_db(current_app)
    admin_id = get_role_id(db, 'administrador')
    if session.get('role_id') != admin_id:
        return redirect(url_for('auth.login'))
    try:
        username = request.form['username'].strip()
        email    = request.form['email']
        pwd      = request.form.get('password')
        confirm  = request.form.get('confirm_password')
        if (pwd or confirm) and pwd != confirm:
            flash("Las contraseñas no coinciden", 'danger')
            return redirect(url_for('user.dashboard'))
        active   = bool(request.form.get('active'))
        edit_user(db, session, user_id,
                  username, email, pwd,
                  int(request.form['role_id']), active)
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('user.dashboard'))

@user_bp.route('delete_user/<int:user_id>', methods=['POST'])
def delete_user_route(user_id):
    db = get_db(current_app)
    admin_id = get_role_id(db, 'administrador')
    if session.get('role_id') != admin_id:
        return redirect(url_for('auth.login'))
    remove_user(db, session, user_id)
    return redirect(url_for('user.dashboard'))
