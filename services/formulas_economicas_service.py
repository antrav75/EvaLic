"""
Módulo de fórmulas para evaluación de ofertas económicas.

Contiene implementaciones de:
 1. Fórmula inversa proporcional.
 2. Fórmula proporcional por baja con presupuesto base.
 3. Fórmula proporcional de reparto de puntos entre varias ofertas.
 4. Comprobación de oferta anormalmente baja según el Art.85 RGLCAP,
    adaptando el umbral en función del número de ofertas presentadas.

Cada función valida entradas para evitar divisiones por cero o valores no válidos.
En caso de error o entrada inválida, devuelve None (o False en la función de umbral).
"""

from datetime import datetime


def inversa_proporcional(puntuacion_maxima, oferta, mejor_oferta):
    """
    Cálculo de puntuación mediante fórmula inversa proporcional:
        score = (mejor_oferta / oferta) * puntuacion_maxima

    Validaciones:
      - Si alguno de los parámetros no es numérico o <= 0, devuelve None.

    Args:
        puntuacion_maxima (float): puntuación máxima asignable.
        oferta (float): precio de la oferta a evaluar.
        mejor_oferta (float): precio mínimo (mejor) entre todas las ofertas.

    Returns:
        float o None: puntuación obtenida, o None si hay entrada inválida.
    """
    try:
        pm = float(puntuacion_maxima)
        of = float(oferta)
        mo = float(mejor_oferta)
    except (TypeError, ValueError):
        return None

    if pm <= 0 or of <= 0 or mo <= 0:
        return None

    try:
        resultado = (mo / of) * pm
    except ZeroDivisionError:
        return None

    return resultado if resultado >= 0 else None


def proporcional_baja_con_presupuesto(puntuacion_maxima, oferta, presupuesto_base):
    """
    Cálculo de puntuación mediante fórmula proporcional por baja con presupuesto base:
        score = ((presupuesto_base - oferta) / presupuesto_base) * puntuacion_maxima

    Validaciones:
      - Si alguno de los parámetros no es numérico, devuelve None.
      - Si presupuesto_base <= 0, oferta < 0, o oferta >= presupuesto_base, o puntuacion_maxima <= 0,
        devuelve None.

    Args:
        puntuacion_maxima (float): puntuación máxima asignable.
        oferta (float): precio de la oferta a evaluar.
        presupuesto_base (float): precio base o presupuesto de referencia.

    Returns:
        float o None: puntuación obtenida, o None si hay entrada inválida.
    """
    try:
        pm = float(puntuacion_maxima)
        of = float(oferta)
        pb = float(presupuesto_base)
    except (TypeError, ValueError):
        return None

    if pm <= 0 or pb <= 0 or of < 0 or of >= pb:
        return None

    try:
        descuento = pb - of
        resultado = (descuento / pb) * pm
    except ZeroDivisionError:
        return None

    return resultado if resultado >= 0 else None


def reparto_proporcional(puntuacion_total, ofertas):
    """
    Reparto proporcional de puntos entre varias ofertas. Cada oferta i recibe:
        score_i = ((min_oferta / oferta_i) / sum_j(min_oferta / oferta_j)) * puntuacion_total

    Validaciones:
      - Si puntuacion_total no es numérico o <= 0, devuelve lista de None.
      - Si ofertas no es lista o está vacía, devuelve lista vacía.
      - Si ninguna oferta válida (> 0), devuelve lista de None.
      - Evita división por cero si suma de factores es 0, devolviendo None.

    Args:
        puntuacion_total (float): total de puntos a repartir.
        ofertas (list of float): lista de precios de las ofertas.

    Returns:
        list de float o None: puntuaciones asignadas en el mismo orden que 'ofertas';
                               cada elemento es None si ocurre error en el cálculo.
    """
    try:
        pt = float(puntuacion_total)
    except (TypeError, ValueError):
        return [None for _ in (ofertas or [])]

    if pt <= 0:
        return [None for _ in ofertas]

    if not isinstance(ofertas, (list, tuple)) or not ofertas:
        return []

    # Filtrar ofertas > 0 y convertir a float
    validas = []
    for o in ofertas:
        try:
            v = float(o)
            if v > 0:
                validas.append(v)
        except (TypeError, ValueError):
            continue

    if not validas:
        return [None for _ in ofertas]

    min_oferta = min(validas)

    factores = []
    for o in ofertas:
        try:
            v = float(o)
            if v > 0:
                factores.append(min_oferta / v)
            else:
                factores.append(0.0)
        except (TypeError, ValueError):
            factores.append(0.0)

    suma_factores = sum(factores)
    if suma_factores <= 0:
        return [None for _ in ofertas]

    scores = []
    for f in factores:
        try:
            score_i = (f / suma_factores) * pt
        except ZeroDivisionError:
            scores.append(None)
            continue
        scores.append(score_i if score_i >= 0 else None)

    return scores


def es_oferta_anormalmente_baja(oferta, ofertas_ponderadas, presupuesto_base=None):
    """
    Comprueba si una oferta es anormalmente baja según el Art.85 RGLCAP,
    ajustando el umbral en función del número de ofertas presentadas:

      - Si hay 3 o más ofertas válidas (> 0): umbral = 0.50 * media_aritmética.
      - Si hay exactamente 2 ofertas válidas:      umbral = 0.75 * media_aritmética.
      - Si hay solo 1 oferta válida:               umbral = 0.50 * presupuesto_base (si se proporciona).
      - En cualquier otro caso (por ejemplo, sin presupuesto_base cuando solo 1 oferta),
        devuelve False.

    Validaciones:
      - Si oferta no es numérico o <= 0, devuelve False.
      - ofertas_ponderadas debe ser iterable; se filtran <= 0.
      - Si no hay ofertas comparables válidas (> 0), devuelve False.
      - Si solo hay 1 oferta y no se pasa presupuesto_base > 0, devuelve False.

    Args:
        oferta (float): precio de la oferta a evaluar.
        ofertas_ponderadas (iterable of float): lista de precios de otras ofertas.
        presupuesto_base (float | None): precio base de referencia (solo se usa si hay 1 oferta).

    Returns:
        bool: True si la oferta es anormalmente baja; False en caso contrario o error.
    """
    # Validar oferta
    try:
        of = float(oferta)
    except (TypeError, ValueError):
        return False
    if of <= 0:
        return False

    # Filtrar ofertas ponderadas válidas (> 0)
    validas = []
    if isinstance(ofertas_ponderadas, (list, tuple)):
        for o in ofertas_ponderadas:
            try:
                v = float(o)
                if v > 0:
                    validas.append(v)
            except (TypeError, ValueError):
                continue

    count = len(validas)
    if count == 0:
        return False

    # Calcular media aritmética
    try:
        media = sum(validas) / count
    except ZeroDivisionError:
        return False

    # Determinar umbral según número de ofertas válidas
    if count >= 3:
        threshold = 0.50 * media
    elif count == 2:
        threshold = 0.75 * media
    else:  # count == 1
        try:
            pb = float(presupuesto_base)
        except (TypeError, ValueError):
            return False
        if pb <= 0:
            return False
        threshold = 0.50 * pb

    # Comparar
    return of <= threshold