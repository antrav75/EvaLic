#!/usr/bin/env python3
"""
Fórmulas para evaluación de ofertas económicas:
 - inversa proporcional
 - proporcional por baja con presupuesto base
 - reparto proporcional
 - comprobación anormal baja Art.85 RGLCAP (umbral según nº ofertas)
"""

def inversa_proporcional(puntuacion_maxima, oferta, mejor_oferta):
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

    print(f"Descuento dividendo: {descuento_dividendo}, Descuento divisor: {descuento_divisor}")
    
    # Si el divisor es cero, no podemos dividir
    if descuento_divisor != 0:
        resultado = (descuento_dividendo / descuento_divisor) * pm
    else:
        return None
       
    # Si la fórmula da negativo (por seguridad), devolvemos None
    return resultado if resultado >= 0 else None

def reparto_proporcional(puntuacion_total, ofertas):
    try:
        pt = float(puntuacion_total)
    except (TypeError, ValueError):
        return [None for _ in (ofertas or [])]
    if pt <= 0:
        return [None for _ in ofertas]
    if not isinstance(ofertas, (list, tuple)) or not ofertas:
        return []
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
