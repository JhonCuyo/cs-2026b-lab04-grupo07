# ADR-001: Adopción de un Monolito Modular para San Camilo en Línea

* **Estado:** Aceptado
* **Fecha:** 2026-09-29
* **Decisores:** Grupo 07

## Contexto
El MVP de San Camilo en Línea debe lanzarse en producción en máximo 1 mes (R-01) con un equipo de 3 desarrolladores (R-02) y un presupuesto ajustado que requiere un servidor VPS único (R-03). El sistema debe gestionar el catálogo por puesto, pedidos multi-puesto, pagos con Yape y notificaciones por WhatsApp (RF-01 al RF-05). Requerimos alta modificabilidad para integrar nuevas pasarelas sin comprometer la entrega ágil.

## Alternativas Consideradas
1. **Monolito en Capas (4.20):** Rápido de construir pero con alto riesgo de acoplamiento entre la lógica de pagos, catálogo y pedidos.
2. **Microservicios (2.60):** Alta escalabilidad pero excede ampliamente la capacidad operativa del equipo y el presupuesto del VPS.
3. **Monolito Modular (4.25):** Elección óptima que permite desacoplamiento por dominio en un solo despliegue.

## Decisión
Usaremos una arquitectura de **Monolito Modular**[cite: 6, 10, 12]. El sistema estará estructurado en 5 módulos (Catálogo, Pedidos, Pagos, Notificaciones y Envíos) comunicados estrictamente mediante interfaces de aplicación públicas dentro de una misma unidad de despliegue.

## Consecuencias
* **Positivas:** Bajo costo operativo en un solo VPS, entrega dentro del plazo de 1 mes y facilidad para extraer módulos a microservicios en el futuro si la demanda aumenta[cite: 6, 10].
* **Negativas / Riesgos:** Se requiere disciplina estricta en el código para respetar los límites de cada módulo y evitar dependencias circulares.