"""Build the updated academic report and the independent visual manual."""

import argparse
import json
import os
import subprocess
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image
from week13_manual_figures import FIGURES

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidencias/semana13-cierre"
CURRENT = ROOT / "docs/evidencias/semana13-integral"
NEW_FIGURES = {
    38: (
        "Navegar por las categorías",
        "Administrador de empresa u operador con lectura.",
        "Inicia sesión y abre Categories. La lista debe tener suficientes resultados para avanzar.",
        "fase5-pagination.png",
        [
            (64, 94, 220, 17, "field", "Aplica un filtro de nombre o condición."),
            (
                64,
                151,
                92,
                18,
                "action",
                "Usa Previous page o Next page y verifica el total.",
            ),
        ],
        "La lista cambia de página. Un filtro nuevo vuelve a la primera.",
        "Si Next page está inactivo, comprueba el total y quita los filtros innecesarios.",
    ),
    39: (
        "Recuperar una lista después de un error",
        "Administrador de empresa u operador con lectura.",
        "Abre Categories. La figura muestra una respuesta HTTP 503 simulada en Playwright.",
        "fase5-fault-503-SIMULATED.png",
        [
            (59, 123, 255, 22, "error", "Lee el aviso sin detalles internos."),
            (
                67,
                144,
                31,
                15,
                "action",
                "Pulsa Try again cuando se recupere el servicio.",
            ),
        ],
        "La lista vuelve a consultar la API y muestra las categorías.",
        "Si el aviso persiste, comprueba la red y reporta la hora del error al administrador.",
    ),
    40: (
        "Confirmar un rechazo en recepción",
        "Administrador de empresa con acceso a la caja.",
        "Busca la caja en Receptions y registra un rechazo con un motivo válido.",
        "recheck/rejection-admin-live.png",
        [
            (59, 89, 112, 26, "field", "Busca por QR o identificador interno."),
            (
                59,
                128,
                257,
                75,
                "action",
                "Verifica la fila Rejected y su motivo en la tabla.",
            ),
        ],
        "La recepción queda registrada y el historial conserva el evento.",
        "Si no aparece, verifica el ámbito de empresa y el identificador antes de reintentar.",
    ),
}


def picture_part(document, paragraph):
    image = paragraph._p.xpath(".//a:blip")[0]
    return document.part.related_parts[image.get(qn("r:embed"))]


def render_figures(document, scratch):
    source = scratch / "manual-originals"
    source.mkdir(parents=True, exist_ok=True)
    manifest = []
    for number, marks in FIGURES.items():
        part = picture_part(document, document.paragraphs[151 + 10 * number])
        path = source / f"{number:02d}.{part.partname.ext}"
        path.write_bytes(part.blob)
        manifest.append((number, path, marks))
    for number, data in NEW_FIGURES.items():
        manifest.append((number, CURRENT / data[3], data[4]))
    entries = []
    for number, path, marks in manifest:
        with Image.open(BytesIO(path.read_bytes())) as image:
            width, height = image.size
        entries.append(
            {
                "id": number,
                "path": str(path),
                "width": width,
                "height": height,
                "marks": marks,
            }
        )
    index = scratch / "manual-figures.json"
    index.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    target = scratch / "manual-callouts"
    subprocess.run(
        [
            os.environ.get("LOGISTECH_NODE", "node"),
            str(ROOT / "scripts/render_week13_callouts.cjs"),
            str(index),
            str(target),
        ],
        check=True,
    )
    return target


def steps(marks):
    return "\n".join(f"{index}. {entry[-1]}" for index, entry in enumerate(marks, 1))


def add_picture(paragraph, path, width):
    image = paragraph.add_run().add_picture(str(path), width=width)
    image._inline.docPr.set(
        "descr", "Captura auténtica con recuadros numerados y pasos en el texto"
    )


def field(paragraph, code):
    result = OxmlElement("w:fldSimple")
    result.set(qn("w:instr"), code)
    paragraph._p.append(result)


