from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from services.oferta_service import list_ofertas_logic, get_oferta_logic, create_oferta_logic, edit_oferta_logic, remove_oferta_logic, evaluate_sobre1_logic
from services.licitante_service import list_licitantes_logic
import sqlite3
from datetime import datetime

ofertas_bp = Blueprint('ofertas', __name__, url_prefix='/ofertas')

@ofertas_bp.route('/')
def index():
    # Recuperar licitacion_id de la query string
    licitacion_id = request.args.get('licitacion_id')

    
    # 1) Listado inicial de ofertas para esta licitación
    all_ofertas = list_ofertas_logic(current_app, licitacion_id)
    ofertas     = all_ofertas

    # 2) Aplicar filtros en memoria
    filtro_empresa = request.args.get('filtro_empresa', '').strip()
    fecha_desde    = request.args.get('fecha_desde', '')
    fecha_hasta    = request.args.get('fecha_hasta', '')

    # Filtrar por nombre de empresa
    if filtro_empresa:
        ofertas = [
            o for o in ofertas
            if filtro_empresa.lower() in (o['nombreempresa'] or '').lower()
        ]

    # Filtrar por rango de fecha de presentación
    if fecha_desde and fecha_hasta:
        try:
            d_from = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            d_to   = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            def in_range(o):
                val = o['fechapresentacion']
                if not val:
                    return False
                if isinstance(val, str):
                    d = datetime.strptime(val, '%Y-%m-%d').date()
                else:
                    d = val if hasattr(val, 'day') else val.date()
                return d_from <= d <= d_to
            ofertas = [o for o in ofertas if in_range(o)]
        except ValueError:
            pass

    # 3) Lista de empresas para el desplegable
    empresas = sorted({o['nombreempresa'] for o in all_ofertas if o['nombreempresa']})

    # 4) Renderizar con contexto de filtros
    return render_template(
        'ofertas/index.html',
        ofertas=ofertas,
        licitacion_id=licitacion_id,
        empresas=empresas,
        request=request
    )

@ofertas_bp.route('/new', methods=['GET', 'POST'])
def new():
    lic_id     = request.args.get('licitacion_id')
    next_url   = request.args.get('next') or url_for('ofertas.index', licitacion_id=lic_id)

    if request.method == 'POST':
        data = {
            'licitacion_id':   lic_id,
            'licitante_id':    request.form.get('licitante_id'),
            'fechapresentacion': request.form.get('fechapresentacion')
        }

        try:
            # Intentamos crear la oferta
            create_oferta_logic(current_app, data)
            flash('Oferta creada', 'success')
            return redirect(request.form.get('next') or url_for('ofertas.index', licitacion_id=lic_id))

        except sqlite3.IntegrityError:
            # Capturamos el UNIQUE constraint de (licitacion_id, licitante_id)
            flash(
                'Error: esta empresa ya ha presentado una oferta para esta licitación.',
                'danger'
            )
            # Volvemos a cargar la lista de licitantes para renderizar el form
            licitantes = list_licitantes_logic(current_app)
            return render_template(
                'ofertas/create.html',
                licitacion_id=lic_id,
                licitantes=licitantes,
                next=next_url,
                # opcional: volver a poner en el form lo que ya había rellenado
                selected_licitante_id=data['licitante_id'],
                fechapresentacion=data['fechapresentacion']
            )

    # GET
    licitantes = list_licitantes_logic(current_app)
    return render_template(
        'ofertas/create.html',
        licitacion_id=lic_id,
        licitantes=licitantes,
        next=next_url
    )

@ofertas_bp.route('/<int:licitacion_id>/<int:licitante_id>/edit', methods=['GET', 'POST'])
def edit(licitacion_id, licitante_id):
    next_url = request.args.get('next') or url_for('ofertas.index', licitacion_id=licitacion_id)
    oferta = get_oferta_logic(current_app, licitacion_id, licitante_id)
    if request.method == 'POST':
        data = {
            'licitacion_id': oferta.licitacion_id,
            'licitante_id': request.form.get('licitante_id'),
            'fechapresentacion': request.form.get('fechapresentacion')
        }
        edit_oferta_logic(current_app, licitacion_id, licitante_id, data)
        flash('Oferta actualizada', 'success')
        return redirect(request.form.get('next') or url_for('ofertas.index', licitacion_id=licitacion_id))
    licitantes = list_licitantes_logic(current_app)
    return render_template('ofertas/edit.html', oferta=oferta, licitantes=licitantes, next=next_url)

@ofertas_bp.route('/<int:licitacion_id>/<int:licitante_id>/delete', methods=['POST'])
def delete(licitacion_id, licitante_id):
    next_url = request.args.get('next') or url_for('ofertas.index', licitacion_id=licitacion_id)
    oferta = get_oferta_logic(current_app, licitacion_id, licitante_id)
    remove_oferta_logic(current_app, licitacion_id, licitante_id)
    flash('Oferta eliminada', 'success')
    return redirect(request.form.get('next') or url_for('ofertas.index', licitacion_id=licitacion_id))


@ofertas_bp.route('/<int:licitacion_id>/evaluar_sobre1', methods=['GET', 'POST'])
def evaluar_sobre1(licitacion_id):
    if request.method == 'POST':
        # Recoger decisiones de cada checkbox
        evaluaciones = {}
        # Marcar los checked
        for key, value in request.form.items():
            if key.startswith('admitidasobre1_'):
                lid = int(key.split('_')[1])
                evaluaciones[lid] = True
        # Marcar los unchecked para que se desmarquen
        ofertas = list_ofertas_logic(current_app, licitacion_id)
        for o in ofertas:
            lid = o['licitante_id']
            if lid not in evaluaciones:
                evaluaciones[lid] = False
        evaluate_sobre1_logic(current_app, licitacion_id, evaluaciones)
        flash('Ok', 'success')
        return redirect(url_for('licitaciones.edit_licitacion_route', lic_id=licitacion_id))
    # GET: mostrar tabla
    ofertas = list_ofertas_logic(current_app, licitacion_id)
    return render_template('ofertas/evaluar_sobre1.html',
                           ofertas=ofertas,
                           licitacion_id=licitacion_id)
