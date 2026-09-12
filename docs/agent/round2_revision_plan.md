# Round-2 Minor Revision Plan (ACM TORS)

**Decision:** Minor revision  
**Deadline:** 04-Oct-2026  
**Source letter:** `docs/agent/reviewers_round2.txt`  
**Manuscript under revision:** `paper.tex` + `bibliography.bib`  
**Prior round (for context only):** `docs/agent/reviewers.txt` responds to `original_submission_paper.pdf`  
**Working rule:** One-by-one approval. Propose each change, wait for explicit go-ahead, then edit. Do not change `paper.tex` / `bibliography.bib` until approved.

Latest refresh: 12-Sep-2026 — R2-REF1/2/3/5 applied (title casing + preprint/weak-source polish + Kang dedupe + Wikipedia CPM); reviewer-response draft updated accordingly. Remaining: DOIs/AI disclosure, claim softens, tables, Section 3, R1 taxonomy, numbered cites.

---

## Decision context

- Associate Editor: paper substantially improved; remaining issues are mostly reference hygiene + a few claim/table accuracy fixes.
- Reviewer 1: **Accept**, with one substantive ask (Section 4.4 state-space taxonomy: Markovianity vs Expressiveness; SlateQ vs PinnerFormer contrast).
- Deliverables for resubmission: revised PDF + cover letter explaining changes.

---

## Author decisions already recorded

| Question | Decision |
|---|---|
| AI used for citation search / bib formatting / prose drafting? | Yes (generic tool wording; no tool name) |
| ACM AI disclosure? | Add Methods-section disclosure (citation search + bibliography formatting are research-data-source work under ACM Authorship Policy, May 2026) |
| Edit workflow | One-by-one approval before any `paper.tex` / `bibliography.bib` change |

---

## Priority queue (recommended order)

Work AE not-so-minor and R1 Accept-blocker first, then AE minor reference polish, then cover letter.

| Order | ID | Severity | Owner | Status | One-line |
|---:|---|---|---|---|---|
| 1 | R2-AI1 | Not-so-minor / AE | Methodology | PENDING APPROVAL | Draft AI-use disclosure paragraph |
| 2 | R2-DOI1 | Not-so-minor / AE | Bibliography | INVESTIGATED | Fix confirmed wrong DOIs |
| 3 | R2-CITE1 | Not-so-minor / AE | Introduction | LOCATED | Revise Chen et al. 2022 / "supervised prediction" claim |
| 4 | R2-CITE2 | Not-so-minor / AE | Introduction | LOCATED | Soften off-policy estimator generalization |
| 5 | R2-CITE3 | Not-so-minor / AE | Introduction | LOCATED | Soften "SL ignores policy-induced distribution shifts" |
| 6 | R2-TAB1 | Not-so-minor / AE | Table utility / Zhao 2020 | INVESTIGATED | Correct Zhao et al. 2020 blended utility formula |
| 7 | R2-TAB2 | Not-so-minor / AE | Table utility / LinkedIn | LOCATED | Clarify why Yan et al. 2020 is in the table |
| 8 | R2-HIST1 | Not-so-minor / AE | Section 3 | PARTIAL | Remove / soften "RL is next step" vs parallel co-evolution |
| 9 | R2-STATE1 | Reviewer 1 | Section 4.4 / state space | PENDING | Rewrite Markovianity vs Expressiveness cells + SlateQ/PinnerFormer contrast |
| 10 | R2-ABBR1 | Minor / AE | Introduction | LOCATED | Expand SL at first use |
| 11 | R2-REF1 | Minor / AE | Bibliography | DONE | Title case → sentence case for cited entries |
| 12 | R2-REF2 | Minor / AE | Bibliography | DONE (checklist applied) | Preprint → published where available; keeps documented |
| 13 | R2-REF3 | Minor / AE | Bibliography + tex | DONE | Deduplicated Kang & McAuley 2018 |
| 14 | R2-REF4 | Minor / AE | Global style | PENDING APPROVAL | Switch author-year → numbered citations |
| 15 | R2-REF5 | Minor / AE | History / CPM | DONE | Wikipedia CPM → hu2004performance |
| 16 | R2-COVER | Submission | Cover letter | DRAFTED | Draft response letter in plan (incl. Horizon keep-as-arXiv explanation) |

