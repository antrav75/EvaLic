from models.criterios_data import (
    list_criterios, get_criterio, create_criterio,
    edit_criterio, delete_criterio,
    list_tipo_criterios, list_formulas
)

def listar(db, lic_id):
    return list_criterios(db, lic_id)

def obtener(db, crit_id):
    return get_criterio(db, crit_id)

def crear(db, data, usuario_id):
    # Calculamos peso (0 si no se envía) y fórmula (None si no aplica)
    peso = int(data.get('Peso') or 0)
    tip_id = int(data['tipocriterio_id'])
    formula = int(data.get('formula_id')) if data.get('formula_id') else None

    create_criterio(
        db,
        data['NombreCriterio'],
        data.get('Descripcion'),
        peso,
        tip_id,
        int(data['licitacion_id']),
        formula
    )

def actualizar(db, crit_id, data):
    # Calculamos peso (0 si no se envía) y fórmula (None si no aplica)
    peso = int(data.get('Peso') or 0)
    tip_id = int(data['tipocriterio_id'])
    formula = int(data.get('formula_id')) if data.get('formula_id') else None

    edit_criterio(
        db,
        crit_id,
        data['NombreCriterio'],
        data.get('Descripcion'),
        peso,
        tip_id,
        formula
    )

def borrar(db, crit_id):
    delete_criterio(db, crit_id)

def tipos(db):
    return list_tipo_criterios(db)

def formulas(db):
    return list_formulas(db)
