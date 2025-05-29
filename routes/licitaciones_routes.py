# routes/licitaciones_routes.py

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app, abort
)
from math import ceil
from models.dao import get_db, get_role_id
from services.licitacion_service import (
    list_licitaciones, get_licitacion, create_licitacion,
    edit_licitacion, remove_licitacion,
    list_evaluadores_logic, get_evaluadores_for_licitacion, assign_evaluadores
)
from services.stage_service import advance_stage, get_current_stage_name
from datetime import datetime

licitaciones_bp = Blueprint('licitaciones', __name__, url_prefix='/licitaciones')

@licitaciones_bp.route('/', methods=('GET',))
def index():
    if 'user_id' not in session or session.get('role_id') != 2:
        return redirect(url_for('auth.login'))

    db = get_db(current_app)
    user_id = session.get('user_id')

    lic_rows = list_licitaciones(db)
    licitaciones = [l for l in lic_rows if l['user_id'] == user_id]

       # ——— APLICAR FILTROS SEGÚN FORMULARIO ———
    external_id  = request.args.get('external_id', '').strip()
    title        = request.args.get('title', '').strip()
    fecha_tipo   = request.args.get('fecha_tipo', '')
    fecha_desde  = request.args.get('fecha_desde', '')
    fecha_hasta  = request.args.get('fecha_hasta', '')

    if external_id:
       licitaciones = [
           l for l in licitaciones
           if external_id.lower() in (l['external_id'] or '').lower()
       ]

    if title:
       licitaciones = [
           l for l in licitaciones
           if title.lower() in (l['title'] or '').lower()
       ]

    if fecha_tipo and fecha_desde and fecha_hasta:
       try:
           d_from = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
           d_to   = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
           def dentro(r):
               val = r[fecha_tipo]
               if not val:
                   return False
               # si viene como string “YYYY-MM-DD”
               if isinstance(val, str):
                   dt = datetime.strptime(val, '%Y-%m-%d').date()
               else:
                   # si ya es date o datetime
                   dt = val if hasattr(val, 'day') else val.date()
               return d_from <= dt <= d_to
           licitaciones = [l for l in licitaciones if dentro(l)]
       except ValueError:
           # fechas mal formateadas: ignorar filtro
           pass
   
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('LIC_PER_PAGE', 10)
    total = len(licitaciones)
    total_pages = ceil(total / per_page) if total else 1
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
        current_page=page,
        request=request
    )

@licitaciones_bp.route('/<int:lic_id>/avanzar_estado', methods=('POST',))
def avanzar_estado(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    fecha_avance = request.form.get('fecha_avance')
    try:
        siguiente = advance_stage(db, lic_id, fecha_avance)
    except Exception as e:
        flash(str(e), 'error')
    else:
        flash(f'Estado avanzado a {siguiente}', 'success')
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

    # Obtener la etapa actual con la nueva función
    current_stage = get_current_stage_name(db, lic_id)

    # Datos para modal Evaluadores
    evaluadores_all = list_evaluadores_logic(db)
    evaluadores_selected = get_evaluadores_for_licitacion(db, lic_id)
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

    return render_template(
        'licitaciones/edit.html',
        lic=lic,
        current_stage=current_stage,
        is_responsable=is_responsable,
        evaluadores_all=evaluadores_all,
        evaluadores_selected=evaluadores_selected,
        selected_ids=selected_ids
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
    current_stage = get_current_stage_name(db, lic_id)
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