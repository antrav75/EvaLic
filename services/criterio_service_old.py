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
    create_criterio(
        db,
        data['NombreCriterio'],
        data.get('Descripcion'),
        int(data.get('Peso') or 0),
        int(data['tipocriterio_id']),
        int(data['licitacion_id']),
        int(data['formula_id'])
    )

def actualizar(db, crit_id, data):
    edit_criterio(
        db,
        crit_id,
        data['NombreCriterio'],
        data.get('Descripcion'),
        int(data.get('Peso') or 0),
        int(data['tipocriterio_id']),
        int(data['formula_id'])
    )

def borrar(db, crit_id):
    delete_criterio(db, crit_id)

def tipos(db):
    return list_tipo_criterios(db)

def formulas(db):
    return list_formulas(db)
