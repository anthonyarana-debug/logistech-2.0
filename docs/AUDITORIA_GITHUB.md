# Auditoría y preparación de sincronización privada

**Estado vigente:** repositorio público, confirmado por API durante la adaptación. La auditoría y propuesta de privacidad que siguen son históricas; no se cambió visibilidad ni se publicó esta adaptación. Ver PUBLICACION_GITHUB.md.

Fecha de revisión: 27/10/2026, America/Lima. **Actualización: publicación privada autorizada y verificada** en [anthonyarana-debug/logistech-2.0](https://github.com/anthonyarana-debug/logistech-2.0); ver [PUBLICACION_GITHUB.md](PUBLICACION_GITHUB.md). No se modificó el repositorio Android. Las secciones siguientes conservan el registro de auditoría y la propuesta **previos a la autorización**.

## Estado encontrado

- Git limpio al comenzar; no existía origin ni otro remoto, upstream o rama remota.
- Seis commits lineales alcanzables: F0 `1223797`, F1 `b91caf9`, F2 `e5efee1`, F3 `7e9b7b9`, F4 `b05ce9e` y F5 `04dd19a`. F5 estaba únicamente en la rama local codex/fase-5-validacion.
- master local señala F0: **no debe convertirse por accidente en la versión predeterminada del nuevo remoto**. La preparación está en codex/preparacion-github, descendiente de F5. El main remoto propuesto partirá de esta preparación, con toda la historia anterior.
- GitHub CLI gh no está disponible en PATH; Git Credential Manager sí está disponible. Se autenticó en memoria para consultas GET a api.github.com sin imprimir ni guardar el token. Cuenta confirmada: anthonyarana-debug.
- Se consultaron los 27 repositorios visibles para esa cuenta (incluido uno privado), se buscó el commit F5 y el informe docs/INFORME_FASE_5.md. No se encontró F5 en esos repositorios. Este resultado se limita a los repositorios accesibles por esa credencial, no a todo GitHub.
- La coincidencia de LogisTech fue [diegoaragonmurillo-sys/Logis_Tech_Proyecto_Final](https://github.com/diegoaragonmurillo-sys/Logis_Tech_Proyecto_Final): público, estructura Android (app, Gradle/Kotlin), rama principal main en `060cb00fecba639f1d9f05c34d33c1054169e89e`, más nueve ramas feature. No tiene el informe F5 y no es el repositorio web Django/React actual. Solo se leyó metadato/estructura; no se clonó, alteró, configuró como origin ni recibió commits.
- La consulta del destino propuesto anthonyarana-debug/logistech-2.0 respondió 404: no existía visible para la cuenta. No se creó.

## Revisión de publicación

Se auditó el contenido Git completo alcanzable por ramas/etiquetas, no solo el árbol actual: seis commits y 279 blobs al inicio, mayor archivo 968 114 bytes. Ninguna ruta sensible, valor privado local conocido, JWT literal o patrón de token/clave detectado. Se compararon en memoria las claves locales de entorno/DEMO; el reporte no guarda sus valores. Plantillas permitidas: .env.example y deploy/production.env.example, con marcadores ficticios. Las claves sintéticas de pruebas no son credenciales de las cuentas DEMO ni de producción.

Se reforzó .gitignore: entornos, .env/DEMO, claves, gestores de credenciales, archivos de DB/dumps, backups, rutas de volúmenes y secretos locales. El auditor prueba veinte exclusiones representativas y reconoce firmas SQLite/pg_dump, además de nombres de archivo. No hay bases o volúmenes Docker versionados; la declaración de un volumen en Compose es configuración, no sus datos.

Las capturas existentes se habían inspeccionado en F4/F5: contienen datos académicos y formularios vacíos, sin contraseñas/tokens. Evidencias/CSV incluyen UUID, nombres DEMO, rutas locales y metadatos de equipo; no conceden acceso. La autoría Git conserva nombre/correo de commits anteriores. Estos metadatos quedarán visibles para los colaboradores del repositorio privado; no se reescribió la historia para eliminarlos. Las fuentes conservan sus licencias OFL; no se añadió una licencia distinta al proyecto.

Límites: el escaneo por patrones y comparación de valores conocidos no certifica ausencia absoluta de secretos desconocidos/rotados, ni realiza OCR de capturas. El futuro repositorio debe seguir privado y con acceso mínimo. Si apareciera una credencial real en un commit anterior, ignorarla o borrarla en HEAD no sería suficiente: detener publicación, revocarla y preparar saneamiento del historial. No hubo hallazgos que exigieran esa operación.

## Preparación realizada

- Rama local codex/preparacion-github, sin borrar ni reescribir fases anteriores.
- scripts/auditar_publicacion.py, sin red y sin mostrar valores secretos: revisa índice y todos los blobs alcanzables, incluidas ramas de fases; devuelve error ante hallazgos.
- .githooks/pre-push, activado solo en este repositorio: ejecuta el auditor y bloquea el nombre del remoto Android original. Es una barrera adicional, se puede omitir y **no verifica por sí mismo la visibilidad GitHub ni reemplaza autorización humana**. No se editó configuración Git global.
- docs/NUEVA_COMPUTADORA.md con instalación, clonación futura, secretos nuevos, migraciones, datos DEMO y coordinación de ramas. Clonar código no copia datos PostgreSQL.
- No se configuró origin, creó repositorio, transmitió código o hizo push.

Comprobaciones del auditor: cuatro tests de biblioteca estándar aprobados (plantilla segura, secreto artificial eliminado pero presente en historial, firma de dump con nombre inocente y ruta sensible Unicode); sin valores privados en la salida. Hook probado sin red: devuelve 1 al nombre Android y 0 para un destino ficticio local de prueba tras auditar el índice/historial. Ruff y diff sin errores. Ver [auditoría local](evidencias/github-auditoria-local.json) y [consulta GitHub de lectura](evidencias/github-lectura.json).

## Propuesta concreta pendiente de aprobación

Destino: `https://github.com/anthonyarana-debug/logistech-2.0`, visibilidad **PRIVATE**, repositorio vacío (sin README/licencia/gitignore generados por GitHub). Main predeterminado contendrá la preparación y F5; publicar también los puntos de control codex/fase-1-configuracion, codex/fase-2-autenticacion, codex/fase-3-api-crud, codex/fase-4-frontend, codex/fase-5-validacion y el master F0 con nombre remoto codex/fase-0-planificacion.

Tras autorización expresa: volver a comprobar que el nombre está libre y la cuenta es la correcta; crear como privado; verificar con GET la privacidad/propiedad; configurar origin con HTTPS sin credenciales en URL; auditar; realizar push atómico de las referencias indicadas sin force/mirror; fijar main como predeterminada si hiciera falta; verificar SHA remoto y un clon nuevo. No apuntar al Android ni reemplazar una historia remota existente. Si el destino ya existe, inspeccionarlo y detener cualquier sobrescritura.

El proyecto mantiene su estado académico F5: validado localmente, cloud parcial. Publicar el código en un repositorio GitHub privado **no despliega la aplicación ni satisface un cloud activo**.
