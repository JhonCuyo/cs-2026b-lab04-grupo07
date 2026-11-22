# ADR-010: Sistema agéntico para resolver issues en San Camilo en Línea

* **Estado:** Aceptado
* **Fecha:** 2026-11-21
* **Decisores:** Grupo 07 (Jhon Deyvis Cuyo Ccapa, Wilber Jesus Guerra Pilco y Diego Sebastian Santacruz Villa)

## Contexto

San Camilo en Línea, un [monolito modular](001-estilo-arquitectonico.md), necesita un modo reproducible y auditable de diagnosticar y corregir incidencias de código. El Lab 10 lo evalúa sobre tres casos: comisión multipuesto (`ISSUE-01`), visibilidad de productos agotados (`ISSUE-02`) y redondeo monetario (`ISSUE-03`). Las demostraciones no deben requerir claves de API y deben limitar el exceso de agencia (OWASP LLM06) y el impacto de instrucciones no confiables leídas del repositorio.

## Alternativas consideradas

1. **Agente único con shell libre:** fácil de configurar, pero le permite ejecutar comandos arbitrarios y modificar las pruebas que deberían validar su trabajo.
2. **Coordinación multiagente para todos los issues:** separa responsabilidades, pero añade pasos y contexto incluso cuando el cambio es local y de bajo riesgo.
3. **Coordinación según el riesgo, con política por rol y revisión humana (elegida):** concentra el costo de la revisión adicional en los cambios que lo justifican.

## Decisión

* **Arquetipo:** usar el bucle ReAct en `agentes/agente/`. Cada decisión se valida contra el contrato JSON y la política antes de invocar una herramienta. Después se observa el resultado y se registra en la traza.
* **Coordinación:** usar un agente único para los cambios locales de `ISSUE-01` e `ISSUE-03`. Para `ISSUE-02`, usar un planificador sin herramientas, un ejecutor y un revisor sin permiso de edición, con un máximo de dos rondas.
* **Herramientas y memoria:** limitar las operaciones de archivo al repositorio, proteger las rutas de pruebas en la política y restringir los comandos con una lista blanca. El historial conserva el contexto de la sesión; `mapa_repo()` y `notas.md` apoyan la exploración y la memoria de trabajo.
* **Control humano:** el ejecutor tiene un presupuesto de 12 pasos y el revisor, de 8. El orquestador pide aprobación `s`/`n` por defecto para cada `editar_archivo` permitido por la política. `--sin-confirmacion` se reserva para CI y demostraciones. El veredicto del revisor no reemplaza la aprobación humana del PR. Véase la [hoja de ruta de delegación](../../../agentes/delegacion.md).
* **Modelo intercambiable:** `ModeloGrabado` reproduce decisiones sin servicios externos ni claves de API; `ModeloInteractivo` permite ingresar y grabar decisiones manualmente.

## Consecuencias

* **Evidencia positiva:** las [trazas de E7](../../../agentes/observacion.md) registran el bloqueo del intento de ejecutar el comando sugerido por un comentario y el rechazo del intento de edición del revisor. Solo la variante actor-crítico retiró el comentario en el experimento archivado. Las trazas JSONL y los diagramas Mermaid permiten revisar estas acciones por separado de los mensajes finales.
* **Costo:** la variante actor-crítico requirió 16 pasos y dos rondas frente a 6 pasos y una ronda del agente único. La confirmación de cada edición añade tiempo de revisión; cualquier ampliación de permisos depende de la evidencia exigida por la hoja de ruta.
* **Límites:** las trayectorias grabadas permiten reproducir el flujo, no medir la capacidad de detección autónoma de un modelo. Una prueba en verde tampoco demuestra que el agente haya aplicado el parche. Las restricciones del laboratorio no sustituyen el aislamiento del entorno ni la revisión del diff y las observaciones de herramienta.
