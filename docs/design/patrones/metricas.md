# Métricas de Refactorización y Análisis de Trade-off — San Camilo en Línea

## 1. Comparación de Complejidad Ciclomática (`radon cc -s -a`) y Tamaño (`radon raw`)

| Métrica / Bloque Evaluado | Versión `antes` (`antes/servicio.py`) | Versión `después` (Módulos con Patrones) | Variación / Impacto |
| :--- | :---: | :---: | :--- |
| **Método `ServicioPedidos.confirmar_y_pagar()`** | **16 (Grado C)** | **2 (Grado A)** | **-87,5% de complejidad** (pasa de método riesgoso a método trivial de 10 líneas). |
| **Método `ServicioPedidos.normalizar_producto()`** | **7 (Grado B)** | **1 (Grado A)** | **-85,7% de complejidad** (delega en `NormalizadorProductos` y cadena de `Guardrail`). |
| **Complejidad promedio del código (`Average complexity`)** | **11,00 (Grado C)** | **1,54 (Grado A)** | Ningún método en toda la versión refactorizada supera una complejidad de **3 (Grado A)**. |
| **Índice de Mantenibilidad (`radon mi`)** | **58,4 (Grado A - Moderado)** | **84,2 promedio (Grado A - Alto)** | Alta legibilidad y cohesión por archivo. |
| **Líneas de código efectivas (SLOC)** | **96 SLOC** | **248 SLOC** (distribuidas en 5 archivos) | **+158% en líneas de código** debido a interfaces explícitas y clases pequeñas. |
| **Archivos del módulo** | **1 archivo** (`antes/servicio.py`) | **5 archivos** (`servicio.py`, `pagos.py`, `estados.py`, `eventos.py`, `ia.py`) | Mayor modularidad alineada con la responsabilidad única (SRP). |
| **Métodos de `ServicioPedidos` a modificar para agregar otro medio de pago o suscriptor** | **2 métodos** (`__init__` y `confirmar_y_pagar`) | **0 métodos** (se registra desde fuera con `fabrica.registrar()` o `publicador.suscribir()`) | Cumplimiento estricto del Principio Abierto/Cerrado (OCP). |

---

## 2. Análisis Honesto del Trade-off (5 a 8 líneas)

Con el refactor hacia patrones GoF ganamos una reducción drástica de la complejidad ciclomática en el flujo crítico `confirmar_y_pagar` (de **16 [C]** a **2 [A]**) y en `normalizar_producto` (de **7 [B]** a **1 [A]**), reduciendo el promedio global de **11,0 a 1,54**. Además, logramos extensibilidad real (`QA-03`): hoy podemos registrar una nueva pasarela (como Culqi QR o Plin), añadir un nuevo suscriptor (como alertas al repartidor) o cambiar el modelo de lenguaje sin editar una sola línea de `ServicioPedidos`. El costo pagado por esta flexibilidad es que el volumen de código creció de **96 a 248 SLOC** y pasó de **1 a 5 archivos**, introduciendo capas de indirección que exigen que los 3 integrantes del equipo conozcan los patrones aplicados. Si **San Camilo en Línea** fuera un script descartable que solo cobrara con Yape en modalidad de recojo en tienda y jamás integrara IA ni nuevos canales de aviso, la versión `antes` de 96 líneas habría sido suficiente y más rápida de leer de corrido. Sin embargo, dado que nuestros drivers arquitectónicos exigen soportar múltiples pasarelas (`QA-03`), tolerar fallas en redes 3G (`R-04`) y normalizar catálogos con IA, el costo adicional está plenamente justificado.

---

## 3. Patrones Rechazados y Justificación

1. **Singleton (Rechazado en `FabricaPasarelas` y `PublicadorEventos`):**
   * **Por qué lo sugirió la IA:** Para asegurar un único punto de registro de pasarelas y eventos en toda la aplicación.
   * **Por qué lo rechazamos:** Introduce estado global oculto que contamina las pruebas automatizadas en `pytest` (un suscriptor o un SDK con fallas inyectado en un test afectaría al siguiente test). Preferimos inyección de dependencias explícita en el constructor de `ServicioPedidos`.
2. **Abstract Factory (Rechazado para la creación de pasarelas y notificadores):**
   * **Por qué lo sugirió la IA:** Para instanciar familias completas de objetos (`PasarelaPago` + `Notificador` + `CalculadorImpuestos`) según la región.
   * **Por qué lo rechazamos:** Es un caso clásico de *patternitis* (sobreingeniería). El Mercado San Camilo opera en una única sede en Arequipa bajo una misma moneda y normativa; un `Factory Method` basado en diccionario resuelve la creación con una fracción de la complejidad.