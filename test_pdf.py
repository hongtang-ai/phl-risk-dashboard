"""Local smoke test: generate PHL PDF from demo case and write to disk."""

from __future__ import annotations

from pathlib import Path

from analyzer import load_demo_case
from ui.pdf_export import generate_pdf_report


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    case = load_demo_case()
    filename, pdf_bytes = generate_pdf_report(case)
    out_path = out_dir / filename
    out_path.write_bytes(pdf_bytes)
    print(f"Wrote {out_path} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    main()
