# Bitácora de Uso de Inteligencia Artificial - San Camilo en Línea

| # | Fecha | Herramienta | Prompt (Resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 2026-09-29 | Claude | Generación de alternativas de arquitectura según RCRTF | Arquitectura de Microservicios con Kubernetes y RabbitMQ | Excede las restricciones R-01 (plazo de 1 mes), R-02 (equipo de 3) y R-03 (presupuesto bajo) | Rechazada |
| 2 | 2026-09-29 | ChatGPT | Crítica adversarial a Monolito Modular ("Abogado del diablo") | Señaló riesgos de acoplamiento de base de datos y caída total si falla un módulo | Se validó que aislando los esquemas en PostgreSQL y usando tareas asíncronas con Celery/Redis se mitigan los riesgos | Aceptada |
| 3 | 2026-09-30 | Gemini | Estrategia para PWA en celulares de gama baja | PWA con Service Workers y caché local para catálogos | Se verificó la compatibilidad con dispositivos Android de gama baja y señal 3G (QA-01) | Aceptada |
| 4 | 2026-09-30 | Copilot | Generación del código Mermaid para el flujo del sistema | Sintaxis Mermaid con subgraph y dependencias | Se corrigieron nombres de componentes y la dirección de las flechas hacia las APIs externas | Corregida |
| 5 | 2026-10-01 | Claude | Borrador de ADR-001 sobre el estilo arquitectónico | Estructura base del registro de decisión | Se ajustaron las consecuencias citando explícitamente los IDs de restricciones de drivers.md | Corregida |

---

## Anexo: Prompts Completos

### Prompt 1: Generación de alternativas (Rechazada / Evaluada)
> **Rol:** Arquitecto de Software Senior experto en soluciones para comercio local.  
> **Contexto:** Plataforma "San Camilo en Línea" para el Mercado San Camilo (Arequipa). Los comerciantes publican sus productos desde celulares de gama baja; los clientes realizan pedidos multi-puesto y pagan con Yape; las confirmaciones se envían por WhatsApp.  
> **Restricciones:** 3 desarrolladores, MVP funcional en 1 mes, único servidor VPS de bajo costo.  
> **Tarea:** Propón 3 alternativas de estilo arquitectónico indicando ventajas, desventajas y qué atributos de calidad favorece o penaliza.  
> **Formato:** Tabla comparativa en Markdown con recomendación final.

### Prompt 2: Crítica adversarial (Abogado del diablo)
> **Rol:** Arquitecto Evaluador Adversario.  
> **Contexto:** Hemos seleccionado una arquitectura de Monolito Modular para San Camilo en Línea.  
> **Tarea:** Critica esta decisión. Enumera los 5 riesgos más graves en producción dados nuestros límites de equipo y plazo, y sugiere tácticas de mitigación.