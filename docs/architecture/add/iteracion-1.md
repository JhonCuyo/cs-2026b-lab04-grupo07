# Iteración 1 de ADD 3.0 — Aislamiento Multimercado y Reglas Parametrizadas (`QA-01` y `QA-02`)

## 1. Objetivo de la Iteración (Paso 2 de ADD)
Atender los dos escenarios prioritarios detonados por la incorporación de los mercados **Altiplano** y **Río Seco**:
* **QA-01 (H, H) — Seguridad / Aislamiento:** Un comerciante o administrador del Mercado Altiplano nunca debe visualizar ni modificar productos, pedidos ni reportes de San Camilo o Río Seco (**0 filas ajenas expuestas**).
* **QA-02 (H, M) — Modificabilidad:** Incorporar un nuevo mercado con sus propias tarifas de delivery, recargos por puesto y horarios de atención en **$\le 1$ día** y con **0 líneas de código desplegadas**.

## 2. Elementos del Sistema a Refinar (Paso 3 de ADD)
* Contenedor **Backend API** (`Módulo Catálogo`, `Módulo Pedidos` y `Módulo Reportes`).
* Contenedor **Base de Datos PostgreSQL 16** (esquema de tablas de dominio y políticas de acceso).

## 3. Evaluación de Conceptos de Diseño Candidatos (Paso 4 de ADD — Prompt IA 2)

| Concepto de Diseño Evaluado | Táctica Arquitectónica (Bass et al.) | Impacto en Aislamiento (`QA-01`) | Impacto en Modificabilidad (`QA-02`) | Costo / Complejidad (Plazo 1 mes, 1 VPS) | Decisión del Equipo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Opción 1: Una instancia de BD PostgreSQL y un contenedor API por cada mercado** | Aislar recursos físicos | Muy alto (bases separadas) | **Malo:** Requiere aprovisionar contenedores, migrar esquemas y configurar subdominios Nginx por cada mercado (~3 días). | **Alto:** Triplica el consumo de RAM en el VPS único de 4 GB (`R-03`). | **Rechazada:** Viola la restricción de presupuesto `R-03` y complica las operaciones del equipo de 3 personas. |
| **Opción 2: Hardcodear `if mercado == "ALTIPLANO"` en clases Strategy por cada mercado** | Polimorfismo en código | Nulo (requiere filtros manuales en cada query) | **Malo:** Cada nuevo mercado o cambio de tarifa exige editar código Python, abrir PR y redesplegar. | **Medio:** Propenso a olvidos de `WHERE mercado_id = ...` en consultas de reportes. | **Rechazada:** No cumple la meta de `0 líneas de código desplegadas` de `QA-02` y deja alto riesgo de fuga de datos. |
| **Opción 3: Columna discriminadora `mercado_id` + PostgreSQL Row-Level Security (RLS) + Claim `mercado_id` en el JWT** | Seguridad: *Limitar acceso (RLS)* y *Autenticar actores* | **Excelente:** El motor PostgreSQL bloquea en la capa de datos cualquier fila cuyo `mercado_id` no coincida con `current_setting('app.mercado_id')`. | **Alto:** Todas las organizaciones comparten las mismas tablas sin duplicar infraestructura. | **Bajo:** 1 migración SQL para habilitar `ENABLE ROW LEVEL SECURITY` y un middleware Django de 15 líneas. | **Aceptada (`ADR-008`).** |
| **Opción 4: Tabla `configuracion_mercado` en BD (Diferir el enlace / Parameterization)** | Modificabilidad: *Diferir el enlace (Binding time)* | Neutro (se apoya en RLS) | **Excelente:** Permite registrar un nuevo mercado y sus reglas (`tarifa_base`, `recargo_puesto`, `tope_lineas`) insertando 1 fila en BD. | **Bajo:** Reemplaza valores estáticos por lectura cacheada de `ConfiguracionMercado`. | **Aceptada (`ADR-008`).** |

## 4. Instanciación de Elementos y Responsabilidades (Pasos 5 y 6 de ADD)
1. **Middleware `TenantMercadoMiddleware` en `Backend API`:** Extrae el claim `mercado_id` del token JWT del comerciante/administrador y ejecuta `SET LOCAL app.mercado_id = '<mercado_id>'` al abrir cada transacción en PostgreSQL.
2. **Políticas RLS en `PostgreSQL 16`:** Se activan sobre las tablas `puestos`, `productos` y `pedidos` (`CREATE POLICY aislamiento_mercado ON pedidos USING (mercado_id = current_setting('app.mercado_id'))`).
3. **Motor de Reglas `MotorMultimercado` (`ConfiguracionMercado`):** Almacena en base de datos la tarifa base de delivery (`S/ 5.00` en San Camilo, `S/ 6.50` en Altiplano, `S/ 8.00` en Río Seco) y el recargo por puesto adicional.

## 5. Análisis y Evidencia Cuantitativa Antes/Después (Paso 7 de ADD)
Se ejecutó el prototipo `python fitness/aislamiento_modificabilidad.py` comparando el comportamiento antes y después de aplicar RLS y parametrización en BD sobre una base de datos con registros de los 3 mercados:

| Métrica del Escenario | Antes de las Tácticas (Sin RLS / Tarifas en código) | Después de las Tácticas (Con RLS + Tabla `ConfiguracionMercado`) | Meta del Escenario | ¿Cumple? |
| :--- | :---: | :---: | :---: | :---: |
| **Filas de otros mercados expuestas al consultar como `ALTIPLANO` (`QA-01`)** | **3 filas ajenas expuestas** (2 de San Camilo + 1 de Río Seco) | **0 filas ajenas expuestas** (solo retorna registros de `ALTIPLANO`) | **0 filas filtradas** | **SÍ** |
| **Líneas de código modificadas/desplegadas para dar de alta el 4.° mercado `ZAMACOLA` (`QA-02`)** | **14 líneas** (nuevo `elif`, constantes y redeploy) | **0 líneas de código** (1 inserción en `ConfiguracionMercado` en $< 5$ min) | **$\le 1$ día y 0 líneas desplegadas** | **SÍ** |
| **Cálculo dinámico de tarifa para 3 puestos según reglas de cada mercado** | Fijo (`S/ 5.00` para todos) | San Camilo: `S/ 7.00` \| Altiplano: `S/ 9.50` \| Río Seco: `S/ 9.00` \| Zamácola: `S/ 8.00` | Reglas independientes por mercado | **SÍ** |