def rebuild_indexes(document):
    for name in ("Week 13 Table Caption", "Week 13 Figure Caption"):
        style = document.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = document.styles["Carga Normal"]
        style.paragraph_format.keep_with_next = True

    paragraphs = document.paragraphs
    manual = False
    for index, paragraph in enumerate(paragraphs):
        text = paragraph.text.strip()
        if "ANEXO A" in text and paragraph.style.name == "Heading 1":
            manual = True
        if "ANEXO B" in text and paragraph.style.name == "Heading 1":
            manual = False
        if text.startswith(("Tabla ", "Figura ")):
            is_table = text.startswith("Tabla ")
            if text.split()[-1].isdigit():
                title = paragraphs[index + 1]
                title.text = f"{text}. {title.text.strip()}"
                paragraph._p.getparent().remove(paragraph._p)
                paragraph = title
            if manual and not is_table:
                paragraph.text = f"Anexo A · {paragraph.text}"
            paragraph.style = (
                "Week 13 Table Caption" if is_table else "Week 13 Figure Caption"
            )

    entries = (
        ("ÍNDICE GENERAL", r'TOC \o "1-4" \h \z'),
        ("ÍNDICE DE TABLAS", r'TOC \t "Week 13 Table Caption,1" \h \z'),
        ("ÍNDICE DE FIGURAS", r'TOC \t "Week 13 Figure Caption,1" \h \z'),
    )
    controls = document._element.body.xpath("./w:sdt")[:3]
    for control, (title, code) in zip(controls, entries, strict=True):
        heading = document.add_paragraph(title)
        heading.runs[0].bold = True
        heading.alignment = 1
        heading.paragraph_format.keep_with_next = True
        contents = document.add_paragraph()
        field(contents, code)
        control.addprevious(heading._p)
        control.addprevious(contents._p)
        control.getparent().remove(control)


def append_procedure(document, number, path, before=None):
    title, role, prerequisites, _, marks, result, errors = NEW_FIGURES[number]

    def add(text="", style=None):
        return (
            before.insert_paragraph_before(text, style)
            if before
            else document.add_paragraph(text, style)
        )

    add(title, "Manual Heading1" if before else "Heading 1")
    add(f"Figura {number}. {title}").paragraph_format.keep_with_next = True
    add_picture(add(), path, Inches(5.75))
    add(f"Rol. {role}")
    add(f"Requisitos previos. {prerequisites}")
    add(steps(marks))
    add(f"Resultado esperado. {result}")
    add(f"Si ocurre un error. {errors}")


