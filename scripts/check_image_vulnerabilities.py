"""Gate full Trivy reports without hiding unfixed findings or accepting missing scans."""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Provide one or more full Trivy JSON report paths.")
    blocked = False
    for filename in sys.argv[1:]:
        report = json.loads(Path(filename).read_text(encoding="utf-8"))
        if "Results" not in report or "Metadata" not in report:
            raise SystemExit(f"Invalid scan: {filename}")
        findings = [
            v for result in report["Results"] for v in result.get("Vulnerabilities", [])
        ]
        critical = [v for v in findings if v["Severity"] == "CRITICAL"]
        fixable = [
            v for v in findings if v["Severity"] == "HIGH" and v.get("FixedVersion")
        ]
        unfixed = [
            v for v in findings if v["Severity"] == "HIGH" and not v.get("FixedVersion")
        ]
        print(
            f"{Path(filename).name}: critical={len(critical)}, fixable_high={len(fixable)}, unfixed_high={len(unfixed)}"
        )
        blocked |= bool(critical or fixable)
    print(
        "Unfixed findings still require documented review before any public deployment."
    )
    raise SystemExit(int(blocked))


if __name__ == "__main__":
    main()
