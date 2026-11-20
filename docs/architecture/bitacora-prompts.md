# Bitácora de Uso de IA — Laboratorio 09 (Prompt Engineering y Evals)

Registro auditable bajo la regla de oro: *"Un prompt no se siente mejor, se demuestra mejor con promptfoo"*.

---
### Interacción 1: Diseño del contrato JSON Schema (E1)
* **Propuesta:** Esquema con campos obligatorios.
* **Decisión:** Aceptada con ajuste de rangos numéricos para confianza.

### Interacción 2: Construcción del dataset de casos (E1)
* **Propuesta:** 8 casos de prueba incluyendo inyección en español local.
* **Decisión:** Aceptada íntegramente.

### Interacción 3: Propuesta rechazada de incluir "Piensa paso a paso" (Chain-of-Thought)
* **Propuesta de la IA:** Agregar texto libre de razonamiento antes del JSON.
* **Verificación:** Rompía el contrato JSON Schema de `promptfoo`.
* **Decisión:** **Rechazada.**

### Interacción 4: Creación del proveedor grabado (E2)
* **Propuesta:** Script en Python para leer fixtures estáticas.
* **Decisión:** Aceptada.

### Interacción 5: Análisis de no determinismo y red teaming (E5/E7)
* **Propuesta:** Estructura de red teaming bajo OWASP LLM01.
* **Decisión:** Aceptada íntegramente.