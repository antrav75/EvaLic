from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app
)

from services.criterio_service import (
    listar, obtener, crear, actualizar, borrar,
    tipos, formulas
)
from services.licitacion_service import get_licitacion
from services.etapa_service import get_current_stage
from models.dao import get_db

criterios_bp = Blueprint('criterios', __name__, url_prefix='/criterios')

@criterios_bp.route('/<int:lic_id>')

def index(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    items = listar(db, lic_id)
    return render_template(
        'criterios/index.html',
        criterios=items,
        lic_id=lic_id
    )

@criterios_bp.route('/<int:lic_id>/create', methods=('GET','POST'))
def create_criterio_route(lic_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            data['licitacion_id'] = lic_id
            crear(db, data, session['user_id'])
            flash('Criterio creado exitosamente', 'success')
            # redirijo al listado de criterios
            return redirect(url_for('criterios.index', lic_id=lic_id))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template(
        'criterios/create.html',
        lic_id=lic_id,
        tipo_opts=tipos(db),
        formula_opts=formulas(db)
    )

@criterios_bp.route('/<int:lic_id>/<int:crit_id>/edit', methods=('GET','POST'))
def edit_criterio_route(lic_id, crit_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    crit = obtener(db, crit_id)
    if not crit:
        flash('Criterio no encontrado', 'danger')
    if request.method == 'POST':
        try:
            actualizar(db, crit_id, request.form.to_dict())
            flash('Criterio actualizado', 'success')
            # redirijo al listado de criterios
            return redirect(url_for('criterios.index', lic_id=lic_id))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template(
        'criterios/edit.html',
        criterio=crit,
        tipo_opts=tipos(db),
        formula_opts=formulas(db),
        lic_id=lic_id
    )

@criterios_bp.route('/<int:lic_id>/<int:crit_id>/delete', methods=('POST',))
def delete_criterio_route(lic_id, crit_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    try:
        borrar(db, crit_id)
        flash('Criterio eliminado', 'success')
    except Exception as e:
        flash(str(e), 'danger')

    # ¡Muy importante! devolver algo. Redirigimos al listado:
    return redirect(url_for('criterios.index', lic_id=lic_id))