---

## Item-by-item plan

### R2-AI1 — AI-use disclosure (AE)

**AE quote:** *"Some DOIs ... (which I assume is a result of AI use, which should be declared in the paper)"*

**ACM policy note (May 14, 2026 Authorship Policy):**
- AI used to assist writing: disclosure **not** required.
- AI used in research lifecycle / creation-selection of data sources (incl. candidate paper discovery and bibliography construction for a survey): disclose specific uses in the **Methods** section.
- Authors remain responsible for citation integrity (fabricated / wrong DOIs are content-integrity issues regardless of disclosure).

**Proposed location:** end of Section 2 (Paper Collection Methodology), after the "153 papers" paragraph (~line 127), before the design-questions paragraph.

**Proposed text (for approval):**

```latex
A large language model-based assistant was used to help identify
candidate papers and to draft or format bibliography entries.
All cited works were subsequently verified by the authors against
primary sources (published PDFs, venue pages, or Crossref metadata),
and any incorrect metadata, including mismatched DOIs, were corrected
before submission of this revision. The assistant was not used to
generate experimental results, figures, or numerical findings.
```

**Also mention in cover letter** that DOIs were audited and corrected.

**Approval needed before edit.**

---

### R2-DOI1 — Wrong DOIs (AE)

**AE examples:** Mehrotra et al., Wen et al. 2019, Zhao et al. 2020, and others.

**Investigation done:** Crossref audit of all 19 bib entries that currently have a `doi` field (`scripts/audit_dois.py`). Result: **4 mismatches / 19**.

| Bib key | Claimed paper | Current DOI resolves to | Correct DOI |
|---|---|---|---|
| `zhao2020jointly` | Jointly Learning to Recommend and Advertise | Graph Attention Networks over Edge Content-Based Channels | `10.1145/3394486.3403384` |
| `wen2019learning` | Multi-objective rewards / utility (IJCAI) | Deep Cascade Generation on Point Sets | `10.24963/ijcai.2019/532` (+ fix title to "...Contextual Bandits for Personalized Ranking") |
| `Mehrotra2020` | Bandit Based Optimization... Music Streaming | USAD | `10.1145/3394486.3403374` |
| `Stigler1950` | The Development of Utility Theory. I | Unrelated antitrust paper | `10.1086/256962` |

**Note:** AE said "Mehrotra et al, 2018"; the cited Spotify multi-objective bandit paper in our bib is `Mehrotra2020` (KDD 2020). Separate `Mehrotra2018` exists (CIKM fair marketplace) and currently has **no** DOI field. Confirm in cover letter which paper was flagged.

**Follow-up (not yet done):**
- Spot-check high-risk entries without DOIs (venue/year/title consistency).
- Optionally add correct DOIs for cited entries that lack them (not AE-required, but improves polish).

**Approval needed before bib edits.**

---

### R2-CITE1 — Chen et al. 2022 / "supervised prediction" (AE)

**AE quote:** *"Rather than replacing SL, RL can be viewed as embedding supervised prediction within a sequential control framework [Chen et al. 2022]." → Not sure where this is indicated... Maybe avoid the term "supervised prediction"*

**Location:** Introduction ~line 105; citation key `chen2022off` = "Off-policy actor-critic for recommender systems" (RecSys 2022).

**Plan:**
1. Re-read Chen et al. 2022 for what it actually supports (off-policy actor-critic / offline RL for recommenders).
2. Rewrite the sentence so the claim matches the paper, **or** drop/replace the citation.
3. Avoid "supervised prediction" phrasing as AE suggested.
4. Double-check any technical definition nearby.

**Draft rewrite direction (not final wording):** RL can complement SL by using learned value estimates or rewards from predictive models inside a sequential decision objective, citing Chen for the actor-critic / off-policy recommender setting rather than for a general "embedding SL" claim.

