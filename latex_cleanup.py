#!/usr/bin/env python3
"""Utilities for cleaning LaTeX exported from DOCX/Pandoc."""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CleanupStats:
    removed_quote_blocks: int
    unicode_replacements: int
    simplified_longtables: int
    normalized_bibliography_items: int


QUOTE_BLOCK_PATTERN = re.compile(
    r"\\begin\{quote\}\s*(.*?)\s*\\end\{quote\}",
    re.DOTALL,
)

LONGTABLE_PATTERN = re.compile(
    r"\\begin\{longtable\}\{(?P<cols>[^}]*)\}(?P<body>.*?)\\end\{longtable\}",
    re.DOTALL,
)

MINIPAGE_PATTERN = re.compile(
    r"\\begin\{minipage\}\[[^\]]*\]\{[^}]*\}(?P<body>.*?)\\end\{minipage\}",
    re.DOTALL,
)

BIBITEM_QUOTE_PATTERN = re.compile(
    r"(?P<item>\\item)\s*\\begin\{quote\}\s*(?P<body>.*?)\s*\\end\{quote\}",
    re.DOTALL,
)

UNICODE_MATH_REPLACEMENTS = {
    "Ʈ": r"\\tau",
    "𝒵": r"\\mathcal{Z}",
    "ℤ": r"\\mathbb{Z}",
    "ℝ": r"\\mathbb{R}",
    "ℚ": r"\\mathbb{Q}",
    "ℕ": r"\\mathbb{N}",
}


def remove_quote_blocks(text: str) -> tuple[str, int]:
    def replacer(match: re.Match) -> str:
        return match.group(1).strip()

    new_text, count = QUOTE_BLOCK_PATTERN.subn(replacer, text)
    return new_text, count


def normalize_unicode_math(text: str) -> tuple[str, int]:
    count = 0
    for char, replacement in UNICODE_MATH_REPLACEMENTS.items():
        if char in text:
            count += text.count(char)
            text = text.replace(char, replacement)
    return text, count


def _strip_minipages(body: str) -> str:
    def replacer(match: re.Match) -> str:
        return match.group("body").strip()

    stripped, _ = MINIPAGE_PATTERN.subn(replacer, body)
    return stripped


def simplify_longtables(text: str) -> tuple[str, int]:
    simplified = 0

    def replacer(match: re.Match) -> str:
        nonlocal simplified
        cols = match.group("cols")
        body = match.group("body")
        new_body = _strip_minipages(body)
        if new_body != body:
            simplified += 1
        return f"\\begin{{longtable}}{{{cols}}}{new_body}\\end{{longtable}}"

    new_text = LONGTABLE_PATTERN.sub(replacer, text)
    return new_text, simplified


def normalize_bibliography_items(text: str) -> tuple[str, int]:
    def replacer(match: re.Match) -> str:
        return f"{match.group('item')} {match.group('body').strip()}"

    new_text, count = BIBITEM_QUOTE_PATTERN.subn(replacer, text)
    return new_text, count


def cleanup_latex(text: str) -> tuple[str, CleanupStats]:
    text, quote_count = remove_quote_blocks(text)
    text, unicode_count = normalize_unicode_math(text)
    text, simplified_longtable = simplify_longtables(text)
    text, bib_count = normalize_bibliography_items(text)

    stats = CleanupStats(
        removed_quote_blocks=quote_count,
        unicode_replacements=unicode_count,
        simplified_longtables=simplified_longtable,
        normalized_bibliography_items=bib_count,
    )
    return text, stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean up LaTeX generated from DOCX or Pandoc exports.",
    )
    parser.add_argument("input", type=Path, help="Path to the input LaTeX file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional output path. Defaults to <input>.clean.tex",
    )
    args = parser.parse_args()

    input_path = args.input
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_path = args.output or input_path.with_suffix(".clean.tex")
    original_text = input_path.read_text(encoding="utf-8")
    cleaned_text, stats = cleanup_latex(original_text)
    output_path.write_text(cleaned_text, encoding="utf-8")

    print("Cleanup summary:")
    print(f"- Removed quote blocks: {stats.removed_quote_blocks}")
    print(f"- Unicode replacements: {stats.unicode_replacements}")
    print(f"- Simplified longtables: {stats.simplified_longtables}")
    print(f"- Normalized bibliography items: {stats.normalized_bibliography_items}")
    print(f"Saved cleaned file to: {output_path}")


if __name__ == "__main__":
    main()
