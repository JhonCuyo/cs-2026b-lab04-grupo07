# ADR-005: Adopción de Patrones de Diseño GoF en el Módulo de Pedidos e IA de Catálogo

* **Estado:** Aceptado
* **Fecha:** 2026-10-25
* **Decisores:** Grupo 07 (San Camilo en Línea)

## Contexto
En la primera implementación del flujo crítico `confirmar_y_pagar()` y de la función de normalización de nombres de productos con IA (`src/pedidos/antes/servicio.py`), el método principal alcanzó una complejidad ciclomática de **16 (Grado C en `radon`)** y un promedio de **11,0**. Agregar una nueva pasarela de pago (escenario `QA-03` de `drivers.md`), modificar las reglas de envío o integrar un nuevo canal de notificación obligaba a editar directamente `ServicioPedidos`, violando los principios SRP y OCP. Asimismo, el componente de IA para normalizar productos escritos por comerciantes en celulares de gama baja (`QA-01`) es no determinista y puede infiltrar precios falsos o afirmaciones no permitidas si no se aísla y valida.

## Alternativas Consideradas
1. **Mantener el diseño procedural con condicionales (`antes/servicio.py`):** Menor cantidad de líneas (96 SLOC en 1 archivo), pero alta complejidad ciclomática (16), código de reintentos duplicado y alto riesgo de regresión al agregar pasarelas o cambiar el proveedor de LLM.
2. **Refactorización pragmática hacia patrones GoF guiada por olores (Opción elegida):** Aplicar únicamente patrones justificados por un olor concreto y verificados con pruebas de caracterización.
3. **Sobreingeniería con `Abstract Factory` y `Singleton` (Propuesta inicial de IA rechazada):** Crear fábricas abstractas por región e instancias globales únicas; descartado por introducir estado global entre pruebas y complejidad innecesaria para el MVP de 1 mes (`R-01`).

## Decisión
Adoptamos siete patrones de diseño GoF dentro de `src/pedidos/`:
1. **Strategy + Adapter + Factory Method (registro)** en `pagos.py`: Puerto `PasarelaPago`, adaptadores `YapeAdapter` y `PlinAdapter`, `FabricaPasarelas` y estrategia de tarifas de envío.
2. **Decorator** en `pagos.py` (`ConReintentos` para fallas temporales de red 3G, `R-04`) y en `ia.py` (`ConCache` para evitar llamadas repetidas al LLM).
3. **State** en `estados.py`: Clases `EstadoPedido` (`Borrador`, `Confirmado`, `Pagado`, `Cancelado`) que hacen imposibles las transiciones inválidas por construcción.
4. **Observer** en `eventos.py`: `PublicadorEventos` con suscriptores desacoplados (`NotificadorWhatsAppComerciantes` y `ActualizadorReportes`).
5. **Chain of Responsibility** en `ia.py`: Cadena determinista de `Guardrail` (`SinPreciosInfiltrados -> SinAfirmacionesMedicas -> LongitudMaximaCatalogo`) combinada con `ProveedorLLM` (**Strategy/Adapter**).

Se rechazan explícitamente **Singleton** (para preservar la inyección limpia de dobles de prueba en `pytest`) y **Abstract Factory** (por ausencia de familias de productos multi-región).

## Consecuencias
* **Positivas:**
  * La complejidad ciclomática de `confirmar_y_pagar()` bajó de **16 (C) a 2 (A)** y el promedio global bajó de **11,0 a 1,54**.
  * Cumplimiento de `QA-03`: registrar una nueva pasarela o un nuevo suscriptor requiere **0 modificaciones** en `ServicioPedidos`.
  * El componente de IA es 100% probable en milisegundos sin clave de API ni conexión a internet mediante `ClienteLLMFalso`.
* **Negativas / Trade-offs:**
  * El código creció de **96 a 248 SLOC** distribuidas en **5 archivos**, aumentando el nivel de indirección que el equipo debe conocer y mantener.