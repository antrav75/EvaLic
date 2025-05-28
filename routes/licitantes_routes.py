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
    # Obtener todos los licitantes
    lics = list_licitantes_logic(current_app)
    # Renderizar plantilla con contexto
    return render_template('licitantes/index.html',
                           licitantes=lics,
                           licitacion_id=licitacion_id)

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
