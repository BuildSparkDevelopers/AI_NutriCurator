$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
}

Write-Host "== AI_NutriCurator FakeDB test ==" -ForegroundColor Cyan

$pythonCheck = @"
from app.settings import settings
print("AI_DATA_SOURCE=", settings.AI_DATA_SOURCE)
"@

python -X utf8 -c $pythonCheck

$testScript = @"
from fastapi.testclient import TestClient

from app.main import app
from api.deps import get_current_user_id

app.dependency_overrides[get_current_user_id] = lambda: 2
client = TestClient(app)

test_cases = [
    {"name": "warning_path", "product_id": 199504000000},
    {"name": "safe_path", "product_id": 201905000000},
]

for case in test_cases:
    response = client.post("/api/v1/ai/analyze", json={"product_id": case["product_id"]})
    body = response.json()
    full_state = body.get("full_state_debug", {}) if isinstance(body, dict) else {}
    print("=" * 72)
    print(f"[{case['name']}] product_id={case['product_id']}")
    print("status_code=", response.status_code)
    print("status=", body.get("status"), "decision=", body.get("decision"))
    print(
        "keys=",
        [k for k in ("candidates", "sub_recommendations", "final_answer") if k in full_state],
    )
    print("cand=", len(full_state.get("candidates", []) or []))
    print("subs=", len(full_state.get("sub_recommendations", []) or []))
    print("final_answer=", (full_state.get("final_answer") or "")[:120])
"@

python -X utf8 -c $testScript

Write-Host "== done ==" -ForegroundColor Green
