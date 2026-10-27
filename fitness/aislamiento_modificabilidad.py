"""Prototipo y simulación cuantitativa para la Iteración 1 de ADD (QA-01 y QA-02):
Aislamiento multimercado (RLS) y Reglas de negocio parametrizadas en BD (San Camilo, Altiplano, Río Seco).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfiguracionMercado:
    mercado_id: str
    nombre: str
    tarifa_base_delivery: float
    recargo_por_puesto_extra: float
    tope_lineas_pedido: int
    activo: bool = True


class MotorMultimercado:
    """Implementa dos tácticas arquitectónicas:
    1. Seguridad (Limitar acceso / RLS simulado): toda consulta exige contexto de tenant (mercado_id del JWT).
    2. Modificabilidad (Diferir el enlace / Configuración en BD): tarifas y reglas por mercado en tabla, no en código.
    """

    def __init__(self, rls_activo: bool = True):
        self.rls_activo = rls_activo
        self._configuraciones: dict[str, ConfiguracionMercado] = {
            "SAN_CAMILO": ConfiguracionMercado("SAN_CAMILO", "Mercado San Camilo", 5.00, 1.00, 15),
            "ALTIPLANO": ConfiguracionMercado("ALTIPLANO", "Mercado Altiplano", 6.50, 1.50, 10),
            "RIO_SECO": ConfiguracionMercado("RIO_SECO", "Mercado Mayorista Río Seco", 8.00, 0.50, 25),
        }
        self._pedidos_bd: list[dict] = [
            {"id": 1, "mercado_id": "SAN_CAMILO", "puesto": "Puesto 12", "total": 35.0},
            {"id": 2, "mercado_id": "SAN_CAMILO", "puesto": "Puesto 45", "total": 50.0},
            {"id": 3, "mercado_id": "ALTIPLANO", "puesto": "Puesto A-04", "total": 42.0},
            {"id": 4, "mercado_id": "RIO_SECO", "puesto": "Puesto Mayorista 09", "total": 180.0},
        ]

    def registrar_mercado_en_bd(self, config: ConfiguracionMercado) -> None:
        """QA-02: Incorpora un nuevo mercado insertando una fila de configuración sin tocar el código."""
        self._configuraciones[config.mercado_id] = config

    def consultar_pedidos(self, jwt_mercado_id: str) -> list[dict]:
        """QA-01: Simula política RLS de PostgreSQL (WHERE mercado_id = current_setting('app.mercado_id'))."""
        if not self.rls_activo:
            return list(self._pedidos_bd)
        if not jwt_mercado_id or jwt_mercado_id not in self._configuraciones:
            raise PermissionError("Token JWT sin claim 'mercado_id' válido")
        return [p for p in self._pedidos_bd if p["mercado_id"] == jwt_mercado_id]

    def calcular_tarifa_mercado(self, mercado_id: str, num_puestos: int) -> float:
        """QA-02: Calcula la tarifa según los parámetros almacenados en BD para ese mercado."""
        if mercado_id not in self._configuraciones:
            raise ValueError(f"Mercado no configurado: {mercado_id}")
        cfg = self._configuraciones[mercado_id]
        extras = max(0, num_puestos - 1)
        return round(cfg.tarifa_base_delivery + (extras * cfg.recargo_por_puesto_extra), 2)


def evaluar_escenarios_iteracion_1() -> dict:
    # Caso A (Antes / Sin RLS): un comerciante de Altiplano ve pedidos de otros mercados
    motor_sin_rls = MotorMultimercado(rls_activo=False)
    filas_sin_rls = motor_sin_rls.consultar_pedidos("ALTIPLANO")
    fugas_sin_rls = sum(1 for p in filas_sin_rls if p["mercado_id"] != "ALTIPLANO")

    # Caso B (Después / Con RLS): 0 filas ajenas expuestas
    motor_con_rls = MotorMultimercado(rls_activo=True)
    filas_con_rls = motor_con_rls.consultar_pedidos("ALTIPLANO")
    fugas_con_rls = sum(1 for p in filas_con_rls if p["mercado_id"] != "ALTIPLANO")

    # Caso C (QA-02): Incorporar un 4to mercado ("Mercado Zamácola") en caliente sin desplegar código
    motor_con_rls.registrar_mercado_en_bd(
        ConfiguracionMercado("ZAMACOLA", "Mercado Zamácola", 6.00, 1.00, 12)
    )
    tarifa_zamacola = motor_con_rls.calcular_tarifa_mercado("ZAMACOLA", num_puestos=3)

    return {
        "fugas_sin_rls": fugas_sin_rls,
        "fugas_con_rls": fugas_con_rls,
        "tarifa_san_camilo_3puestos": motor_con_rls.calcular_tarifa_mercado("SAN_CAMILO", 3),
        "tarifa_altiplano_3puestos": motor_con_rls.calcular_tarifa_mercado("ALTIPLANO", 3),
        "tarifa_rio_seco_3puestos": motor_con_rls.calcular_tarifa_mercado("RIO_SECO", 3),
        "tarifa_nuevo_mercado_zamacola": tarifa_zamacola,
        "lineas_codigo_modificadas_para_nuevo_mercado": 0,
    }


if __name__ == "__main__":
    res = evaluar_escenarios_iteracion_1()
    print("=== EVIDENCIA CUANTITATIVA ITERACIÓN 1 (QA-01 y QA-02) ===")
    for k, v in res.items():
        print(f"  {k}: {v}")