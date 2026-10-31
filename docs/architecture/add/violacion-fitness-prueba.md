# Verificación de Fitness Functions Estructurales (`lint-imports`) — Prueba de Violación Intencional (E5.2)

Para comprobar que las fitness functions estructurales (`FF-01` y `FF-02` definidas en `.importlinter`) detectan y bloquean degradaciones reales de la arquitectura, introdujimos temporalmente dos violaciones deliberadas:
1. **Violación de `FF-01` (`ADR-001` — Ciclos entre módulos):** Agregamos `import src.sancamilo.pedidos` dentro de `src/sancamilo/catalogo/__init__.py`.
2. **Violación de `FF-02` (`ADR-005` — Acoplamiento directo a adaptadores):** Agregamos `from src.sancamilo.pagos.adaptadores import YapeAdapter` dentro de `src/sancamilo/reportes/__init__.py`.

## 1. Salida Real de `lint-imports` Detectando las Violaciones (Estado: BROKEN)

```text
$ lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 8 files, 6 dependencies.
---------------------------------

FF-01 Capas del monolito modular San Camilo sin ciclos (ADR-001) BROKEN
FF-02 Solo el contenedor de arranque conoce los adaptadores de pago (ADR-005) BROKEN

Contracts: 0 kept, 2 broken.

----------------
Broken contracts
----------------

FF-01 Capas del monolito modular San Camilo sin ciclos (ADR-001)
----------------------------------------------------------------
src.sancamilo.catalogo is not allowed to import src.sancamilo.pedidos:
- src.sancamilo.catalogo -> src.sancamilo.pedidos (l. 4)

FF-02 Solo el contenedor de arranque conoce los adaptadores de pago (ADR-005)
-----------------------------------------------------------------------------
src.sancamilo.reportes is not allowed to import src.sancamilo.pagos.adaptadores:
- src.sancamilo.reportes -> src.sancamilo.pagos.adaptadores (l. 3)
```

## 2. Salida de `lint-imports` tras Revertir las Violaciones (Estado: KEPT)

```text
$ lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 8 files, 4 dependencies.
---------------------------------

FF-01 Capas del monolito modular San Camilo sin ciclos (ADR-001) KEPT
FF-02 Solo el contenedor de arranque conoce los adaptadores de pago (ADR-005) KEPT

Contracts: 2 kept, 0 broken.
```