from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session
)

from services.criterio_service import (
    listar, obtener, crear, actualizar, borrar,
    tipos, formulas
)
from services.licitacion_service import get_licitacion


criterios_bp = Blueprint('criterios', __name__, url_prefix='/criterios')

@criterios_bp.route('/<int:lic_id>')

def index(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))


    # 1) Recuperar todos los criterios
    items = listar(lic_id)
 
    # 2) Aplicar filtros en memoria según formulario
    filtro_nombre = request.args.get('filtro_nombre', '').strip()
    filtro_tipo   = request.args.get('filtro_tipo', '')
 
    if filtro_nombre:
        items = [
            c for c in items
            if filtro_nombre.lower() in (c['NombreCriterio'] or '').lower()
        ]
 
    if filtro_tipo:
        items = [
            c for c in items
            if c['TipoCriterio'] == filtro_tipo
        ]

    # Extraer solo el nombre de tipo para el desplegable
    tipo_filtros = [t['TipoCriterio'] for t in tipos()]

    return render_template(
        'criterios/index.html',
        criterios=items,
        lic_id=lic_id,
        tipo_opts=tipo_filtros,  # ahora es lista de strings, no Rows
        request=request
    )

@criterios_bp.route('/<int:lic_id>/create', methods=('GET','POST'))
def create_criterio_route(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            data['licitacion_id'] = lic_id
            crear( data, session['user_id'])
            flash('Criterio creado exitosamente', 'success')
            # redirijo al listado de criterios
            return redirect(url_for('criterios.index', lic_id=lic_id))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template(
        'criterios/create.html',
        lic_id=lic_id,
        tipo_opts=tipos(),
        formula_opts=formulas()
    )

@criterios_bp.route('/<int:lic_id>/<int:crit_id>/edit', methods=('GET','POST'))
def edit_criterio_route(lic_id, crit_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    crit = obtener( crit_id)
    if not crit:
        flash('Criterio no encontrado', 'danger')
    if request.method == 'POST':
        try:
            actualizar( crit_id, request.form.to_dict(),session['user_id'])
            flash('Criterio actualizado', 'success')
            # redirijo al listado de criterios
            return redirect(url_for('criterios.index', lic_id=lic_id))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template(
        'criterios/edit.html',
        criterio=crit,
        tipo_opts=tipos(),
        formula_opts=formulas(),
        lic_id=lic_id
    )

@criterios_bp.route('/<int:lic_id>/<int:crit_id>/delete', methods=('POST',))
def delete_criterio_route(lic_id, crit_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        borrar(lic_id,crit_id,session['user_id'])
        flash('Criterio eliminado', 'success')
    except Exception as e:
        flash(str(e), 'danger')

    # ¡Muy importante! devolver algo. Redirigimos al listado:
    return redirect(url_for('criterios.index', lic_id=lic_id))
