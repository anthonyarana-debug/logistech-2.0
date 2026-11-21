# Auditoría de LogisTech Android

Se localizaron dos proyectos Kotlin en Descargas. La revisión y la compilación se hicieron a partir de `Proyectos Extraidos/Logist_Tech_Fixed/Logist_Tech_Fixed`. El proyecto original se consultó en solo lectura y el build se ejecutó en una copia de trabajo aparte. La variante revisada usa Kotlin, Compose, Android SDK 36, API mínima 26, CameraX 1.3.4, OCR ML Kit 16.0.0 y lectura de códigos 17.2.0. Referencias del proyecto móvil: `app/build.gradle.kts:11`, `AndroidManifest.xml:4`, `scanner/ScannerScreen.kt:284`.

| Área | Comportamiento móvil observado | Adaptación a LogisTech 2.0 |
|---|---|---|
| Sesión | `auth/SessionManager.kt:3` conserva ID, nombre y rol local. Expone roles despacho y banda. | Login real con CSRF, JWT en memoria, cookie HttpOnly renovable y roles del servidor. |
| Cámara | CameraX y ML Kit recuperan el valor crudo del QR. OCR tiene procesamiento separado. | Reutilizar el escáner. Resolver `logistech:box:<uuid>`, UUID o código `CJ-…` contra `GET /identification/resolve/`. |
| Formato de QR | `ocr/OcrProcessor.kt:95` espera un JSON. El método de registro de caja aparece en el mismo archivo. | Usar el identificador que resuelve la API y obtener los datos autorizados desde Django. |
| Recepción e historial | `history/HistorialManager.kt:28` agrega eventos al historial local. | Enviar `POST /receipts/` con `Idempotency-Key` y validar el historial persistido en la web. |

`gradlew.bat --no-daemon assembleDebug` compiló la copia con Android SDK instalado y acceso a dependencias. El intento offline falló porque el artefacto Foojay Resolver no estaba en caché. El APK debug pasó la verificación de firma. ADB instaló el APK en el emulador, con la opción `-t` para esta variante de prueba. [Evidencia ADB y SHA-256](evidencias/semana16/android.txt)

El emulador con páginas de 16 KB mostró un aviso de alineación de bibliotecas nativas. Después de aceptarlo, el prototipo abrió la pantalla de identificación local. La compatibilidad nativa de 16 KB queda pendiente de actualizar y verificar en un teléfono. [Aviso del emulador](evidencias/semana16/android-compatibilidad-16kb.png) · [Pantalla de identificación](evidencias/semana16/android-login.png)

La adaptación Kotlin puede reutilizar cámara, OCR y UI. La estimación inicial es de 8–16 horas para cliente HTTPS, sesión, identificación, recepción y pruebas. Un MVP Flutter equivalente se estima en 16–28 horas porque requiere integrar la cámara y construir esas mismas pantallas y flujos. El resultado de este APK acredita instalación de un prototipo móvil. Quedan pendientes la integración de la API, la prueba en teléfono físico y el flujo de recepción visible en la web. [Contrato de integración](ANDROID_COMPATIBILIDAD.md)
