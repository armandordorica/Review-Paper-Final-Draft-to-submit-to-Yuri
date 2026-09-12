# Bibliography: Round-2 Reference Polish Audit

Scope: `bibliography.bib` (and rendered References in timestamped PDFs).

Latest refresh: 12-Sep-2026 (AE minor: title casing + preprint polish + Kang dedupe + Wikipedia CPM).

## Reviewer context used

- **Associate Editor (round 2):** title casing; replace preprints; dedupe Kang; replace Wikipedia CPM; wrong DOIs (separate).
- Full letter: `docs/agent/reviewers_round2.txt`.
- Plan: `docs/agent/round2_revision_plan.md`.
- Checklist progress: `docs/agent/preprint_checklist_progress.json`.

## Resolved

- **R2-REF1 (DONE).** Converted cited Title Case article/paper titles to sentence case, preserving proper nouns and acronyms with BibTeX braces where needed. Verified in `paper_2026-09-12_1435.pdf`. Writing rule added to `.cursor/skills/write-rl-paper/SKILL.md` §7H and root `SKILL.md`.

- **R2-REF2 (DONE).** Preprint / weak-source cites updated to published venues where available (AAAI, ICML, ECML PKDD, MLJ, IJCAI, IJECE, KDD, ICDM IEEE). Horizon and RecSim retained as arXiv (no archival proceedings); institutional landing-page URLs used as optional links. Lambert title corrected to current arXiv listing. Progress log: `docs/agent/preprint_checklist_progress.json`.

- **R2-REF3 (DONE).** Consolidated Kang & McAuley 2018 on `kang2018sasrec`; retargeted `\cite{Kang2018}`; removed duplicate key.

- **R2-REF5 (DONE).** History paragraph Wikipedia CPM cite → `hu2004performance`; removed `wikipedia-cpm` bib entry.

## Pending (other AE bibliography items)

- **R2-DOI1.** Fix confirmed wrong DOIs (`zhao2020jointly`, `wen2019learning`, `Mehrotra2020`, `Stigler1950`).
- **R2-REF4.** Switch to numbered citations (`acmnumeric`) — awaiting author confirmation.
