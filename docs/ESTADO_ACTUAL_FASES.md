# Estado actual de las fases de LogisTech 2.0

| Fase | Objetivo | Implementado | Validado | Pendiente | Evidencia | Versión |
|---|---|---|---|---|---|---|
| F0 | Auditoría y alcance | Requisitos, arquitectura y plan | Revisión documental histórica | Seguimiento de evolución | [Informe F0](INFORME_FASE_0.md) | F0 |
| F1 | Base reproducible | Django, React, PostgreSQL y Docker | Arranque y salud documentados | Operación pública en F7 | [Informe F1](INFORME_FASE_1.md) | F1 |
| F2 | Modelo y autenticación | Usuario personalizado, roles y JWT | Migraciones y pruebas con PostgreSQL | Validación pública de sesión | [Informe F2](INFORME_FASE_2.md) | F2 |
| F3 | API y CRUD | Inventario versionado, permisos y validaciones | API, integridad y aislamiento | Verificación externa | [Informe F3](INFORME_FASE_3.md) | F3 |
| F4 | Interfaz | Industrial Precision, formularios y paneles | Regresión visual y operativa | Validación externa | [Informe F4](INFORME_FASE_4.md) | F4 |
| F5 | Evidencia del 25 % | Suites y ensayos de rendimiento | pytest, Playwright y Locust históricos | Capacidad de producción | [Informe F5](INFORME_FASE_5.md) | F5 |
| F6.1 | Administración | Empresas, sucursales, usuarios y catálogo | Permisos por rol y empresa | Piloto externo | [Informe F6](INFORME_FASE_6.md) | F6.1 |
| F6.2 | Trazabilidad | QR, identificación, recepción e historial | Operaciones reales locales y auditoría de permisos | Piloto externo | [Informe F6.2](INFORME_FASE_6_BLOQUE_2.md) | F6.2 |
| F7 | Producción y despliegue | HTTPS local, red privada, paginación, backups y k6 monitorizado | Ensayo local y evidencia de 5.000 GET | Piloto externo de roles, escrituras y trazabilidad | [Resultados Semana 13](SEMANA_13_RESULTADOS_PRUEBAS.md) | Semana 13 |
| F8 | Evolución y validación final | Alcance y aceptación propuestos | Revisión de dependencias | Implementación por bloques tras F7 | [Plan F8](PLAN_FASE_8.md) | Plan |

El ZIP de cierre interno pasó la comprobación de integridad y declara el SHA local `53af6f3feb7c9a1df510632c7d8d2ca6e1f89f49`. Su SHA-256 es `1a9e68a4f20fd0b1d4194253e22a5f1685c234224815ff10e31140176174a32e`. El respaldo remoto F7 quedó verificado en `9b840a0ac28df6e8d0f3530571aed0ee1b1ad046`. Los cinco commits posteriores incorporan paginación, imágenes endurecidas, pruebas, métricas y documentación. El trabajo nuevo parte de ese cierre en `codex/f7-cierre-80-cloud-documentacion`.
