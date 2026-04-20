# CFT_analysis

## LaTeX cleanup utility

This repository includes a small helper to clean LaTeX files exported from DOCX/Pandoc.
It focuses on the structural issues highlighted in the analysis (excessive `quote` blocks,
minipage-heavy `longtable` layouts, and Unicode math symbols).

### Usage

```bash
python3 latex_cleanup.py path/to/document.tex
```

This writes `document.clean.tex` by default and prints a short summary of the changes.
Use `-o` to select a custom output path:

```bash
python3 latex_cleanup.py path/to/document.tex -o cleaned.tex
```

### What it fixes

- Removes nested `quote` environments to reduce indentation noise.
- Strips `minipage` wrappers from `longtable` bodies for simpler tables.
- Normalizes common Unicode math symbols to LaTeX commands.
- Flattens bibliography items that are wrapped in `quote` blocks.
