# Detección de Olores de Código y Selección de Patrones — San Camilo en Línea

## 1. Medición Inicial con `radon` (`src/pedidos/antes/servicio.py`)

```text
$ radon cc -s -a src/pedidos/antes/servicio.py
src/pedidos/antes/servicio.py
    M 33:4 ServicioPedidos.confirmar_y_pagar - C (16)
    C 25:0 ServicioPedidos - B (10)
    M 89:4 ServicioPedidos.normalizar_producto - B (7)

3 blocks (classes, functions, methods) analyzed.
Average complexity: B (11.0)
```

## 2. Análisis de Olores (Prompt IA 1) y Decisión del Equipo

| Líneas (`antes/servicio.py`) | Olor de Código Detectado (Fowler) | Patrón GoF Propuesto por la IA | Principio SOLID que Mejora | Costo / Trade-off | Decisión del Equipo y Justificación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L43–44 y L61–80** | **Condicionales por variante (`Switch Statements`):** `if/elif` por cada medio de pago (`YAPE`, `PLIN`) y por tarifa de modalidad (`RECOJO`, `DELIVERY`, `EXPRESS`). | **Strategy + Factory Method (registro)** | **O** (Open/Closed) y **D** (Dependency Inversion) | +3 clases nuevas e indirección al instanciar. | **Aceptado:** Cumple directamente con `QA-03` de `drivers.md` (integrar Plin u otra pasarela en <= 2 días sin modificar `ServicioPedidos`). |
| **L64 y L73** | **Acoplamiento a SDKs externos (`Inappropriate Intimacy`):** El servicio conoce que Yape recibe `(celular, soles)` y devuelve un `dict`, mientras Plin recibe `(centimos, celular)` y devuelve una `tuple`. | **Adapter** | **D** (Dependency Inversion) e **I** (Interface Segregation) | +1 clase adaptadora por cada SDK externo. | **Aceptado:** Aísla el dominio detrás del puerto `PasarelaPago` definido en el Lab 05 (`paquetes.puml`). |
| **L62–79** | **Código duplicado (`Duplicated Code`):** El bucle `for intento in range(3)` con captura de `TimeoutError` se repite idéntico en Yape y Plin. | **Decorator** (`ConReintentos`) | **S** (Single Responsibility) y **O** (Open/Closed) | +1 clase envoltorio que implementa `PasarelaPago`. | **Aceptado:** Crítico para `R-04` y `QA-02` (redes móviles 3G inestables en el Mercado San Camilo). |
| **L34–40, L59, L82–88** | **Condicionales complejos sobre estado (`Primitive Obsession / State Checking`):** Múltiples `if pedido.estado != "BORRADOR"` anidados para validar transiciones. | **State** (`EstadoPedido`) | **S** (Single Responsibility) y **L** (Liskov Substitution) | +5 clases de estado (`EstadoPedido`, `Borrador`, `Confirmado`, `Pagado`, `Cancelado`). | **Aceptado:** Implementa limpiamente la máquina de estados del pedido multipuesto diseñada en el Lab 05. |
| **L84–87** | **Responsabilidades mezcladas al notificar (`Divergent Change`):** `confirmar_y_pagar` itera sobre los puestos del mercado para armar mensajes de WhatsApp y líneas de reporte manualmente. | **Observer** (`PublicadorEventos`) | **S** (Single Responsibility) y **O** (Open/Closed) | +3 clases (`PublicadorEventos`, `NotificadorWhatsAppComerciantes`, `ActualizadorReportes`). | **Aceptado:** Desacopla el pago del envío de avisos a comerciantes (`RF-04`) y del módulo de reportes. |
| **L90–113** | **Lógica de caché y validaciones secuenciales acopladas (`Long Method`):** `normalizar_producto` mezcla caché en memoria y 3 validaciones de salida del LLM. | **Strategy + Adapter + Decorator (`ConCache`) + Chain of Responsibility (`Guardrail`)** | **S** (Single Responsibility) y **O** (Open/Closed) | +6 clases en `ia.py`. | **Aceptado:** Permite probar la normalización de catálogo (`QA-01`) sin API Key real y encadenar reglas contra alucinaciones del LLM. |
| **N/A (Sugerencia extra de IA)** | *"Garantizar una única instancia global de `FabricaPasarelas` y `PublicadorEventos` en toda la app."* | **Singleton** | Ninguno (viola bajo acoplamiento) | Introduce estado global compartido entre tests. | **Rechazado:** Dificulta la inyección de `YapeSDK(fallas=2)` en `pytest` y acopla las pruebas entre sí. Se usa inyección de dependencias por constructor. |
| **N/A (Sugerencia extra de IA)** | *"Crear familias de objetos (Pasarela + Notificador + Moneda) por país usando `Abstract Factory`."* | **Abstract Factory** | Open/Closed | +4 interfaces y fábricas abstractas innecesarias. | **Rechazado (Patternitis):** San Camilo en Línea opera únicamente en Arequipa (moneda única en Soles); aplicar `Abstract Factory` excede el alcance del MVP de 1 mes (`R-01`). |