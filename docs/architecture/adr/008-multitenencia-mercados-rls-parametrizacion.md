# ADR-008: Multitenencia por Mercado con Row-Level Security (RLS) y Reglas Parametrizadas en BD

* **Estado:** Aceptado
* **Fecha:** 2026-10-28
* **Decisores:** Grupo 07 (San Camilo en Línea)

## Contexto
La expansión de la plataforma a los mercados **Altiplano** y **Río Seco** exige aislamiento estricto de datos entre mercados (`QA-01: 0 filas filtradas`) y la capacidad de dar de alta un nuevo mercado con sus propias reglas de tarifa de delivery y topes de pedido en $\le 1$ día sin desplegar código (`QA-02`).

## Alternativas Consideradas
1. **Una base de datos PostgreSQL por mercado:** Aislamiento físico alto, pero excede la memoria del VPS único (`R-03`) y requiere migraciones y despliegues manuales por cada nuevo mercado.
2. **Un esquema PostgreSQL por mercado:** Complejidad media de migración; innecesario para 3 a 5 mercados locales.
3. **Columna `mercado_id` + PostgreSQL Row-Level Security (RLS) + Claim `mercado_id` en el JWT + Tabla `configuracion_mercado` (Opción elegida).**

## Decisión
Implementamos multitenencia de base de datos compartida mediante una columna `mercado_id` protegida por políticas **Row-Level Security (RLS)** en PostgreSQL 16, inyectando el tenant desde el claim `mercado_id` del token JWT en cada transacción. Además, externalizamos las reglas de tarifas y topes por mercado en la tabla `configuracion_mercado` (táctica *Diferir el enlace*).

## Consecuencias
* **Positivas (Evidencia):** El prototipo `fitness/aislamiento_modificabilidad.py` y la fitness function `FF-06` garantizan **0 filas filtradas** entre mercados y permiten incorporar un nuevo mercado con **0 líneas de código modificadas**.
* **Negativas / Trade-off aceptado:** Introduce el riesgo `R2` (una tabla nueva sin política RLS podría exponer datos), el cual queda mitigado permanentemente por la prueba `test_ff06` en GitHub Actions.