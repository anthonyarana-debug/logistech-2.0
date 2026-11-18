# Pendientes de Semana 13

- Revisar las alertas residuales de imagen y decidir si procede parche de proveedor, reducción de exposición o aceptación técnica documentada.
- Completar en AWS el piloto con roles adicionales, escrituras CRUD, QR, recepción e historial. Verificar renovación de TLS y establecer una segunda copia cifrada independiente del equipo operador.
- En AWS se confirmaron 50 altas, pero el p95 de 17,32 s detuvo la escalera. Quedan pendientes los escalones de 100–1.000 registros, el caso de 10.000 en 30 s y la escalera GET hasta 50.000. Antes de repetir, acordar la concurrencia y medir CPU, espera de Gunicorn, E/S y PostgreSQL durante la carga. [Resultados en la nube](SEMANA_13_PRUEBAS_NUBE.md#resultados-en-la-nube-18-de-noviembre-de-2026)
- El pico histórico del ensayo local de 2.500 GET con 20 VU sigue pendiente de diagnóstico.
- Arrancar F8 por incrementos cuando se cumplan los criterios de entrada del plan.

[Checklist F7](LOGISTECH_SEMANA_13_AWS_CHECKLIST.md) · [Plan F8](PLAN_FASE_8.md)

La contraseña inicial del administrador debe rotarse por un canal privado cuando el propietario lo autorice. Después se verifican el inicio de sesión, la renovación y los permisos. Revisar el siguiente respaldo nocturno y confirmar una copia cifrada posterior a la creación del administrador.
