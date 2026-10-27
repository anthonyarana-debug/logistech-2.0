"""Controles negativos del auditor en repositorios temporales, sin red ni secretos reales."""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "auditar_publicacion.py"
spec = importlib.util.spec_from_file_location("publication_audit", SOURCE)
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)


class PublicationAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="logistech-git-audit-")
        self.root = Path(self.temporary.name).resolve()
        self.assertEqual(self.root.parent, Path(tempfile.gettempdir()).resolve())
        self.git("init", "-q")
        self.git("config", "user.name", "Prueba local")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        (self.root / ".gitignore").write_text(
            (SOURCE.parents[1] / ".gitignore").read_text(encoding="utf-8"), encoding="utf-8"
        )
        (self.root / ".env.example").write_text("SECRET_KEY=REEMPLAZAR_POR_VALOR_LOCAL\n")
        self.git("add", ".gitignore", ".env.example")
        self.git("commit", "-qm", "Base de prueba sin secretos")

    def tearDown(self):
        self.temporary.cleanup()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.DEVNULL)

    def audit(self):
        with patch.object(auditor, "ROOT", self.root):
            return auditor.audit()

    def test_safe_template_and_ignore_rules(self):
        result = self.audit()
        self.assertEqual(result["hallazgos"], [])
        self.assertEqual(result["exclusiones_comprobadas"], 20)

    def test_deleted_secret_is_still_found_in_history_without_disclosure(self):
        artificial = "ghp_" + "A" * 36
        (self.root / ".env").write_text("TOKEN=" + artificial)
        self.git("add", "-f", ".env")
        self.git("commit", "-qm", "Caso negativo artificial")
        self.git("rm", "-q", "--", ".env")
        self.git("commit", "-qm", "Retirar archivo del arbol actual")
        result = self.audit()
        self.assertTrue(any(item["tipo"] == "token_github" for item in result["hallazgos"]))
        self.assertTrue(any(item["tipo"] == "ruta_sensible" for item in result["hallazgos"]))
        self.assertNotIn(artificial, str(result))

    def test_database_signature_detected_even_with_innocent_filename(self):
        (self.root / "datos.bin").write_bytes(b"PGDMP" + b"fixture artificial, sin base real")
        self.git("add", "datos.bin")
        self.git("commit", "-qm", "Caso negativo de firma")
        result = self.audit()
        self.assertTrue(
            any(item["tipo"] == "base_o_dump_por_contenido" for item in result["hallazgos"])
        )

    def test_sensitive_path_with_unicode_parent_is_not_hidden_by_git_quoting(self):
        folder = self.root / "área privada"
        folder.mkdir()
        (folder / ".env").write_text("LOCAL=valor-ficticio")
        self.git("add", "-f", "área privada/.env")
        self.git("commit", "-qm", "Caso negativo de nombre Unicode")
        self.assertTrue(any(item["tipo"] == "ruta_sensible" for item in self.audit()["hallazgos"]))


if __name__ == "__main__":
    unittest.main()
