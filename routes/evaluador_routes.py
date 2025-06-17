from flask import Blueprint, render_template, session, redirect, url_for, current_app, request, flash
from services.evaluaciones_service import listar_por_evaluador
from services.oferta_service import list_ofertas_admitidas_logic
from services.licitacion_service import get_licitacion as get_licitacion_logic

from services.evaluaciones_service import obtener_evaluaciones, guardar_evaluacion
from services.criterio_service import listar_tecnicos, listar_economicos
from services.resultados_service import generar_informe
from services.licitacion_service import obtener_licitacion_por_id

# Importamos el nuevo servicio
from services.licitante_service import listar_licitantes_por_licitacion as list_licitantes
from datetime import datetime
from math import ceil

evaluador_bp = Blueprint('evaluador', __name__, url_prefix='/evaluador')
evaluador_bp.route('/<int:licitacion_id>/evaluar', methods=['GET', 'POST'])

@evaluador_bp.route('/', methods=('GET',))
def index():
    if 'user_id' not in session or session.get('role_id') != 3:
        return redirect(url_for('auth.login'))

    
    user_id = session.get('user_id')

    licitaciones = listar_por_evaluador( session['user_id'])

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
    per_page = current_app.config.get('LIC_PER_PAGE', 5)
    total = len(licitaciones)
    total_pages = ceil(total / per_page) if total else 1
    start = (page - 1) * per_page
    end = start + per_page
    licitaciones = licitaciones[start:end]
    
    return render_template(
        'evaluador/index.html',
        licitaciones=licitaciones,
        total_pages=total_pages,
        current_page=page,
        request=request
    )


@evaluador_bp.route('/<int:licitacion_id>/evaluar', methods=['GET', 'POST'])
def evaluar(licitacion_id):
    # Autenticación y contexto
    if 'user_id' not in session or session.get('role_id') != 3:
        return redirect(url_for('auth.login'))

    usuario_id = session['user_id']
    #db = get_db(current_app)

    # POST: guardar o actualizar evaluaciones
    if request.method == 'POST':
        ofertas = list_ofertas_admitidas_logic(licitacion_id)
        # Filtrar solo criterios técnicos
        criterios = listar_tecnicos(licitacion_id)
        for oferta in ofertas:
            licitante_id = oferta['licitante_id']
            for c in criterios:
                crit_id = c['id']
                puntuacion = request.form.get(f'puntuacion_{licitante_id}_{crit_id}', 0)
                comentarios = request.form.get(f'comentarios_{licitante_id}_{crit_id}', '').strip()

                # y la guardamos en la BD
                guardar_evaluacion(
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
    lic = get_licitacion_logic(licitacion_id)
    # Convertir filas a dicts para permitir asignaciones
    raw_ofertas = list_ofertas_admitidas_logic(licitacion_id)
    ofertas = [dict(of) for of in raw_ofertas]
    # Filtrar criterios técnicos
    criterios = listar_tecnicos(licitacion_id)
    evaluaciones = obtener_evaluaciones(licitacion_id, usuario_id)

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


licitaciones_bp = Blueprint('evaluador', __name__, url_prefix='/evaluador')

@evaluador_bp.route('/<int:licitacion_id>/informe', methods=['GET'])
def informe(licitacion_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    #db = get_db(current_app)

    # 1) Recuperar datos de la licitación si los necesitas
    lic = obtener_licitacion_por_id(licitacion_id)

    # 2) Generar resultados técnicos + económicos
    informe_rows, evaluadores, totals = generar_informe(licitacion_id)

    # 3) Solo licitantes que participaron
    raw_ofertas = list_ofertas_admitidas_logic(licitacion_id)
    # <-- Aquí ajustamos para que cada dict tenga "id" en lugar de "licitante_id"
    ofertas = [
        {'id': o['licitante_id'], 'nombreempresa': o['nombreempresa']}
        for o in raw_ofertas
    ]

    # 4) Cargar criterios técnicos y económicos (igual que antes)
    criterios_tecnicos = []
    for c in listar_tecnicos(licitacion_id):
        criterios_tecnicos.append({
            'criterio_id': c['id'],
            'nombre_criterio': c['NombreCriterio']
        })

    criterios_economicos = []
    for c in listar_economicos(licitacion_id):
        criterios_economicos.append({
            'criterio_id': c['id'],
            'nombre_criterio': c['NombreCriterio']
        })

    # 5) Renderizar el informe pasándole todas las variables necesarias
    return render_template(
        'evaluador/informe.html',
        lic=lic,
        informe=informe_rows,
        evaluadores=evaluadores,
        ofertas=ofertas,
        criterios_tecnicos=criterios_tecnicos,
        criterios_economicos=criterios_economicos,
        totals=totals,
    )