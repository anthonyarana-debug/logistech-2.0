# Publicación de LogisTech 2.0 y visibilidad vigente

**Estado vigente:** repositorio **público**, confirmado durante la adaptación mediante API anónima GitHub: `private=false`, `visibility=public`. La adaptación no cambió su visibilidad ni realizó push. Los ocho puntos de control de la publicación original permanecen como antecedentes; esta rama de adaptación sigue solo local.

## Registro histórico de publicación privada inicial

Fecha: 27/10/2026, America/Lima. Autorización expresa del propietario para crear el destino PRIVATE y efectuar el primer push. **Repositorio publicado y clonación autenticada comprobada.**

Enlace definitivo: [https://github.com/anthonyarana-debug/logistech-2.0](https://github.com/anthonyarana-debug/logistech-2.0). Durante la publicación privada inicial se exigía acceso autorizado y la consulta anónima devolvía 404. Actualmente el repositorio es público y esa descripción no representa su visibilidad vigente.

## Comprobaciones realizadas

1. GET /user confirmó anthonyarana-debug mediante Git Credential Manager, sin imprimir, guardar o incluir el token en URL/archivos.
2. Antes de crear, GET del destino devolvió 404. Se creó vacío con private=true y auto_init=false; respuesta 201. GET posterior confirmó propietario, private=true y visibility=private.
3. Se volvió a auditar índice e historial: siete commits, 289 blobs, veinte exclusiones y ningún hallazgo de valores privados locales conocidos, rutas sensibles, patrones de tokens o firmas de dumps.
4. Se configuró origin únicamente con `https://github.com/anthonyarana-debug/logistech-2.0.git`. Se comprobó que no tenía ramas antes de publicar.
5. Push **atómico, sin force ni mirror** de ocho ramas. Main predeterminada en GitHub y seguimiento local origin/main. El primer main publicado fue `951c36cbfc9297478fd815f4cb7925b2a8afaf03`, incluyendo la preparación y todos los commits anteriores. Este registro se incorpora después mediante avance normal de main, sin cambiar los puntos de control.
6. GET de la rama main coincidió con el SHA local; GitHub pudo consultar F5 `04dd19ab41182fb194517c159d4df8a6b40a1e7d` y el blob del informe F5 coincidió con el local.
7. Clon HTTPS **real desde GitHub**, autenticado y en un directorio temporal nuevo: main seleccionada por defecto, siete commits en la publicación inicial, F5 ancestro y ramas remotas disponibles. Sin .env/.env.demo.json/.env.f5-demo.json. Auditor en el clon sin hallazgos. El temporal se eliminó al terminar; no se generaron credenciales ni datos dentro del clon.
8. Consulta anónima a la API devolvió 404; consulta autenticada confirmó PRIVATE. No se habilitaron colaboradores, Pages, despliegues o recursos de aplicación.

## Ramas conservadas

| Rama remota | Punto de control |
|---|---|
| main | Última versión del proyecto, preparación y registro de publicación |
| codex/fase-0-planificacion | 1223797, origen del master local, conservado sin renombrarlo localmente |
| codex/fase-1-configuracion | b91caf9 |
| codex/fase-2-autenticacion | e5efee1 |
| codex/fase-3-api-crud | 7e9b7b9 |
| codex/fase-4-frontend | b05ce9e |
| codex/fase-5-validacion | 04dd19a |
| codex/preparacion-github | 951c36c |

La rama pública del Android original permaneció en `060cb00fecba639f1d9f05c34d33c1054169e89e` en la consulta posterior. Todas las operaciones sobre ese repositorio fueron GET; no se configuró como remoto ni recibió commits. Se mantiene la barrera local del hook que bloquea su nombre.

## Qué se publicó y qué queda local

Código, migraciones, documentación, licencias, pruebas y evidencias académicas saneadas. No se publicaron .env reales, contraseñas/cuentas DEMO privadas, tokens, bases, dumps o volúmenes Docker. Las plantillas .env.example y deploy/production.env.example tienen marcadores ficticios. Los ejemplos y claves sintéticas de unitarias no son credenciales de cuentas activas. Los archivos privados locales existentes no se borraron ni modificaron para publicar.

La auditoría es una defensa por patrones y valores conocidos, no certificación absoluta. Con el repositorio ahora público, mantener la exclusión de secretos y activar el hook en cada clon. Historial Git incluye autoría y las evidencias contienen metadatos académicos/rutas de equipo ya revisados, sin acceso a cuentas.

## Continuar en otra computadora

Seguir [NUEVA_COMPUTADORA.md](NUEVA_COMPUTADORA.md). Requiere Git/Git Credential Manager, Docker Desktop Linux y Python 3.13 para generar configuración con biblioteca estándar; la aplicación usa sus entornos Docker fijados. Clonar el repositorio público sin credenciales, generar secretos nuevos, construir, migrar la base nueva e iniciar servicios. Datos de PostgreSQL no viajan con el clon: crear DEMO nuevos o usar un respaldo cifrado autorizado fuera de Git.

No se inició ninguna fase adicional. Publicar código en GitHub no equivale a desplegar LogisTech en cloud; la situación académica de F5 permanece documentada en su informe.
