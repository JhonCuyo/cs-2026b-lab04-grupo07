# Hoja de Ruta de Delegación Progresiva — San Camilo en Línea (Grupo 07)

Basado en Albada (2025, cap. 13) y Koenigstein (2026, cap. 2), la autonomía del sistema crece de forma controlada a medida que las trazas JSONL y las pruebas demuestran que los controles funcionan.

## Evolución de los 4 roles humanos

| Etapa | Rol humano | Permisos del agente | Controles | Evidencia para avanzar |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Ejecutor**: inicia y supervisa cada paso. | Inspecciona el repositorio (`listar_archivos`, `leer_archivo`, `buscar`, `mapa_repo`) y ejecuta pruebas; no puede editar archivos. | Sandbox de rutas, contrato JSON, `max_pasos=8` y trazas JSONL obligatorias. | Al menos 10 diagnósticos correctos en `src/sancamilo/`, ningún intento de escape del sandbox y como máximo un 5 % de errores de contrato. |
| **2** | **Revisor**: aprueba o rechaza cada edición propuesta y revisa el PR. | Añade `editar_archivo` con aprobación, memoria de notas y comandos de lista blanca (`pytest`, `radon`, `lint-imports`, `git status` y `git diff`). | Confirmación `s`/`n` para `editar_archivo` en el orquestador, protección de `tests/` y `agentes/pruebas_agente/`, y revisión humana obligatoria del PR. | Al menos 20 issues consecutivos con `pytest` y `lint-imports` en verde, sin ediciones rechazadas por seguridad ni inyecciones indirectas que superen los controles. |
| **3** | **Colaborador**: refina los cambios con el agente y decide si fusionar el PR. | Podría permitir ediciones de bajo riesgo en ramas `feat/`, por ejemplo en `catalogo/` o `reportes/`, y mantener la confirmación en `pagos/` y `pedidos/`. | Coordinación actor-crítico con revisor sin edición, presupuesto de pasos y tokens, CI obligatorio y protección adicional de `fitness/` antes de ampliar permisos. | Al menos 50 PR fusionados, menos de un 10 % de retrabajo, ninguna regresión en producción y trazabilidad de todos los PR en `observacion.md`. |
| **4** | **Gobernador**: fija objetivos, límites y criterios de auditoría. | Podría delegar issues rutinarios etiquetados `auto-fix`: preparar una rama, proponer un cambio y abrir un PR con resultados de CI. No puede fusionar directo a `main` ni desplegar credenciales. | Auditoría continua de trazas JSONL, alertas ante eventos `BLOQUEADO`, revisión periódica de `Politica` y ejercicios defensivos. | Etapa final. Ante un incidente grave de seguridad o una regresión en `pagos/`, se vuelve a la etapa 2. |

## Posición actual del Grupo 07

Operamos en la **etapa 2 (Revisor)**. En ambos modos de `agentes/orquestador.py`, `solicitar_aprobacion_consola()` muestra la ruta y el antes y después de cada `editar_archivo` que supera la política. `s` autoriza la edición; `n` o el fin de la entrada la bloquean. Cualquier otra respuesta vuelve a pedir confirmación. Un integrante del equipo conserva la decisión de aprobar y fusionar el PR.

`--sin-confirmacion` omite únicamente la interacción de consola para CI o demostraciones no interactivas; las demás reglas de la política siguen activas. Las trayectorias del laboratorio son grabadas: sus mensajes finales no sustituyen la revisión de las acciones y observaciones en la traza.
