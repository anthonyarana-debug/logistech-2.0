# Plan de Fase 8

La entrada requiere validar F7 en el servidor autorizado, cerrar el riesgo de las imágenes y confirmar que el equipo puede restaurar un backup cifrado. El alcance funcional se divide en incrementos con pruebas de aceptación.

| Incremento | Alcance | Criterio de aceptación |
|---|---|---|
| Movimientos de inventario | Entradas, salidas y ajustes con motivo, empresa, sucursal, responsable y clave de idempotencia | Transacciones concurrentes conservan saldo y un reintento no duplica el movimiento |
| Existencias y conciliación | Saldo por sucursal y producto, discrepancias y correcciones trazables | Reconciliar un conjunto de entradas/salidas contra el libro de movimientos sin cruce de empresas |
| Reportes | Filtros, exportación acotada, resumen por sucursal y periodo | Los totales coinciden con los movimientos y aplican el alcance del usuario |
| Rendimiento | 10.000, 25.000 y 50.000 GET en ensayo dedicado, escalones aprobados, cuotas por identidad y seguimiento de recursos | Cumplir iteraciones, cero errores y p95 inferior al umbral acordado. Comparar CPU, RAM, E/S, planes y latencia durante la carga |
| Operación | Logs, alertas, restore periódico, CI de release y migraciones con rollback ensayado | Identificar versión por SHA, restaurar datos independientes y comprobar la reversión o recuperación compatible |

Mantener los contratos de QR, recepción e historial. Para migraciones futuras, añadir estructura compatible, rellenar datos en lotes verificables y activar restricciones después de validar. Acordar RPO, RTO y capacidad a partir de ensayos con datos representativos. Los ensayos de mayor volumen requieren dimensionamiento y una estrategia de tokens que respete las cuotas.
