from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"
SCHEMA_PATH = ROOT / "schema" / "triage_schema.json"
GOLDEN_PATH = ROOT / "data" / "golden_triage_results.json"
