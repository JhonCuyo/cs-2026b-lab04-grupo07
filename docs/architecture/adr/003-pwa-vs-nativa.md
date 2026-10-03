# ADR-003: Adopción de Progressive Web App (PWA) para Comerciantes y Clientes

* **Estado:** Aceptado
* **Fecha:** 2026-09-30
* **Decisores:** Grupo 07

## Contexto
Los comerciantes del Mercado San Camilo utilizan teléfonos inteligentes de gama baja con memoria limitada y conectividad móvil 3G e inestable (R-04). El sistema requiere cumplir con el atributo de usabilidad crítico: permitir publicar productos en $\le 3$ toques (QA-01) sin requerir descargas pesadas desde tiendas de aplicaciones.

## Alternativas Consideradas
1. **Aplicación Nativa (Android/Flutter):** Excelente rendimiento pero requiere descarga e instalación pesada, incompatible con dispositivos de gama muy baja con almacenamiento lleno.
2. **Sitio Web Responsive Tradicional:** Requiere conexión a internet constante para cada interacción.
3. **Progressive Web App (PWA):** Aplicación web instalable, ligera y con capacidad de almacenamiento en caché para operar con conexiones lentas.

## Decisión
Desarrollaremos la interfaz móvil como una **Progressive Web App (PWA)**. La PWA almacenará en caché la interfaz de publicación del comerciante y los catálogos para permitir interacciones fluidas en redes 3G.

## Consecuencias
* **Positivas:** No requiere espacio de instalación en tiendas, carga liviana optimizada para 3G y cumplimiento del flujo de publication en $\le 3$ toques (QA-01).
* **Negativas / Riesgos:** Acceso limitado a ciertas características nativas de hardware avanzadas en iOS (aunque no afecta las funcionalidades del MVP).