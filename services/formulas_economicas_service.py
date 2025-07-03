#!/usr/bin/env python3
"""
Fórmulas para evaluación de ofertas económicas:
 - inversa proporcional
 - proporcional por baja con presupuesto base
 - reparto proporcional
 - comprobación anormal baja Art.85 RGLCAP (umbral según nº ofertas)
"""

# Función: inversa_proporcional
# Parámetros:
#   puntuacion_maxima (número): Es la puntuación máxima que se puede conceder a una oferta.
#   oferta (número): Es el valor económico que oferta una empresa licitante 
#   mejor_oferta (número): Es el valor de la mejor oferta realizada en la licitación.
# Descripción: Esta función calcula en base a la formula proporcional inversa la puntuación
#              que obtiene una oferta determinada en un criterio económico. 
# Retorna: resultado (número) si es mayor que 0
def inversa_proporcional(puntuacion_maxima, oferta, mejor_oferta):
    try:
        pm = float(puntuacion_maxima)
        of = float(oferta)
        mo = float(mejor_oferta)
    except (TypeError, ValueError):
        return None
    # - Validación inicial-
    # Se controla que los valores no sean 0, espcialmente of para que no se produzca una división por cero
    if pm <= 0 or of <= 0 or mo <= 0:
        return None
    try:
        resultado = (mo / of) * pm
    except ZeroDivisionError:
        return None
    return resultado if resultado >= 0 else None

# Función: proporcional_baja_con_presupuesto
# Parámetros:
#   puntuacion_maxima (número): Es la puntuación máxima que se puede conceder a una oferta.
#   oferta (número): Es el valor económico que oferta una empresa licitante 
#   mejor_oferta (número): Es el valor de la mejor oferta realizada en la licitación.
#   presupuesto_base (número): Es el presupuesto base (El mínimo que se puede ofertar)
# Descripción: Esta función calcula en base a la formula proporcional a la baja con presupuesto base 
#              la puntuación que obtiene una oferta determinada en un criterio económico. 
# Retorna: resultado (número) si es mayor que 0
def proporcional_baja_con_presupuesto(puntuacion_maxima, oferta, mejor_oferta, presupuesto_base):
    try:
        pm = float(puntuacion_maxima)
        of = float(oferta)
        pb = float(presupuesto_base)
        mo = float(mejor_oferta)
    except (TypeError, ValueError):
        return None

    # — Validaciones iniciales —
    # 1) La puntuación máxima y el presupuesto base deben ser positivos
    if pm <= 0 or pb <= 0:
        return None

    # 2) La mejor oferta (mo) debe ser positiva 
    if  mo <= 0:
        return None

    # 3) La oferta (of) debe ser positiva
    if of <= 0:
        return None

    # — Cálculo principal —
    descuento_dividendo = of - pb      
    descuento_divisor  = mo - pb     

    #print(f"Descuento dividendo: {descuento_dividendo}, Descuento divisor: {descuento_divisor}")
    
    # Si el divisor es cero, no podemos dividir
    if descuento_divisor != 0:
        resultado = (descuento_dividendo / descuento_divisor) * pm
    else:
        return None
       
    # Si la fórmula da negativo (por seguridad), devolvemos None
    return resultado if resultado >= 0 else None

# Función: reparto_proporcional
# Parámetros:
#   puntuacion_total (número): Es la puntuación total que se pueden obtener entre todas las ofertas.
#   ofertas (lista): Son las ofertas que se han presentado para evaluar. 
#   presupuesto_base (número): Es el presupuesto base (El mínimo que se puede ofertar)
# Descripción: Esta función calcula en base a la formula del reparto proporcional la puntuación
#              que obtiene una oferta determinada en un criterio económico. 
# Retorna: lista de resultados
def reparto_proporcional(puntuacion_total, ofertas, precio_base):
    """
    Reparte pto_total entre varias ofertas usando la fórmula inversa
    proporcional basada en la 'baja' (oferta - precio_base).
    """
    try:
        pt = float(puntuacion_total)
    except (TypeError, ValueError):
        return [None for _ in (ofertas or [])]
    if pt <= 0:
        return [None for _ in ofertas]
    if not isinstance(ofertas, (list, tuple)) or not ofertas:
        return []

    # Validación de precio_base
    try:
        pb = float(precio_base)
    except (TypeError, ValueError):
        return [None for _ in ofertas]
    if pb <= 0:
        return [None for _ in ofertas]

    # Cálculo de “bajas” = oferta_i – precio_base
    bajas = []
    for o in ofertas:
        try:
            v = float(o)
            bi = v - pb 
            bajas.append(bi if bi > 0 else 0.0)
        except (TypeError, ValueError):
            bajas.append(0.0)

    suma_bajas = sum(bajas)
    if suma_bajas <= 0:
        return [None for _ in ofertas]

    # Reparto proporcional: P_{o_i} = P_t * (b_i / Σ b_j)
    scores = []
    for bi in bajas:
        try:
            score_i = (bi / suma_bajas) * pt
        except ZeroDivisionError:
            scores.append(None)
            continue
        scores.append(score_i if score_i >= 0 else None)

    return scores

# Función: es_oferta_anormalmente_baja
# Parámetros:
#   oferta (número): Es el valor económico que oferta una empresa licitante
#   ofertas_ponderadas (lista): Son los valores de las puntuaciones de las ofertas ya ponderadas.
#   presupuesto_base (número): Es el presupuesto base (El mínimo que se puede ofertar)
# Descripción: Esta función calcula si una función se puede considerar anormalmente baja teniendo
#              en cuenta el valor de la oferta respecto a las demás ofertas y el presupuesto_base
#              siguiendo la fórmula descrita en el Art.85 RGLCAP.
# Retorna: verdadero (1) o falso (0)
def es_oferta_anormalmente_baja(oferta, ofertas_ponderadas, presupuesto_base=None):
    try:
        of = float(oferta)
    except (TypeError, ValueError):
        return False
    if of <= 0:
        return False
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
    try:
        media = sum(validas) / count
    except ZeroDivisionError:
        return False
    if count >= 3:
        threshold = 0.50 * media
    elif count == 2:
        threshold = 0.75 * media
    else:
        try:
            pb = float(presupuesto_base)
        except (TypeError, ValueError):
            return False
        if pb <= 0:
            return False
        threshold = 0.50 * pb
    return of <= threshold
