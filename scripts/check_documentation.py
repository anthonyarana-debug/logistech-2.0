"""Check the academic report's final conclusions and relative document links."""

import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = [
    "INFORME_ACADEMICO.md", "MATRIZ_GUIA_PROFESOR.md", "API_INTERNA.md",
    "INTERNACIONALIZACION.md", "INVENTARIO_IDIOMA.md", "INFORME_ADAPTACION.md",
]


def main():
    errors = []
    for name in DOCUMENTS:
        path = ROOT / "docs" / name
        if not path.is_file():
            errors.append(f"Missing document: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("http:", "https:", "#")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not (path.parent / target).exists():
                errors.append(f"Broken relative link in {name}: {target}")
    report = (ROOT / "docs/INFORME_ACADEMICO.md").read_text(encoding="utf-8")
    ending = report.rsplit("## 10. Conclusiones", 1)
    numbers = re.findall(r"^(\d+)\. ", ending[-1], flags=re.MULTILINE)
    if len(ending) != 2 or numbers != ["1", "2", "3", "4", "5"]:
        errors.append("Exactly five numbered conclusions are required")
    if re.search(r"^#{1,6} ", ending[-1], flags=re.MULTILINE):
        errors.append("Conclusions must be the final section")
    if "PARCIAL" not in report or "sin aplicación desplegada externamente" not in report:
        errors.append("The cloud limitation must remain explicit")
    print(json.dumps({"documents": len(DOCUMENTS), "conclusions": numbers, "errors": errors}))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
