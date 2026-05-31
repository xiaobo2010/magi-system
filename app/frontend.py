"""MAGI System Frontend — loads static HTML + JS"""

import os
from pathlib import Path

_STATIC_DIR = Path(__file__).parent / "static"


def render_html() -> str:
    """Return the complete HTML for the MAGI System frontend."""
    html_path = _STATIC_DIR / "index.html"
    return html_path.read_text(encoding="utf-8")
