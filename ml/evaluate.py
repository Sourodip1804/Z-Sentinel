from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = ROOT / "ml" / "artifacts" / "evaluation.json"


def main() -> None:
    if not EVAL_PATH.exists():
        raise SystemExit("No evaluation.json found. Run python ml/train.py first.")
    payload = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    print(json.dumps(payload, indent=2))
    print("\nDisclaimer:", payload.get("disclaimer"))


if __name__ == "__main__":
    main()
