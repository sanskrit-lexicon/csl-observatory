# Contributing

Contributions to `csl-observatory` are welcome. This repository ingests data from the wider CDSL ecosystem and produces dashboards and figures; contributions typically take one of these forms:

## What to contribute

- **New metrics.** Add a function to `scripts/compute_metrics.py` and a corresponding table or figure to `scripts/render_reports.py`.
- **New visualisations.** Add a Mermaid block to `reports/*.md` (validate via `gh api markdown -X POST -f text=...`).
- **Contributor map updates.** Edit `scripts/contributors_map.json` to fill in real names, ORCIDs, or role descriptions.
- **Article revisions.** Edit `article/article.md`. Run `pandoc article/article.md -o article.pdf --citeproc --bibliography refs.bib` locally.

## Workflow

1. Fork the repository.
2. Create a topic branch: `git checkout -b add-<short-description>`.
3. Make changes; run `python scripts/pull_data.py && python scripts/compute_metrics.py && python scripts/render_reports.py` if your change affects derived data.
4. Commit with a descriptive message; the data snapshot directory should reflect the date of the change.
5. Open a pull request; describe the metric or visualisation rationale.

## Licensing

By contributing, you agree your contributions are licensed under GPL-3.0 (code) or CC BY-SA 4.0 (data) consistent with the rest of the repository.
