# Drivers Arquitectónicos - San Camilo en Línea

## 1. Requisitos Funcionales Clave
| ID | Requisito | Actor | Prioridad |
|---|---|---|---|
| RF-01 | Buscar y consultar catálogo de productos organizado por puesto del mercado. | Cliente | Alta |
| RF-02 | Realizar un pedido unificado con productos de múltiples puestos del mercado. | Cliente | Alta |
| RF-03 | Procesar el pago del pedido mediante la pasarela móvil Yape. | Cliente | Alta |
| RF-04 | Enviar confirmación del pedido y detalle de compra vía WhatsApp API al comerciante. | Sistema / Comerciante | Alta |
| RF-05 | Gestionar el estado de preparación y la asignación del pedido para recojo o delivery. | Comerciante / Repartidor | Media |

## 2. Atributos de Calidad (Ordenados por Prioridad)
1. **Capacidad de Interacción / Usabilidad (Atributo Crítico):** El sistema debe permitir a comerciantes con baja alfabetización digital publicar o actualizar productos en muy pocos pasos desde smartphones de gama baja.
2. **Eficiencia de Desempeño (Rendimiento en Redes Lentas):** La interfaz y las llamadas API deben estar optimizadas para operar eficientemente bajo conexiones móviles inestables o de baja velocidad (redes 3G).
3. **Modificabilidad:** La arquitectura debe permitir agregar nuevas pasarelas de pago o proveedores de envío sin alterar la lógica central de los módulos del sistema.
4. **Disponibilidad:** El sistema debe garantizar la captura y registro de pedidos incluso si el servicio externo de notificaciones (WhatsApp API) experimenta caídas temporales.

## 3. Restricciones
| ID | Tipo | Restricción |
|---|---|---|
| R-01 | Plazo | Licitación de MVP funcional desplegado en producción en máximo 1 mes. |
| R-02 | Equipo | Equipo de desarrollo conformado por 3 estudiantes con conocimientos en tecnologías web/móviles. |
| R-03 | Presupuesto | Presupuesto limitado; se debe emplear un servidor VPS económico de un solo nodo para el MVP. |
| R-04 | Entorno del Usuario | Dispositivos móviles de gama baja y conectividad 3G/intermitente para los comerciantes del mercado. |

## 4. Escenarios de Atributos de Calidad
| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida |
|---|---|---|---|---|---|---|---|
| QA-01 | Capacidad de Interacción | Comerciante | Intenta publicar un nuevo producto en su puesto | Operación normal desde un celular de gama baja | Módulo de Catálogo / PWA | La interfaz guía al usuario con un flujo simplificado | Publicación completada en $\le 3$ toques en la pantalla |
| QA-02 | Rendimiento | Cliente | Solicita cargar el catálogo completo de un puesto | Hora pico de compras (11:00 a. m. - 1:00 p. m.) en red 3G | API del Catálogo / PWA | Filtra los datos y envía una carga ligera optimizada | Tiempo de respuesta del p95 $\le 2,5$ segundos |
| QA-03 | Modificabilidad | Desarrollador | Solicita integrar una nueva pasarela de pago (ej. Plin) | Fase de mantenimiento y evolución | Módulo de Pagos | Se agrega el adaptador de la nueva pasarela sin modificar los demás módulos | Tiempo de implementación $\le 2$ días-persona |