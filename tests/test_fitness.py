"""Fitness functions automatizadas de calidad para San Camilo en Línea 2.0 (Lab 08)."""

import pytest
from fitness.aislamiento_modificabilidad import MotorMultimercado, ConfiguracionMercado
from fitness.rendimiento import simular as simular_rendimiento, con_cache, bd_con_indice
from fitness.disponibilidad import simular as simular_disponibilidad

PRESUPUESTO_P95_MS = 1500.0  # QA-03: p95 <= 1500 ms a 18 req/s (3 mercados)


def test_ff03_rendimiento_hora_punta_tres_mercados():
    """Verifica QA-03: con índice y caché, 18 req/s mantiene p95 <= 1500 ms."""
    r = simular_rendimiento(lam=18, workers=4, servicio=con_cache(bd_con_indice, hit_rate=0.85))
    assert r["p95"] <= PRESUPUESTO_P95_MS, f"Degradación de rendimiento: p95={r['p95']} ms > {PRESUPUESTO_P95_MS} ms"


def test_ff04_disponibilidad_cero_pedidos_perdidos_ante_caida_yape():
    """Verifica QA-04: con Reintentos + Circuit Breaker + Outbox se pierden 0 pedidos."""
    r = simular_disponibilidad("breaker")
    assert r["perdidos"] == 0, f"Se perdieron {r['perdidos']} pedidos durante la caída"


def test_ff05_circuit_breaker_protege_al_proveedor_caido():
    """Verifica QA-04: el Circuit Breaker reduce drásticamente las llamadas durante los 20 min de caída."""
    con_breaker = simular_disponibilidad("breaker")["llamadas_en_caida"]
    solo_reintentos = simular_disponibilidad("reintentos")["llamadas_en_caida"]
    assert con_breaker <= 20
    assert con_breaker < (solo_reintentos / 5)


def test_ff06_aislamiento_multimercado_rls_y_alta_sin_codigo():
    """Verifica QA-01 (0 filas filtradas entre mercados) y QA-02 (nuevo mercado por configuración)."""
    motor = MotorMultimercado(rls_activo=True)
    pedidos_altiplano = motor.consultar_pedidos("ALTIPLANO")
    assert all(p["mercado_id"] == "ALTIPLANO" for p in pedidos_altiplano)

    with pytest.raises(PermissionError):
        motor.consultar_pedidos("MERCADO_INEXISTENTE")

    motor.registrar_mercado_en_bd(ConfiguracionMercado("MIRAFLORES", "Mercado Miraflores", 5.50, 1.00, 12))
    assert motor.calcular_tarifa_mercado("MIRAFLORES", num_puestos=2) == 6.50