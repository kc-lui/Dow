"""Run the Dow data-integrity checks, save the report under reports/, exit 1 on any error."""
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dowtheory.cli import run_check


def main() -> int:
    status, report = run_check()
    out = ROOT / "reports" / f"integrity_{datetime.now():%Y%m%d_%H%M%S}.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"Report written to {out}")
    return status


if __name__ == "__main__":
    sys.exit(main())
