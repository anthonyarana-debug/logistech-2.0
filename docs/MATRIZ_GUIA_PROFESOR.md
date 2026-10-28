# Matriz de cumplimiento de la guía del profesor

Fuente: «Guía para la documentación de proyectos de software», Organización de Computadoras, Universidad Nacional del Sur, 2017, cinco páginas. Se leyó íntegramente y se verificó visualmente en la auditoría previa. No es una rúbrica ponderada: los estados indican cobertura documental, no aprobación académica.

Entrega principal: [INFORME_ACADEMICO](INFORME_ACADEMICO.md). La auditoría previa y el inventario de 37 archivos se entregaron fuera del repositorio antes de la autorización; esta matriz registra el resultado del ajuste. Los informes F0–F5 conservan su condición histórica.

| ID / página guía | Exigencia | Antes de la adaptación | Entrega / sección y evidencia | Estado / pendiente |
|---|---|---|---|---|
| G01 / 1–2 | Idea, necesidad y objetivos | Dispersos en README/informes | INFORME_ACADEMICO §1, objetivos verificables | Cubierto documentalmente |
| G02 / 2 | Usuarios y nivel de experiencia del lector | Roles existentes, audiencia implícita | Informe §1.4; ROLES_PERMISOS | Cubierto |
| G03 / 1–2 | Requisitos generales/funcionales | MATRIZ_ENTREGABLES, CHECKLIST | Informe §2.1; matriz original con evidencias | Cubierto |
| G04 / 2 | Restricciones no funcionales | SEGURIDAD, DISENO, rendimiento | Informe §2.2; SEGURIDAD y pruebas | Cubierto en alcance local; cloud parcial |
| G05 / 2 | Autoría, legacy, retrocompatibilidad | Antecedentes Android en auditoría | Informe §1.5 y límites explícitos | Parcial: identificación académica nominal humana; no auditoría/compatibilidad Android inventada |
| G06 / 2 | Alcances y limitaciones | Informes por fase | Informe §2.3 y §8; F6–F8 excluidas | Cubierto |
| G07 / 2 | Herramientas y planificación | PLAN, lockfiles, decisiones | Informe §3.1; DECISIONES_TECNICAS | Cubierto; sin metodología/equipo ficticios |
| G08 / 1–2 | Obtención e instalación | NUEVA_COMPUTADORA y README | Informe §3.2; guía corregida a repositorio público | Cubierto; adaptación todavía local hasta revisión |
| G09 / 2 | Prueba y ejecución | PRUEBAS y evidencias F5 | Informe §3.3/§8; scripts/verify_adaptation.py; informe de cierre | Cubierto con resultados reales separados de historia |
| G10 / 3 | Jerarquía y diagrama global | Arquitectura con texto futuro | Informe §4.1; ARQUITECTURA actualizada | Cubierto |
| G11 / 3 | Ficha de cada módulo y archivos | Descripciones breves | Informe §4.2: propósito, responsabilidad, restricciones y dependencias | Cubierto |
| G12 / 3–4 | Dependencias/tecnologías/decisiones | Versiones y ADR dispersos | Informe §4.3; lockfiles y DECISIONES_TECNICAS | Cubierto |
| G13 / 4 | Entidades, atributos, relaciones y gráficos | BASE_DE_DATOS/ER verificado F5 | Informe §5 con ER y tabla; Mermaid fuente conservada | Cubierto; tablas framework detalladas aparte |
| G14 / 4 | Entradas, internos y salidas | Implícitos en API/modelos | Informe §5, tabla de tratamiento de datos | Cubierto |
| G15 / 4 | Procesos, propósito, invocación, entradas/salidas | Guion y secuencias textuales | Informe §6; SESION.mmd y PROCESOS.mmd | Cubierto para funciones implementadas |
| G16 / 4–5 | Comentarios y documentación de interfaces | Comentarios y docstrings desiguales | API_INTERNA y comentarios/docstrings de puntos críticos existentes/nuevos | Cubierto en interfaces mantenidas; no documentación automática universal de cada helper |
| G17 / 5 | API: firmas, argumentos/tipos/retorno | ENDPOINTS orientado a REST | Informe §7; ENDPOINTS y API_INTERNA | Cubierto para contrato público e interfaces internas relevantes |
| G18 / 5 | Invocación/defaults/obligatoriedad | Guías separadas | Informe §3/§7; API_INTERNA y ENDPOINTS | Cubierto |
| G19 / 5 | TDAs y representación/limitaciones | Sin referencia conjunta | API_INTERNA: estado de sesión, errores, querysets y dominio; Informe §5 | Aplicado a estructuras reales, sin inventar TDAs propios |
| G20 / 5 | Conclusiones sobre decisiones, dificultades y experiencia | Cierres por fase | Informe §10, exactamente cinco conclusiones numeradas al final | Cubierto documentalmente |

## Condiciones adicionales del usuario

| Condición | Implementación / evidencia | Resultado |
|---|---|---|
| Documentación en español | Informe y guías Markdown | Cumplido |
| Inglés predeterminado / catálogo central | frontend/src/i18n; core/messages.py/labels.py; LANGUAGE_CODE=en | Implementado; regresión documentada en INFORME_ADAPTACION |
| Español opcional sin API externa | Estructura central preparada, sin selector incompleto | No habilitado; no es requisito obligatorio |
| Contratos, modelos, migraciones y datos estables | Checks y tests de idioma, metadata y valores del usuario | Sin renombrados/modelos/migraciones por traducción |
| Diseño conservado | Sin cambios de CSS ni segundo tema; responsive/axe/capturas nuevas | Industrial Precision conservado |
| Cinco conclusiones al final | Verificador estructural y revisión | Exactamente cinco |
| Cloud parcial | Informe §2.3/§8 y DESPLIEGUE | No se acredita despliegue inexistente |
| GitHub público | Consulta GET API pública: private=false, visibility=public | Documentación vigente corregida; registro de privacidad inicial histórico preservado |
| Sin fases nuevas ni push/despliegue | Rama local de adaptación; revisión de Git | Respetado; no publicación automática |

## Revisión humana pendiente

Confirmar identificación académica nominal, formato de entrega exigido por el profesor y evaluación de cloud. Completar lector de pantalla/zoom nativo/tacto físico si se requieren. El PDF original no obliga a usar Doxygen ni a producir un PDF final; se entrega Markdown con fuentes gráficas editables. La aprobación académica depende del profesor y de su rúbrica, no de esta matriz.
