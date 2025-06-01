from flask import Blueprint, render_template, session, redirect, url_for, current_app, request, flash
from services.evaluaciones_service import listar_por_evaluador
from services.oferta_service import list_ofertas_admitidas_logic, evaluate_sobre1_logic
from services.licitacion_service import get_licitacion as get_licitacion_logic
from models.dao import get_db

from services.evaluaciones_service import obtener_evaluaciones, guardar_evaluacion
from services.criterio_service import listar_tecnicos
from services.resultados_service import generar_informe_tecnico
from services.licitacion_service import obtener_licitacion_por_id

evaluador_bp = Blueprint('evaluador', __name__, url_prefix='/evaluador')
evaluador_bp.route('/<int:licitacion_id>/evaluar', methods=['GET', 'POST'])

@evaluador_bp.route('/')
def index():
    # Comprobar sesión y rol
    if 'user_id' not in session or session.get('role_id') != 3:
        return redirect(url_for('auth.login'))
    db = get_db(current_app)
    licitaciones = listar_por_evaluador(db, session['user_id'])
    return render_template('evaluador/index.html', licitaciones=licitaciones)

@evaluador_bp.route('/<int:licitacion_id>/evaluar', methods=['GET', 'POST'])
def evaluar(licitacion_id):
    # Autenticación y contexto
    if 'user_id' not in session or session.get('role_id') != 3:
        return redirect(url_for('auth.login'))

    usuario_id = session['user_id']
    db = get_db(current_app)

    # POST: guardar o actualizar evaluaciones
    if request.method == 'POST':
        ofertas = list_ofertas_admitidas_logic(current_app, licitacion_id)
        # Filtrar solo criterios técnicos
        criterios = listar_tecnicos(current_app, licitacion_id)
        for oferta in ofertas:
            licitante_id = oferta['licitante_id']
            for c in criterios:
                crit_id = c['id']
                puntuacion = request.form.get(f'puntuacion_{licitante_id}_{crit_id}', 0)
                comentarios = request.form.get(f'comentarios_{licitante_id}_{crit_id}', '').strip()

                # y la guardamos en la BD
                guardar_evaluacion(
                    current_app,
                    licitacion_id,
                    usuario_id,
                    licitante_id,
                    crit_id,
                    puntuacion,  
                    comentarios
                )
        
        flash('Evaluación guardada con éxito', 'success')
        return redirect(url_for('evaluador.index', licitacion_id=licitacion_id))

    # GET: preparar datos para la vista
    lic = get_licitacion_logic(db, licitacion_id)
    # Convertir filas a dicts para permitir asignaciones
    raw_ofertas = list_ofertas_admitidas_logic(current_app, licitacion_id)
    ofertas = [dict(of) for of in raw_ofertas]
    # Filtrar criterios técnicos
    criterios = listar_tecnicos(current_app, licitacion_id)
    evaluaciones = obtener_evaluaciones(current_app, licitacion_id, usuario_id)

    # Mapa de evaluaciones existentes
    eval_map = {
        (e['licitante_id'], e['criterio_id']): e
        for e in evaluaciones
    }

    # Construir lista de criterios por oferta
    for oferta in ofertas:
        lista = []
        for c in criterios:
            key = (oferta['licitante_id'], c['id'])
            e = eval_map.get(key)
            score = e['puntuacion'] if e else 0
            lista.append({
                'id': c['id'],
                'nombre': c['NombreCriterio'],
                'peso': c['peso'],
                'puntuacion': score,
                'comentarios': e['comentarios'] if e else '',
                'total': score * c['peso']
            })
        oferta['criterios_evaluacion'] = lista

    return render_template('evaluador/evaluar.html', lic=lic, ofertas=ofertas)

@evaluador_bp.route('/<int:licitacion_id>/informe_tecnico', methods=['GET'])
def informe_tecnico(licitacion_id):
    if 'user_id' not in session or session.get('role_id') != 3:
        return redirect(url_for('auth.login'))

    db = get_db(current_app)
    # Obtener datos de licitación (ajusta a tu propia función)
    lic = obtener_licitacion_por_id(db, licitacion_id)
    # Generar y obtener datos del informe (siempre sobrescribe previos)
    informe, evaluadores = generar_informe_tecnico(current_app, licitacion_id)
    # Obtener ofertas para encabezados de columna
    raw_ofertas = list_ofertas_admitidas_logic(db, licitacion_id)  # ajusta a tu función
    ofertas = [dict(of) for of in raw_ofertas]

    return render_template(
        'evaluador/informe_tecnico.html',
        lic=lic,
        informe=informe,
        evaluadores=evaluadores,
        ofertas=ofertas
    )
