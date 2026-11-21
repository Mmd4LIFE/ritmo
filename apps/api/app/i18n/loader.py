from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DIR = Path(__file__).parent


@lru_cache
def _load(locale: str) -> dict[str, str]:
    path = _DIR / f"{locale}.json"
    if not path.exists():
        path = _DIR / "en.json"
    return json.loads(path.read_text(encoding="utf-8"))


def t(locale: str, key: str, **kwargs: object) -> str:
    catalog = _load(locale if locale in ("en", "fa") else "en")
    template = catalog.get(key) or _load("en").get(key, key)
    try:
        return template.format(**kwargs)
    except Exception:
        return template
