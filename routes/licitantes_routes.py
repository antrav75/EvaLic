from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from services.licitante_service import (
    list_licitantes_logic, get_licitante_logic, create_licitante_logic,
    edit_licitante_logic, remove_licitante_logic
)

licitantes_bp = Blueprint('licitantes', __name__, url_prefix='/licitantes')

@licitantes_bp.route('/')
def index():
    # Recuperamos licitacion_id de query string
    licitacion_id = request.args.get('licitacion_id', type=int)
    # 1) Listado completo
    all_licitantes = list_licitantes_logic(current_app)
    lics = all_licitantes

    # ——— Filtros “en memoria” ———
    filtro_nombre    = request.args.get('filtro_nombre',   '').strip()
    filtro_provincia = request.args.get('filtro_provincia','')
    filtro_ciudad    = request.args.get('filtro_ciudad',   '')

    if filtro_nombre:
        lics = [
            l for l in lics
            if filtro_nombre.lower() in (l['nombreempresa'] or '').lower()
        ]

    if filtro_provincia:
        lics = [
            l for l in lics
            if l['provincia'] == filtro_provincia
        ]

    if filtro_ciudad:
        lics = [
            l for l in lics
            if filtro_ciudad.lower() in (l['ciudad'] or '').lower()
        ]

    # Listas para poblar los <select>
    provincias = sorted({l['provincia'] for l in all_licitantes if l['provincia']})
    ciudades   = sorted({l['ciudad']    for l in all_licitantes if l['ciudad']})

    # 2) Renderizamos ya con filtros aplicados
    return render_template(
        'licitantes/index.html',
        licitantes=lics,
        licitacion_id=licitacion_id,
        provincias=provincias,
        ciudades=ciudades,
        request=request
    )

@licitantes_bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        data = {
            'nombreempresa': request.form.get('nombreempresa'),
            'cif': request.form.get('cif'),
            'direccion': request.form.get('direccion'),
            'ciudad': request.form.get('ciudad'),
            'provincia': request.form.get('provincia'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email')
        }
        create_licitante_logic(current_app, data)
        flash('Licitante creado', 'success')
        return redirect(url_for('licitantes.index'))
    return render_template('licitantes/create.html')

@licitantes_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    lic = get_licitante_logic(current_app, id)
    if request.method == 'POST':
        data = {
            'nombreempresa': request.form.get('nombreempresa'),
            'cif': request.form.get('cif'),
            'direccion': request.form.get('direccion'),
            'ciudad': request.form.get('ciudad'),
            'provincia': request.form.get('provincia'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email')
        }
        edit_licitante_logic(current_app, id, data)
        flash('Licitante actualizado', 'success')
        return redirect(url_for('licitantes.index'))
    return render_template('licitantes/edit.html', licitante=lic)

@licitantes_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    remove_licitante_logic(current_app, id)
    flash('Licitante eliminado', 'success')
    return redirect(url_for('licitantes.index'))
