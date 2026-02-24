from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


def _read_literal_dict(path: Path, variable_name: str) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    module = ast.parse(text, filename=str(path))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == variable_name:
                data = ast.literal_eval(node.value)
                if not isinstance(data, dict):
                    raise ValueError(f"{variable_name} is not a dict")
                return data
    raise ValueError(f"{path} does not contain '{variable_name}' assignment")


@lru_cache(maxsize=1)
def load_fake_db() -> Dict[str, Any]:
    base_dir = Path(__file__).resolve().parent
    src = base_dir / "FAKE_DB.json"
    return _read_literal_dict(src, "FAKE_DB")
