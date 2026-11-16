"""Check that texts of every language in languages.json fit a fixed-width widget.

Usage (from the repository root):
    QT_QPA_PLATFORM=offscreen PYTHONPATH=. .venv1/bin/python .github/skills/feature-dev-testing/check_text_fit.py \
        --width 190 Windows.Investments.13 --text "Some literal text"
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any

from PySide6.QtGui import QFontMetrics

from GUI.gui_constants import app, BASIC_FONT  # noqa: F401  # QApplication must exist before measuring fonts



LANGUAGES_FILE = Path(__file__).resolve().parents[3] / "languages.json"
DEFAULT_PADDING = 20


def get_text(language_texts:dict[str, Any], key_path:str) -> str:
    """Get a text of one language by a dotted path like `Windows.Investments.13`.

        Arguments
        ---------
            `language_texts` : (dict[str, Any]) - Texts of one language from languages.json.
            `key_path` : (str) - Dotted path to the text.
        Returns
        -------
            `str` - Text found by the path.
    """

    node:Any = language_texts
    for key in key_path.split("."):
        node = node[key]
    if not isinstance(node, str):
        raise ValueError(f"{key_path} isn't a text")
    return node


def main() -> None:
    """Print the width of each text and exit with code 1 if any text doesn't fit."""

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("keys", nargs="*", help="Dotted languages.json paths without the language, e.g. Windows.Investments.13")
    parser.add_argument("--text", action="append", default=[], help="Literal text to measure (repeatable)")
    parser.add_argument("--width", type=int, required=True, help="Widget width in px")
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING, help="Width kept free for padding in px")
    args = parser.parse_args()

    languages:dict[str, dict[str, Any]] = json.loads(LANGUAGES_FILE.read_text(encoding="utf-8"))
    metrics = QFontMetrics(BASIC_FONT)
    max_text_width = args.width - args.padding

    measured:list[tuple[str, str, str]] = [
        (language, key_path, get_text(texts, key_path))
        for key_path in args.keys for language, texts in languages.items()
    ]
    measured += [("-", "literal", text) for text in args.text]

    all_fit = True
    for language, key_path, text in measured:
        text_width = metrics.horizontalAdvance(text)
        fits = text_width <= max_text_width
        all_fit &= fits
        print(f"{'OK' if fits else 'TIGHT':5} {text_width:4} px  {language:11} {key_path:25} {text!r}")

    print(f"\nWidget {args.width} px, max text width {max_text_width} px (padding {args.padding} px)")
    sys.exit(0 if all_fit else 1)


if __name__ == "__main__":
    main()
