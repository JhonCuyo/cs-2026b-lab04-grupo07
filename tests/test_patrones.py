"""Pruebas específicas que demuestran cada patrón de diseño GoF aplicado."""

import pytest
from src.pedidos.pagos import PasarelaPago, ResultadoPago
from src.pedidos.servicio import ServicioPedidos, Pedido, Linea
from src.pedidos.eventos import Suscriptor
from src.pedidos.pagos import ConReintentos, YapeAdapter
from src.pedidos.externos import YapeSDK
from src.pedidos.ia import LocalLlamaAdapter, ConCache, NormalizadorProductos
from src.pedidos.externos import ClienteLLMFalso


def crear_pedido_base() -> Pedido:
    return Pedido(
        id=201,
        celular="959000999",
        lineas=[Linea("Rocoto Relleno", 2, 12.50, puesto="Puesto 08 - Tradicional")],
    )


def test_e2_open_closed_nueva_pasarela_sin_modificar_servicio():
    class CulqiQRAdapter(PasarelaPago):
        def cobrar(self, monto: float, celular: str) -> ResultadoPago:
            return ResultadoPago(aprobado=True, operacion=f"CULQI-{int(monto)}")

    servicio = ServicioPedidos()
    servicio.fabrica.registrar("CULQI_QR", CulqiQRAdapter)

    pedido = crear_pedido_base()
    estado = servicio.confirmar_y_pagar(pedido, "CULQI_QR")

    assert estado == "PAGADO"
    assert pedido.operacion == "CULQI-25"

def test_e3_state_impide_pagar_sin_confirmar_o_cancelar_un_pedido_pagado():
    pedido = crear_pedido_base()
    # No se puede pagar directamente desde BORRADOR sin confirmar primero
    with pytest.raises(ValueError, match="No se puede pagar un pedido en estado BORRADOR"):
        pedido.pagar("YAPE-100")

    # Flujo válido: BORRADOR -> CONFIRMADO -> PAGADO
    pedido.confirmar()
    assert pedido.estado == "CONFIRMADO"
    pedido.pagar("YAPE-2500")
    assert pedido.estado == "PAGADO"

    # Una vez PAGADO no se puede cancelar ni volver a pagar
    with pytest.raises(ValueError, match="No se puede cancelar un pedido en estado PAGADO"):
        pedido.cancelar()

def test_e4_observer_nuevo_suscriptor_repartidor_sin_tocar_servicio():
    avisos_repartidor: list[str] = []

    class NotificadorRepartidor(Suscriptor):
        def actualizar(self, evento: str, datos: dict) -> None:
            avisos_repartidor.append(f"delivery:Pedido {datos['id']} listo en {len(datos['puestos'])} puestos")

    servicio = ServicioPedidos()
    servicio.publicador.suscribir("pedido_pagado", NotificadorRepartidor())

    pedido = crear_pedido_base()
    servicio.confirmar_y_pagar(pedido, "YAPE")

    assert avisos_repartidor == ["delivery:Pedido 201 listo en 1 puestos"]


def test_e4_decorator_con_reintentos_aisla_fallos_temporales_de_red():
    sdk_inestable = YapeSDK(fallas=2)
    pasarela_decorada = ConReintentos(YapeAdapter(sdk_inestable), intentos=3)

    resultado = pasarela_decorada.cobrar(45.0, "959123456")

    assert resultado.aprobado is True
    assert resultado.operacion == "YAPE-4500"
    assert sdk_inestable.llamadas == 3

def test_e5_decorator_cache_ia_evita_doble_llamada_al_llm():
    llm_falso = ClienteLLMFalso("Cebolla Roja Arequipeña (Kg)")
    normalizador = NormalizadorProductos(ConCache(LocalLlamaAdapter(llm_falso)))

    assert normalizador.normalizar("cebolla roja") == "Cebolla Roja Arequipeña (Kg)"
    assert normalizador.normalizar("  CEBOLLA ROJA  ") == "Cebolla Roja Arequipeña (Kg)"
    assert llm_falso.llamadas == 1


def test_e5_chain_of_responsibility_guardrails_bloquean_afirmaciones_y_exceso_longitud():
    # Caso 1: Afirmación médica prohibida
    normalizador_medico = NormalizadorProductos(
        LocalLlamaAdapter(ClienteLLMFalso("Miel de abeja que cura la gripe"))
    )
    with pytest.raises(ValueError, match="afirmación no permitida 'cura'"):
        normalizador_medico.normalizar("miel")

    # Caso 2: Nombre demasiado largo para pantalla de gama baja (> 60 chars)
    texto_largo = "Papa Amarilla Especial Extra Grande Seleccionada del Valle de Majes Arequipa"
    normalizador_largo = NormalizadorProductos(
        LocalLlamaAdapter(ClienteLLMFalso(texto_largo))
    )
    with pytest.raises(ValueError, match="excede 60 caracteres"):
        normalizador_largo.normalizar("papa")