def revise_report(document, annotated):
    paragraphs = document.paragraphs
    paragraphs[7].runs[
        0
    ].text = "LogisTech 2.0. Informe académico unificado de Semana 13"
    paragraphs[31].text = "1. Informe académico unificado"
    for index, text in {
        102: "7. Procesos y servicios",
        103: "7.1. Registro y sesión",
        109: "7.2. Autorización e inventario",
        115: "7.3. Categorías, cajas y borrado",
        117: "8. API y manual técnico",
        121: "9. Resultados, incidencias y limitaciones",
        122: "9.1. Verificación histórica del entregable del 25 %",
        127: "9.2. Indicadores históricos de prueba y rendimiento",
        136: "10. Referencias",
        142: "11. Conclusiones",
        150: "13. ANEXO A — MANUAL DE USUARIO INTEGRADO",
        545: "14. ANEXO B — PRUEBAS DE CARGA Y PERSISTENCIA",
        580: "14.1. Protocolo de demostración en vivo ante el evaluador",
    }.items():
        paragraphs[index].text = text
    paragraphs[151].text = (
        "Las figuras 1–37 provienen del informe original. Las figuras 38–40 "
        "se obtuvieron durante Playwright en el cierre de Semana 13. Los recuadros "
        "numerados remiten a las acciones de cada procedimiento."
    )
    paragraphs[154].text = (
        "Para el ensayo de Semana 13, accede a https://localhost:8453 con la CA "
        "local de ensayo confiada, JavaScript y cookies. Los datos de acceso se "
        "entregan por un canal privado. La aplicación está publicada en https://logistech.stackpe.online."
    )
    conclusions = [
        "El núcleo inicial evolucionó hasta administrar empresas y seguir cajas por QR, recepción e historial.",
        "La paginación y el alcance por empresa quedaron comprobados en la API y en el navegador.",
        "El perfil local de 5.000 GET terminó con 20 usuarios virtuales, p95 de 39,94 ms y cero errores HTTP.",
        "La restauración independiente conservó ocho modelos y la prueba de cifrado rechazó una copia alterada.",
        "La publicación en Lightsail añadió evidencia para el decimotercer requisito. La aceptación comprobó TLS, salud y acceso de administrador.",
    ]
    observations = [
        "El perfil histórico de 2.500 GET con 20 VU excedió el umbral de 500 ms.",
        "La repetición con 10 VU pasó y la corrida de 5.000 cambió el ritmo entre solicitudes.",
        "Los datos de carga corresponden a un entorno local con 10.000 categorías sintéticas.",
        "La validación de despliegue debe incluir autenticación, datos persistentes y restauración desde una segunda red.",
        "El periodo 2026-I se conserva como dato de la portada histórica. El periodo de esta entrega requiere confirmación.",
    ]
    for i, text in enumerate(conclusions, 1):
        paragraphs[142 + i].text = f"{i}. {text}"
    paragraphs[148].insert_paragraph_before("12. Observaciones", "Heading 3")
    for i, text in enumerate(observations, 1):
        paragraphs[148].insert_paragraph_before(f"{i}. {text}", "Carga Normal")
    for number, marks in FIGURES.items():
        picture = paragraphs[151 + 10 * number]
        drawing = picture._p.xpath(".//wp:extent")[0]
        width = int(drawing.get("cx"))
        if number == 2:
            width = int(width * 0.88)
        picture.clear()
        add_picture(picture, annotated / f"{number}.png", width)
        paragraphs[153 + 10 * number].insert_paragraph_before(
            steps(marks), "Carga Normal"
        )
    for number in NEW_FIGURES:
        append_procedure(document, number, annotated / f"{number}.png", paragraphs[545])

    document.add_page_break()
    document.add_heading("15. ANEXO C — VALIDACIÓN DE SEMANA 13", level=1)
    document.add_paragraph(
        "La matriz aplica el mismo peso a los trece requisitos. Los trece tienen evidencia (100 % de cobertura del "
        "bloque del 80 %). La comprobación pública incluye TLS, salud, sesión y lectura paginada. Los resultados del 25 % "
        "y del anexo histórico conservan sus propios entornos y fechas."
    )
    document.add_paragraph("Tabla C1. Perfiles históricos de lectura paginada")
    table = document.add_table(rows=1, cols=5)
    table.style = document.tables[0].style
    for cell, label in zip(
        table.rows[0].cells,
        ("GET", "VU", "Media (ms)", "p95 (ms)", "Estado"),
        strict=True,
    ):
        cell.text = label
    for row in [
        ("100", "2", "30,36", "39,85", "Aprobado"),
        ("500", "5", "28,06", "42,42", "Aprobado"),
        ("1.000", "10", "29,21", "46,15", "Aprobado"),
        ("2.500", "20", "144,55", "734,64", "Superó el umbral"),
        ("2.500", "10", "36,95", "51,09", "Aprobado"),
        ("5.000", "20", "27,42", "39,94", "Aprobado"),
    ]:
        for cell, value in zip(table.add_row().cells, row, strict=True):
            cell.text = value
    document.add_paragraph(
        "Los perfiles completos tuvieron cero errores HTTP. El ensayo de 5.000 GET se realizó en la página "
        "400 con 10.000 categorías sintéticas y una pausa de 0,97 s por usuario virtual."
    )
    caption = document.add_paragraph("Figura C1. Latencia p95 del ensayo de paginación")
    caption.paragraph_format.keep_with_next = True
    document.add_picture(str(EVIDENCE / "capacity-p95.png"), width=Inches(5.75))
    document.add_heading("15.1. Producción, seguridad y recuperación", level=2)
    document.add_paragraph(
        "El ensayo usó React compilado, Caddy, Gunicorn y PostgreSQL privado. Trivy volvió a registrar cero "
        "CRITICAL y 48 HIGH residuales, con 47 en backend y uno en el proxy. Los hallazgos requieren "
        "revisión de exposición y seguimiento de parches. El backup restauró ocho modelos y el cifrado autenticado "
        "rechazó un archivo alterado. Las caídas controladas de PostgreSQL y Gunicorn volvieron a HTTP 200."
    )
    document.add_paragraph(
        "En la consola AWS se observó Free Plan con US$100, vigente hasta el 28 de abril de 2027, y el bundle "
        "Lightsail Ubuntu 24.04 de Ohio con 4 GB y doble pila por US$24 al mes. Se creó la instancia "
        "logistech-f7 y se asoció la IPv4 estática 18.221.197.129. El kernel corregido arrancó y "
        "PostgreSQL y Gunicorn quedaron saludables en AWS. Caddy obtuvo un certificado de Let’s Encrypt "
        "y se comprobaron landing, salud, sesión de administrador y consulta paginada desde Internet. Los informes técnicos del paquete conservan las "
        "salidas verificables de las pruebas, el presupuesto y la guía de aceptación."
    )

    for paragraph in paragraphs[19:22]:
        if not paragraph.text.strip() and not paragraph._p.xpath(
            ".//w:drawing | .//w:sectPr"
        ):
            paragraph._p.getparent().remove(paragraph._p)
    rebuild_indexes(document)