**Approval needed before prose edit.**

---

### R2-CITE2 — Off-policy estimator overgeneralization (AE)

**AE quote:** *"Second, RL leverages off-policy estimators that re-weight observed trajectories..." I don't think this is generally true*

**Location:** Introduction ~line 105.

**Plan:** Narrow to offline / off-policy evaluation and learning settings that use importance weighting (IPS/DR), rather than stating it as a property of RL in general. Keep `swaminathan2015counterfactual` (or similar) only for the narrowed claim.

**Approval needed before prose edit.**

---

### R2-CITE3 — "SL ignores policy-induced distribution shifts" (AE)

**AE quote:** *"First, SL ignores policy-induced distribution shifts" is maybe also too strong*

**Location:** Introduction ~line 102.

**Plan:** Soften to something like: standard supervised training on logged interactions typically does **not** model how a changed ranking policy shifts the future data distribution, unless explicit causal / off-policy machinery is added. Avoid absolute "ignores."

**Approval needed before prose edit.**

---

### R2-TAB1 — Zhao et al. 2020 blended utility in Table 6 (AE)

**AE quote:** formulas should match the original; possible confusion with Zhao et al. 2021.

**Location:** `tab:utility-comparison` (~lines 483–500) and surrounding critical-comparison prose (~584–590).

**Investigation:** Zhao et al. 2020 (arXiv 2003.00097 / KDD) does **not** use  
`R_total = α R_rec + β R_ad`.  
It uses **separate** rewards (RS: income/dwell time; AS: continue/leave) and blends revenue with long-term Q at **ad-selection scoring**:  
`Score = Q(s_t, a_t^{as}) + α · rev_t(a_t^{as})`.  
The table formula appears closer to DEAR (Zhao et al. 2021) style.

**Plan:**
1. Replace Zhao 2020 table cells (organic / ads / blended) with formulas faithful to the 2020 paper.
2. Keep DEAR 2021 row as-is after verifying against DEAR.
3. Update the "Blending mechanism" / "Reported results" paragraphs so they no longer attribute the wrong additive formula to Zhao 2020.
4. In cover letter: acknowledge the 2020/2021 mix-up and state the correction.

**Approval needed before table/prose edit.**

---

### R2-TAB2 — LinkedIn / Yan et al. 2020 in Table 6 (AE)

**AE quote:** Yan et al. 2020 is not RL; unclear why it appears in a table in an RL paper.

**Location:** `tab:utility-comparison` LinkedIn row; also action-space table and multiple body cites.

**Plan:** Keep the row (useful non-RL baseline for joint ad/organic utility), but:
1. Add an explicit note in the table caption and/or opening of the critical-comparison paragraph that the table includes both RL reward formulations and closely related non-RL constrained-optimization utilities used for the same joint ranking problem.
2. Optionally tag the LinkedIn row as "constrained optimization (non-RL)" in the Company/Paper cell.
3. Audit other Yan et al. mentions so they are not implied to be RL deployments.

**Approval needed before table/prose edit.**

---

### R2-HIST1 — Section 3 progression vs parallel co-evolution (AE)

**AE quote:** suggests progression heuristics → SL → DL → bandits → RL, while also saying things happen in parallel near Fig 1; also "RL is the next step."

**Locations to check:**
- Figure 1 / timeline caption (~line 160).
- History subsections 3.1–3.2 (~230–260), especially bandits → RL transition (~260).
- Any sentence that calls RL the "next step" after ad modeling / deep learning.

**Plan:**
1. Grep for "next step", "evolved into", "superseded", "progression", "replaced by".
2. Keep chronological *adoption* framing; remove language that implies a strict replacement sequence.
3. Align body text with the existing parallel / overlapping timeline caption.

**Status:** partial (heuristics→ML→bandits language located; exact "next step" sentence still to be grepped before proposing a rewrite).

---

### R2-STATE1 — State-space taxonomy (Reviewer 1; Accept with this fix)

