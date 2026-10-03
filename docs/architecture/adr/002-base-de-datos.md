# ADR-002: Selección de PostgreSQL con Esquemas Aislados por Módulo

* **Estado:** Aceptado
* **Fecha:** 2026-09-30
* **Decisores:** Grupo 07

## Contexto
El sistema requiere persistir información estructurada para transacciones complejas como pedidos multi-puesto y registros de pago con Yape (RF-02, RF-03), manteniendo el aislamiento entre los módulos acordado en ADR-001. Debemos operar sobre un único servidor VPS (R-03).

## Alternativas Consideradas
1. **Múltiples Bases de Datos Independientes:** Alta independencia pero sobrecarga los recursos de memoria del VPS (R-03).
2. **Base de Datos NoSQL (MongoDB):** Flexible para catálogos pero compleja para la consistencia transaccional de pagos.
3. **PostgreSQL con Esquemas Aislados (`catalog_schema`, `orders_schema`, etc.):** Motor relacional robusto con separación lógica estricta en una única instancia.

## Decisión
Usaremos **PostgreSQL utilizando un esquema de base de datos independiente por cada módulo** del Monolito Modular[cite: 7, 10]. Ningún módulo podrá realizar consultas directas (JOINs) a esquemas que no le pertenecen.

## Consecuencias
* **Positivas:** Consistencia ACID para el registro de pagos, bajo consumo de recursos en el VPS y aislamiento claro de datos que facilita una futura migración.
* **Negativas / Riesgos:** Las consultas analíticas que requieran datos de múltiples módulos deben realizarse mediante llamadas entre servicios de aplicación.