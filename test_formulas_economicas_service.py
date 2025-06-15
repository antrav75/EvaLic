
import pytest
from services.formulas_economicas_service import (
    inversa_proporcional,
    proporcional_baja_con_presupuesto,
    reparto_proporcional,
    es_oferta_anormalmente_baja
)

# --- Tests para inversa_proporcional ---
def test_inversa_proporcional_valida():
    assert inversa_proporcional(100, 50, 50) == 100.0
    assert inversa_proporcional(100, 100, 50) == 50.0
    assert inversa_proporcional(100, 75.5, 50.5) == pytest.approx(66.56, rel=1e-2)

def test_inversa_proporcional_invalidos():
    assert inversa_proporcional(0, 50, 50) is None
    assert inversa_proporcional(100, 0, 50) is None
    assert inversa_proporcional(100, 50, 0) is None
    assert inversa_proporcional(100, 'a', 50) is None

# --- Tests para proporcional_baja_con_presupuesto ---
def test_proporcional_baja_con_presupuesto_valida():
    resultado = proporcional_baja_con_presupuesto(100, 80000, 70000, 100000)
    assert resultado == pytest.approx(66.67, rel=1e-2)

def test_proporcional_baja_con_presupuesto_invalidos():
    assert proporcional_baja_con_presupuesto(0, 80000, 70000, 100000) is None
    assert proporcional_baja_con_presupuesto(100, 80000, 70000, 0) is None
    assert proporcional_baja_con_presupuesto(100, -10, 70000, 100000) is None
    assert proporcional_baja_con_presupuesto(100, 100000, 100000, 100000) is None

def test_proporcional_baja_con_presupuesto_limites():
    assert proporcional_baja_con_presupuesto(100, 100000, 120000, 100000) == 0.0
    assert proporcional_baja_con_presupuesto(100, 90000, 110000, 95000) is None
    assert proporcional_baja_con_presupuesto(100, 100000.5, 110000.5, 100000.0) == pytest.approx(0.005, rel=1e-3)

# --- Tests para reparto_proporcional ---
def test_reparto_proporcional_valido():
    ofertas = [120000, 130000, 110000]
    resultado = reparto_proporcional(100, ofertas, 100000)
    assert len(resultado) == 3
    assert sum(resultado) == pytest.approx(100.0, rel=1e-2)

def test_reparto_proporcional_base_cero():
    assert reparto_proporcional(100, [120000, 130000], 0) == [None, None]

def test_reparto_proporcional_todas_invalidas():
    assert reparto_proporcional(100, [], 100000) == []

def test_reparto_proporcional_limites():
    assert reparto_proporcional(100, [120000], 100000) == [100.0]
    resultado = reparto_proporcional(100, [120000, "abc", 130000], 100000)
    assert resultado[0] == pytest.approx(40.0, rel=1e-2)
    assert resultado[1] == 0.0
    assert resultado[2] == pytest.approx(60.0, rel=1e-2)
    resultado_iguales = reparto_proporcional(100, [120000, 120000, 120000], 100000)
    for r in resultado_iguales:
        assert r == pytest.approx(33.33, rel=1e-2)

# --- Tests para es_oferta_anormalmente_baja ---
def test_es_oferta_anormalmente_baja_varias_ofertas():
    ofertas = [100000, 110000, 90000]
    assert es_oferta_anormalmente_baja(40000, ofertas) is True
    assert es_oferta_anormalmente_baja(80000, ofertas) is False

def test_es_oferta_anormalmente_baja_dos_ofertas():
    ofertas = [100000, 120000]
    assert es_oferta_anormalmente_baja(70000, ofertas) is True
    assert es_oferta_anormalmente_baja(95000, ofertas) is False

def test_es_oferta_anormalmente_baja_una_oferta_con_presupuesto():
    assert es_oferta_anormalmente_baja(40000, [100000], presupuesto_base=100000) is True
    assert es_oferta_anormalmente_baja(60000, [100000], presupuesto_base=100000) is False

def test_es_oferta_anormalmente_baja_datos_invalidos():
    assert es_oferta_anormalmente_baja(-10, [100000, 110000]) is False
    assert es_oferta_anormalmente_baja(50000, [100000], presupuesto_base=100000) is True

def test_es_oferta_anormalmente_baja_limites():
    assert es_oferta_anormalmente_baja(50000, [100000, 110000, 90000]) is True
    assert es_oferta_anormalmente_baja(50000, [100000]) is False
    assert es_oferta_anormalmente_baja(1, [2, 3, 4]) is True
