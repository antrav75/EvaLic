from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, abort
from math import ceil
from models.dao import get_db, get_role_id
from services.licitacion_service import (
    list_licitaciones, get_licitacion, create_licitacion,
    edit_licitacion, remove_licitacion
)
from services.etapa_service import advance_etapa, get_current_stage
from services.licitacion_service import list_evaluadores_logic, get_evaluadores_for_licitacion, assign_evaluadores

licitaciones_bp = Blueprint('licitaciones', __name__, url_prefix='/licitaciones')

@licitaciones_bp.route('/', methods=('GET',))
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    db = get_db(current_app)
    user_id = session.get('user_id')

    lic_rows = list_licitaciones(db)
    licitaciones = [l for l in lic_rows if l['user_id'] == user_id]

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('LIC_PER_PAGE', 10)
    total = len(licitaciones)
    total_pages = ceil(total / per_page) if total else 1
    current_page = page
    start = (page - 1) * per_page
    end = start + per_page
    licitaciones = licitaciones[start:end]

    responsable_id = get_role_id(db, 'responsable')
    is_responsable = session.get('role_id') == responsable_id

    return render_template(
        'licitaciones/index.html',
        licitaciones=licitaciones,
        is_responsable=is_responsable,
        total_pages=total_pages,
        current_page=current_page,
        request=request
    )


@licitaciones_bp.route('/<int:lic_id>/avanzar_estado', methods=('POST',))
def avanzar_estado(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    fecha_avance = request.form.get('fecha_avance')
    try:
        next_name = advance_etapa(db, lic_id, fecha_avance)
    except Exception as e:
        flash(str(e), 'error')
    else:
        flash(f'Estado avanzado a {next_name}', 'success')
    return redirect(url_for('licitaciones.edit_licitacion_route', lic_id=lic_id))


@licitaciones_bp.route('/create', methods=('GET', 'POST'))
def create_licitacion_route():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    if request.method == 'POST':
        data = request.form
        try:
            create_licitacion(
                db,
                data.get('external_id'),
                data.get('title'),
                data.get('description'),
                data.get('fecha_inicio'),
                data.get('fecha_adjudicacion'),
                session['user_id']
            )
        except ValueError as e:
            flash(str(e), 'error')
        else:
            flash('Licitación creada correctamente', 'success')
            return redirect(url_for('licitaciones.index'))
    return render_template('licitaciones/create.html')

@licitaciones_bp.route('/<int:lic_id>/edit', methods=('GET', 'POST'))
def edit_licitacion_route(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    lic = get_licitacion(db, lic_id)
    if not lic:
        flash('No existe la licitación', 'error')
        return redirect(url_for('licitaciones.index'))
    responsable_id = get_role_id(db, 'responsable')
    is_responsable = session.get('role_id') == responsable_id
    if is_responsable and lic['user_id'] != session.get('user_id'):
        abort(403)

    # Obtiene la etapa actual
    current_stage = get_current_stage(db, lic_id)
    # Datos para modal Evaluadores
    evaluadores_all = list_evaluadores_logic(db)
    evaluadores_selected = get_evaluadores_for_licitacion(db, lic_id)
    # IDs de evaluadores ya asignados
    selected_ids = [e['id'] for e in evaluadores_selected]


    if request.method == 'POST':
        data = request.form
        try:
            edit_licitacion(
                db,
                lic_id,
                data.get('external_id'),
                data.get('title'),
                data.get('description'),
                data.get('fecha_inicio'),
                data.get('fecha_adjudicacion')
            )
        except ValueError as e:
            flash(str(e), 'error')
        else:
            flash('Licitación actualizada correctamente', 'success')
            return redirect(url_for('licitaciones.index'))
    return render_template('licitaciones/edit.html',
         selected_ids=selected_ids,
        evaluadores_all=evaluadores_all,
        evaluadores_selected=evaluadores_selected,
        lic=lic,
        current_stage=current_stage,
        is_responsable=is_responsable
    )

@licitaciones_bp.route('/<int:lic_id>/delete', methods=('POST',))
def delete_licitacion_route(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    try:
        remove_licitacion(db, lic_id, session.get('user_id'))
    except PermissionError:
        abort(403)
    except ValueError as e:
        flash(str(e), 'error')
    else:
        flash('Licitación eliminada correctamente', 'success')
    return redirect(url_for('licitaciones.index'))


@licitaciones_bp.route('/<int:lic_id>/evaluadores', methods=('POST',))
def evaluadores_licitacion(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    lic = get_licitacion(db, lic_id)
    current_stage = get_current_stage(db, lic_id)
    if current_stage not in ('Borrador', 'Iniciada'):
        flash('No se permite asignar evaluadores en esta fase', 'error')
        return redirect(url_for('licitaciones.edit_licitacion_route', lic_id=lic_id))
    selected = request.form.getlist('evaluadores_selected')
    selected_ids = [int(uid) for uid in selected]
    try:
        assign_evaluadores(db, lic_id, selected_ids)
        flash('Evaluadores asignados correctamente', 'success')
    except Exception as e:
        flash(str(e), 'error')
    return redirect(url_for('licitaciones.edit_licitacion_route', lic_id=lic_id))