**R1 quotes:** Markovianity and Expressiveness yield near-duplicate table cells (PinnerFormer, TransAct); focus Markovianity on compression for next-state prediction, Expressiveness on missing dimensions; make SlateQ slate-so-far vs PinnerFormer long-horizon contrast explicit.

**Location:** Section 4.3 / state space (~662–744), especially `tab:state-space-comparison` and surrounding prose. (R1 says "Section 4.4"; verify numbering in compiled PDF vs source.)

**Plan:**
1. Rewrite Markovianity and Expressiveness rows for PinnerFormer and TransAct so they are non-redundant (use R1's suggested framing).
2. Check other columns (SlateQ, DEAR, DIN, etc.) for the same redundancy.
3. Add a short dedicated paragraph contrasting SlateQ's immediate slate-so-far state with PinnerFormer's multi-week user-history embedding (decision horizon, what is compressed, what is left out, when each is appropriate).
4. Refresh `docs/agent/state_space_citation_audit.md` after the edit.

**Approval needed before table/prose edit.**

---

### R2-ABBR1 — Expand SL (AE)

**Location:** Introduction ~line 102 (first "SL" use); "supervised machine learning" appears earlier (~line 99) without "(SL)".

**Plan:** On first mention, write `supervised learning (SL)` (or attach `(SL)` to the earlier supervised-ML sentence), then use SL thereafter. Sweep for any other undefined abbreviations introduced in Intro.

**Approval needed before prose edit.**

---

### R2-REF1 — Title case consistency (AE)

**AE quote:** *"Please use upper-case and lower-case notations consistently"* (under References need polishing).

**Investigation (12-Sep-2026):** Among titles cited in `paper.tex` (115 entries):
- **Sentence case: 85** (majority / current de facto style)
- **Title Case: 29**
- **Mixed: 1** (`wikipedia-cpm`, already scheduled for removal under R2-REF5)

ACM Reference Format conventionally uses **sentence case** for paper/article titles. Recommended rule: convert all **cited** Title Case titles to sentence case; preserve proper nouns (Google, Instagram, Meta, Thompson, Yahoo, Overture, SlateQ) and acronyms (PPC, CTR, RL, etc.).

**Cited Title Case keys to convert (29):**
`kant2021history`, `ellam2003overture`, `wsj2003yahoooverture`, `russo2018tutorial`, `kang2018sasrec`, `Kang2018`, `agarwal2020optimistic`, `Mehrotra2020`, `Jannach2023`, `Zhou2019`, `Zhou2018`, `sagtani2024ad`, `auer2002finite`, `chen2009large`, `agarwal2019online`, `silberstein2023combating`, `mcdonald2023spotify`, `wen2019learning`, `kuleshov2014algorithms`, `burtini2015improving`, `vorotilov2023scaling`, `deffayet2022offline`, `van2024practical`, `xu2023optimizing`, `ie2019slateq`, `zhao2020jointly`, `nielsen2017advertising`, `zhang2024scaling`, `Sutton1998`.

**Out of scope for this item unless asked:** uncited bib entries; booktitle/journal venue casing; math notation in the body.

**Status:** DONE (12-Sep-2026). All cited Title Case titles converted to sentence case. Verified in `paper_2026-09-12_1435.pdf` References. Rule recorded in `.cursor/skills/write-rl-paper/SKILL.md` §7H and root `SKILL.md` (Bibliography Title Casing).

**Resolved queue (cited Title Case only):**
1. `kant2021history` — DONE
2. `ellam2003overture` — DONE
3. `wsj2003yahoooverture` — DONE
4. `russo2018tutorial` — DONE
5. `kang2018sasrec` / `Kang2018` — DONE (casing only; key dedupe remains R2-REF3)
6. `agarwal2020optimistic` — DONE
7. `Mehrotra2020` — DONE
8. `Jannach2023` — DONE
9. `Zhou2019` — DONE
10. `Zhou2018` — DONE
11. `sagtani2024ad` — DONE
12. `auer2002finite` — DONE
13. `chen2009large` — DONE
14. `agarwal2019online` — DONE
15. `silberstein2023combating` — DONE
16. `mcdonald2023spotify` — DONE
17. `wen2019learning` — DONE
18. `kuleshov2014algorithms` — DONE
19. `burtini2015improving` — DONE
20. `vorotilov2023scaling` — DONE
21. `deffayet2022offline` — DONE
22. `van2024practical` — DONE
23. `xu2023optimizing` — DONE
24. `ie2019slateq` — DONE
25. `zhao2020jointly` — DONE
26. `nielsen2017advertising` — DONE
27. `zhang2024scaling` — DONE
28. `Sutton1998` — DONE

---

### R2-REF2 — Preprints → published versions (AE)

**AE quote:** *"Replace references to preprints with references to published papers"*

**Status:** DONE (12-Sep-2026) — checklist decisions applied to `bibliography.bib` /
`paper.tex`. Progress log: `docs/agent/preprint_checklist_progress.json`.

#### Applied replacements

| Bib key | Action taken |
|---|---|
| `carrion2021blending` | arXiv → AAAI 2023 (`@inproceedings`, DOI `10.1609/aaai.v37i13.26835`, pp. 15476–15484; title “…via virtual bids”) |
| `dudik2011doubly` | arXiv → ICML 2011 Omnipress (`@inproceedings`, pp. 1097–1104, ICML PDF URL) |
| `dulac2019challenges` | Retargeted all cites → `dulac2021challenges`; added Springer DOI; removed 2019 arXiv entry |
| `ie2019reinforcement` | Retargeted cites → `ie2019slateq`; polished IJCAI entry + DOI; removed arXiv entry |
| `kang2018sasrec` | IEEE Xplore URL; consolidated duplicate `Kang2018` (also R2-REF3) |
| `mazoure2021improving` | arXiv → ECML PKDD 2022 (`@inproceedings`, MSR publication URL) |
| `zhao2024survey` | arXiv → IJECE 16(3) 2026 (DOI `10.11591/ijece.v16i3.pp1518-1530`; authors + Yuan/Dang) |
| `zhou2016latent` | arXiv → IJCAI 2016 (pp. 3646–3653, official proceedings PDF) |
| `mcdonald2023spotify` | Blog cites → existing KDD 2023 `mcdonald2023impatient` + DOI; removed blog entry |
| `wikipedia-cpm` | Handled under R2-REF5 |

#### Kept as arXiv / tech report (with optional institutional URLs)

| Bib key | Why kept | URL polish |
|---|---|---|
| `gauci2018horizon` | No archival proceedings (ICML 2019 RL4RealLife workshop only) | Meta Research landing page |
| `ie2019recsim` | Google Research tech report; RecSim NG is a different paper | Google Research pubs page; `{RecSim}` casing |
| `lambert2023entangled` | Still arXiv | Title corrected to current arXiv title (dropped “Entangled preferences:”) |
| `kuleshov2014algorithms`, `levine2020offline`, `liu2022monolith`, `lu2016partially`, `naumov2019deep`, `schulman2017proximal` | No better archival venue found / canonical arXiv | unchanged |
| `nielsen2017advertising` | Industry web (not a preprint); already had correct URL | left as-is |

---

### R2-REF3 — Duplicate Kang & McAuley 2018 (AE)

**Status:** DONE (12-Sep-2026). Kept `kang2018sasrec`; retargeted `\cite{Kang2018}`;
removed duplicate bib entry; IEEE Xplore URL.

---

### R2-REF4 — Numbered references (AE)

**Current:** `\citestyle{acmauthoryear}` in `paper.tex` line 8.

**Plan:** Switch to `\citestyle{acmnumeric}` (or ACM numeric equivalent under `acmart`). Recompile and fix any prose that depends on author-year narrative ("as shown by Smith et al. (2019)") that becomes awkward with numbers.

**Risk:** medium (global style change; many narrative citations may need light rephrasing).

**Approval needed before style switch.** Confirm with user whether they want numeric style despite prior author-year drafting.

---

### R2-REF5 — Replace Wikipedia CPM (AE)

**Status:** DONE (12-Sep-2026). History paragraph cite `\cite{wikipedia-cpm}` →
`\cite{hu2004performance}` (performance-based pricing / CPM→CPC→CPA literature
already used in the same paragraph). Removed `wikipedia-cpm` bib entry.

---

### R2-COVER — Cover letter / response to reviewers

**Status:** DRAFT updated (12-Sep-2026) for completed reference-polish items
(R2-REF1/2/3/5). Remaining not-so-minor and R1 items still Planned until edited.

---

## Draft response to reviewers (Round 2)

Working draft for the resubmission cover letter / response document.
Bracketed notes are reminders for us; strip them before sending.
Update each bullet from *Planned* → *Done* only after the edit lands in
`paper.tex` / `bibliography.bib`.

```text
Dear Associate Editor and Reviewer,

Thank you for the minor-revision decision and for the careful reference
and accuracy checks. We address each point below. Section references
refer to the revised manuscript.

----------------------------------------------------------------
Associate Editor — minor points
----------------------------------------------------------------

1. Reference title casing
   Done. We audited cited bibliography titles and converted them to
   consistent sentence case (preserving proper nouns and acronyms),
   matching the majority style already present in the bibliography.

2. Preprints replaced with published versions where available
   Done. We systematically checked arXiv / preprint / weak-source
   citations against published venues (publisher pages, Crossref,
   IEEE Xplore, ACM DL, IJCAI proceedings, and institutional pages).
   Where a peer-reviewed archival version exists, we updated the
   bibliography entry and retargeted in-text citations when a better
   key already existed. Applied updates include:
   - Carrion et al. → AAAI 2023 (DOI 10.1609/aaai.v37i13.26835)
   - Dudík et al. → ICML 2011 proceedings (Omnipress; official PDF URL)
   - Mazoure et al. → ECML-PKDD 2022 (Microsoft Research publication URL)
   - Dulac-Arnold et al. challenges paper → Machine Learning 2021
     (consolidated on the published key; Springer DOI added)
   - Ie et al. SlateQ-related cites → IJCAI 2019 SlateQ paper
     (DOI 10.24963/ijcai.2019/360); removed the parallel arXiv key
   - Zhou & Brunskill latent contextual bandits → IJCAI 2016
   - Zhao & Liu retrieval survey → IJECE 16(3), 2026
     (DOI 10.11591/ijece.v16i3.pp1518-1530)
   - Spotify blog “Optimizing for the long-term…” → KDD 2023
     Impatient Bandits paper (DOI 10.1145/3580305.3599410)
   - Kang & McAuley SASRec → ICDM 2018 IEEE record
     (DOI 10.1109/ICDM.2018.00035; IEEE Xplore URL)

   A small number of citations remain as arXiv / technical reports
   because no archival journal or conference proceedings version
   exists. In particular:
   - Gauci et al., Horizon (arXiv:1811.00260): appeared only at the
     ICML 2019 RL4RealLife workshop, which had no formal proceedings.
     We retain the arXiv record and point the bibliography URL to
     Meta Research’s publication page for the same work.
   - Ie et al., RecSim (arXiv:1909.04847): remains a Google Research /
     arXiv tech report; the later RecSys 2020 RecSim NG demo is a
     different follow-on system, so we do not substitute it. We point
     the bibliography URL to the Google Research publication page.
   - Other retained arXiv citations are canonical industrial tech
     reports or widely cited algorithmic preprints without a later
     archival rewrite (e.g., PPO, Levine et al. offline RL survey,
     DLRM, Monolith). We also corrected the Lambert et al. title to
     match the current arXiv listing. We are happy to adjust any
     specific remaining entry if the Editorial Office prefers an
     alternate citation format.

3. Duplicate Kang & McAuley (2018)
   Done. Consolidated to a single ICDM 2018 bibliography entry
   (`kang2018sasrec`) and retargeted the duplicate in-text cite.

4. Numbered references
   [Planned:] Not yet applied; awaiting confirmation whether to switch
   from author–year to numbered citation style for this revision.

5. Wikipedia CPM citation
   Done. Replaced the Wikipedia “Cost per mille” citation with Hu
   (2004) on performance-based pricing models in online advertising,
   which discusses CPM alongside the shift to CPC/CPA and was already
   used in the same historical paragraph.

----------------------------------------------------------------
Associate Editor — not-so-minor points
----------------------------------------------------------------

6. Incorrect DOIs and AI disclosure
   [Planned:] DOI audit fixes and Methods-section AI disclosure are
   next; not yet applied in this reference-polish pass.

7–11. Claim–citation alignment, off-policy / SL wording, Section 3
   historical framing, and Table utility (Zhao 2020; LinkedIn / Yan 2020)
   [Planned:] …

----------------------------------------------------------------
Reviewer 1
----------------------------------------------------------------

12. Section 4.4 state-space taxonomy (Markovianity vs Expressiveness;
    SlateQ vs PinnerFormer)
    [Planned:] …

We hope these revisions fully address the remaining concerns.

Sincerely,
The authors
```

**Horizon paragraph (standalone):**

```text
Regarding Gauci et al. (Horizon): after checking Google Scholar and venue
records, we found no archival journal or conference proceedings version of
this paper. It was presented at the ICML 2019 RL4RealLife workshop, which
did not publish formal proceedings. We therefore retain the arXiv preprint
(arXiv:1811.00260) as the canonical citable version and point readers to
Meta Research’s publication page for the same work.
```

---

## Suggested session workflow (one-by-one)

1. Approve **R2-AI1** disclosure wording → apply.
2. Approve **R2-DOI1** table of DOI fixes → apply to `bibliography.bib`.
3. Approve intro claim softens (**R2-ABBR1**, **R2-CITE3**, **R2-CITE2**, **R2-CITE1**) as a short Intro batch (or one sentence at a time if preferred).
4. Approve **R2-TAB1** + **R2-TAB2** together (same table).
5. Approve **R2-HIST1** after locating the remaining "next step" sentence.
6. Approve **R2-STATE1** rewrite (largest prose/table rewrite).
7. Approve bibliography polish (**R2-REF3**, **R2-REF5**, then **R2-REF1**, **R2-REF2**).
8. Approve **R2-REF4** numeric citation switch (last style change before compile).
9. Compile via README timestamped workflow; spot-check PDF.
10. Draft **R2-COVER**; user review; then commit/push only when asked.

---

## Investigation artifacts already created (non-manuscript)

| Path | Purpose |
|---|---|
| `docs/agent/reviewers_round2.txt` | Full round-2 decision letter |
| `docs/agent/round2_revision_plan.md` | This plan |
| `scripts/audit_dois.py` | Crossref DOI mismatch checker |
| `/tmp/doi_audit_output.txt` (if still present) | Last audit run output |

**Not yet done (intentionally):** edits to `paper.tex`, `bibliography.bib`, `paper_audit_master.md` section scores, or cover letter body.

---

## Sync with existing audits

When an item is approved and applied, update the matching section audit and add a short note to `docs/agent/paper_audit_master.md`:

| Round-2 ID | Primary audit file |
|---|---|
| R2-AI1 | `methodology_audit.md` |
| R2-CITE1–3, R2-ABBR1 | `introduction_audit.md` |
| R2-HIST1, R2-REF5 | `history_audit.md` |
| R2-TAB1–2 | `reward_design_citation_audit.md` |
| R2-STATE1 | `state_space_citation_audit.md` |
| R2-DOI1, R2-REF1–4 | new short `bibliography_audit.md` (create when first bib edit is approved) |
| Global status | `paper_audit_master.md` (add a Round-2 dashboard section when work starts) |

---

## Out of scope unless user asks

- Reopening round-1 Tier 1 items that R1/AE did not re-raise (e.g., Section 4.5 exploration reframing), except where they collide with new AE claims.
- Broad rewrite of non-flagged sections.
- Committing or pushing without an explicit user request.