def build_manual(source, annotated):
    manual = Document()
    section = manual.sections[0]
    section.page_width, section.page_height = Inches(8.2677), Inches(11.6929)
    section.top_margin = section.bottom_margin = Inches(0.8)
    section.left_margin = section.right_margin = Inches(0.9)
    for name, size in (("Normal", 11), ("Title", 23), ("Heading 1", 16)):
        style = manual.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
    field(section.footer.paragraphs[0], "PAGE")
    for border in list(manual.styles["Title"].element.iter(qn("w:pBdr"))):
        border.getparent().remove(border)
    manual.add_paragraph("Manual visual de LogisTech 2.0", "Title")
    manual.add_paragraph("Semana 13 · Diseño y Desarrollo de Software · TECSUP")
    manual.add_paragraph(
        "Abre el ensayo por HTTPS con JavaScript y cookies habilitados. Recibe tus credenciales por un canal "
        "privado. Si tu cuenta de operador está pendiente, espera la asignación de empresa. Las imágenes de "
        "pruebas usan datos sintéticos. Los recuadros azules identifican campos, los verdes acciones, los "
        "naranjas advertencias y los rojos errores. Los números enlazan cada recuadro con un paso."
    )
    manual.add_paragraph("Índice de procedimientos", "Title")
    field(manual.add_paragraph(), 'TOC \\o "1-1" \\h \\z \\u')
    for number, marks in FIGURES.items():
        offset = 151 + 10 * number
        title = source.paragraphs[offset - 1].text.strip()
        manual.add_page_break()
        manual.add_heading(title, level=1)
        caption = manual.add_paragraph(f"Figura {number}. {title}")
        caption.paragraph_format.keep_with_next = True
        add_picture(manual.add_paragraph(), annotated / f"{number}.png", Inches(6.2))
        for index in (1,):
            manual.add_paragraph(source.paragraphs[offset + index].text)
        manual.add_paragraph(
            "Requisitos previos. Abre la ruta indicada y usa una cuenta con el rol señalado cuando aplique."
        )
        manual.add_paragraph(steps(marks))
        for index in (3, 4, 5):
            manual.add_paragraph(source.paragraphs[offset + index].text)
        if number == 29:
            manual.add_paragraph(
                "La imagen histórica muestra la carga de la tabla. La figura 36 muestra la recepción guardada."
            )
    for number in NEW_FIGURES:
        manual.add_page_break()
        append_procedure(manual, number, annotated / f"{number}.png")
    return manual


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("scratch", type=Path)
    args = parser.parse_args()
    args.scratch.mkdir(parents=True, exist_ok=True)
    annotated = render_figures(Document(args.source), args.scratch)
    source = Document(args.source)
    manual = build_manual(source, annotated)
    revise_report(source, annotated)
    target = ROOT / "output/documents"
    target.mkdir(parents=True, exist_ok=True)
    source.save(target / "LOGISTECH_INFORME_UNIFICADO_SEMANA_13.docx")
    manual.save(target / "LOGISTECH_MANUAL_USUARIO_VISUAL.docx")


if __name__ == "__main__":
    main()
