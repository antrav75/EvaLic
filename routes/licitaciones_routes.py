# routes/licitaciones_routes.py

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app, abort
)
from math import ceil
from models.dao import get_db, get_role_id, get_formulas, guardar_evaluacion_economica, guardar_o_actualizar_evaluacion_economica

from services.licitacion_service import (
    list_licitaciones, get_licitacion, create_licitacion,
    edit_licitacion, remove_licitacion,
    list_evaluadores_logic, get_evaluadores_for_licitacion, assign_evaluadores
)
from services.stage_service import advance_stage, get_current_stage_name
from datetime import datetime

from services.evaluaciones_service import obtener_evaluaciones, guardar_evaluacion
from services.criterio_service import listar_economicos
from services.resultados_service import generar_informe_tecnico
from services.licitacion_service import obtener_licitacion_por_id

from services.oferta_service import list_ofertas_admitidas_logic, evaluate_sobre1_logic
from services.licitacion_service import get_licitacion as get_licitacion_logic

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

@licitaciones_bp.route('/<int:licitacion_id>/evaluar_sobre3', methods=('GET', 'POST'))
def evaluar_sobre3(licitacion_id):
    # 1. Autenticación: solo rol evaluador (role_id == 2)
    if 'user_id' not in session or session.get('role_id') != 2:
        return redirect(url_for('auth.login'))
    usuario_id = session['user_id']
    db = get_db(current_app)

    # 2. Obtener todas las fórmulas para mostrar nombre de fórmula
    formulas_list = get_formulas(current_app)
    formulas_map = { f['id']: f['NombreFormula'] for f in formulas_list }

    # 3. Procesar POST: guardar o actualizar cada evaluación
    if request.method == 'POST' and request.form:
        # 3.1. Recuperar ofertas y criterios económicos desde servicios
        ofertas_bd = list_ofertas_admitidas_logic(current_app, licitacion_id)
        criterios_bd = listar_economicos(current_app, licitacion_id)

        # 3.2. Iterar cada oferta y cada criterio para leer valores del formulario
        for oferta in ofertas_bd:
            lid = oferta['licitante_id']
            for c in criterios_bd:
                cid = c['id']
                # Leer puntuación enviada
                raw_score = request.form.get(f'puntuacion_{lid}_{cid}', '').strip()
                try:
                    puntuacion = float(raw_score) if raw_score else 0.0
                except ValueError:
                    puntuacion = 0.0
                    flash(f"Puntuación inválida para oferta {lid}, criterio {cid}.", 'danger')

                # Leer comentarios
                comentarios = request.form.get(f'comentarios_{lid}_{cid}', '').strip()

                # 3.3. Llamar a la función DAO sin formula_id (no lo guardamos en evaluaciones)
                guardar_o_actualizar_evaluacion_economica(
                    current_app,
                    licitacion_id,
                    lid,
                    cid,
                    puntuacion,
                    comentarios,
                    usuario_id
                )

        flash("Evaluaciones económicas guardadas correctamente.", 'success')
        # Después de procesar POST, recargamos la vista con los valores actuales
        return redirect(url_for('licitaciones.edit_licitacion_route', lic_id=licitacion_id))

    # 4. Reconstruir datos para mostrar en GET y tras POST

    # 4.1. Datos generales de la licitación
    lic = get_licitacion_logic(db, licitacion_id)

    # 4.2. Recuperar ofertas y criterios
    raw_ofertas = list_ofertas_admitidas_logic(current_app, licitacion_id)
    criterios = listar_economicos(current_app, licitacion_id)

    # 4.3. Obtener evaluaciones existentes de este usuario en esta licitación
    evaluaciones = obtener_evaluaciones(current_app, licitacion_id, usuario_id)

    # 4.4. Crear mapa para buscar evaluación por (licitante_id, criterio_id)
    eval_map = {
        (e['licitante_id'], e['criterio_id']): e
        for e in evaluaciones
    }

    # 4.5. Construir lista final de ofertas con sus “criterios_evaluacion”
    ofertas = []
    for of in raw_ofertas:
        oferta_dict = dict(of)  # convierte Row a dict
        lista_criterios = []
        for c in criterios:
            key = (of['licitante_id'], c['id'])
            e = eval_map.get(key)

            # Si ya existe evaluación, extraemos sus datos; si no, campos vacíos
            puntuacion_existente = e['puntuacion'] if e else ''
            comentarios_existente = e['comentarios'] if e else ''
            # El criterio ya contiene formula_id en la tabla criterios
            formula_id_criterio = c['formula_id']
            nombre_f = formulas_map.get(formula_id_criterio, '–')

            lista_criterios.append({
                'id': c['id'],
                'nombre': c['NombreCriterio'],
                'puntuacion': puntuacion_existente,
                'preciobase': c['preciobase'],
                'formula_id': formula_id_criterio,
                'nombre_formula': nombre_f,
                'puntuacion_maxima': c['puntuacionmaxima'],
                'comentarios': comentarios_existente
            })
        oferta_dict['criterios_evaluacion'] = lista_criterios
        ofertas.append(oferta_dict)

    # 5. Renderizar la plantilla con lic, ofertas y la lista de fórmulas (por si hiciera falta)
    return render_template(
        'licitaciones/evaluar_sobre3.html',
        lic=lic,
        ofertas=ofertas
    )