# Introduction: Revision And Reviewer-Risk Audit

Scope: `paper.tex`, `\section{Introduction}` (currently lines 91-121).

Latest refresh: 12-Sep-2026 — R2-ABBR1: expanded SL and RL at first Introduction use (MDP already defined). Round-1 May 17 pass (I1–I6) remains the baseline for other Intro items.

## Round-2 resolved

- **R2-ABBR1 (DONE).** AE: *"Make sure all abbreviations are properly introduced, including SL in the introduction."* First Intro uses are now `supervised learning (SL)` and `Reinforcement learning (RL)`; `Markov Decision Process (MDP)` was already expanded. Intro acronym sweep found only these three short forms.

- **Paper-wide acronym first-use pass (DONE, 12-Sep-2026).** Expanded acronyms that previously appeared before definition, including abstract MDP; table CPM/CPC/CPA and supervised ML; notation-table UCB; CTR/pCTR table wording; DIN, SASRec, AUC, LinUCB, RegCB, NDCG, KPI; and evaluation-table HDQN, AC, GGI, DDPG. Left proper algorithm names (e.g., REINFORCE, UCB1) and later repeat uses abbreviated after first expansion.

## Reviewer context used

- Associate Editor: highlight the introductory/tutorial nature of the work targeted at industry practitioners; give clear problem definitions early; distinguish ad-related aspects from general recommender techniques; avoid repetitive material; use bold sparingly.
- Reviewer 1: lack of depth in core content; overemphasis on pedagogical material (Frozen Lake flagged explicitly); evaluation underdeveloped; terminology defined when introduced; reference alignment concerns (including `danescu2010competing` flagged as supporting a different claim than the one it is attached to); limited discussion of joint optimization; reward design / long-term metrics need more concrete grounding.
- Reviewer 2: insufficient emphasis on ad-policies; tighter RL methods coverage; statements about RL adaptability not sufficiently backed by literature; cited works often general RL rather than ad-specific; repeated information across sections; structure and writing need improvement.

## Current Overall Assessment

The introduction is now substantially stronger after the May 17 revision passes (initial pass + I1-I6 resolutions). It now:

- frames the problem and its stakes in a single merged opener paragraph (formerly two single-sentence paragraphs),
- anchors the joint monetization and engagement claim with `zhao2020jointly` only (the reviewer-flagged `danescu2010competing` mismatch has been removed),
- separates three structural difficulties (cannibalization, horizon-observability mismatch, endogeneity) with sharp non-overlap,
- distinguishes the SL paradigm's contribution (paragraph 4) from its structural limitations (paragraph 5),
- positions RL as a complement to SL rather than a substitute, with specific mechanisms named (MDP formalism, off-policy estimators),
- anchors the over-monetization cautionary example with the on-claim industrial source `sagtani2024ad`,
- uses softened, evidence-anchored vocabulary throughout (`non-trivial` instead of `critical`; removed the absolute *"essential ... without compromising"* summary),
- expands the contribution paragraph from a single sentence into a proper three-sentence block with practitioner framing,
- aligns the "unifying taxonomy" terminology across abstract, gap paragraph, and contributions paragraph,
- removes the FrozenLake preview sentence that Reviewer 1 explicitly flagged.

Estimated reviewer-aligned score: **9.5 / 10**, up from 9.25 / 10 after I7 was reclassified as not-an-issue (P7 is structurally sound as a single unified "challenges" paragraph with explicit *"First / Second / Furthermore"* signposts), and up from 8.5 / 10 before the I1-I6 resolution pass and from roughly 7 / 10 at the start of this revision cycle. The remaining gap to 10 is held entirely by minor phrasing polish (I8, I9) and bibliography hygiene (I10, I11) — none of which would by themselves prompt reviewer pushback.

The main remaining risks are:

- One awkward phrasing ("framework in recommendation systems") in paragraph 6.
- Minor: "real-time" used adverbially where "in real time" is the standard convention.
- Possible bibliography duplication: both `dulac2019challenges` and `dulac2021challenges` are cited in this section.

## Legend

Priority and status are color-coded using inline HTML. Colors render in Cursor / VS Code markdown preview and most rich markdown viewers; on GitHub the text labels remain readable even if colors are stripped.

**Priority:**
<span style="background:#7c1d1d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P0</span> critical / cannot ship
&nbsp;
<span style="background:#dc3545;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P1</span> blocker / must-fix
&nbsp;
<span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> should-fix
&nbsp;
<span style="background:#6c757d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P3</span> nice-to-have

**Status:**
<span style="background:#6c757d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">TODO</span> not started
&nbsp;
<span style="background:#0d6efd;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">IN PROGRESS</span> being edited
&nbsp;
<span style="background:#ffc107;color:black;padding:2px 8px;border-radius:4px;font-weight:bold">PENDING REVIEW</span> awaiting user sign-off
&nbsp;
<span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> applied and committed

## Pending Revision Items

### Phrasing fixes

- <span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> <span style="background:#6c757d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">TODO</span> **I8.** P6 (line 109): *"RL provides a framework in recommendation systems to solve the two problems above"* reads awkwardly. Cleaner: *"RL provides a framework for addressing the two problems above in recommendation systems"* or simply *"RL addresses the two problems above"*.
- <span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> <span style="background:#6c757d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">TODO</span> **I9.** P7 (line 112): *"updated in real-time during user interactions"*. When used adverbially, the unhyphenated *"in real time"* is the standard convention; the hyphenated form is reserved for compound adjectives.

### Bibliography hygiene

- <span style="background:#6c757d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P3</span> <span style="background:#6c757d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">TODO</span> **I10.** Confirm whether `dulac2019challenges` and `dulac2021challenges` are distinct works that both deserve citation, or whether one supersedes the other. Both appear in the intro: dulac2021 at P7 opener (line 112), dulac2019 at P6 (line 109) and P7 interpretability claim (line 112). If both are legitimately distinct, ensure the choice is consistent across the paper.

### Optional citation-density observation

- <span style="background:#6c757d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P3</span> <span style="background:#6c757d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">TODO</span> **I11.** `afsar2022reinforcement` is cited three times in the introduction (P6 framework anchor, P7 dynamic-programming claim, P8 previous-surveys claim). Each use is for a distinct claim, so this is defensible under the citation-audit "distinct facet" rule, but worth flagging as the most-cited source in the introduction.

## Citation Adequacy Scores

Scores use a 1-10 scale:

- 9-10: directly supports the attached claim and is well placed.
- 7-8: mostly appropriate but broad, indirect, or supporting only part of the sentence.
- 5-6: plausible but weakly aligned or too general for the attached claim.
- 1-4: likely mismatched and should be removed or replaced.

| Citation | Uses | Where Used | Adequacy | Assessment |
|---|---:|---|---:|---|
| `zhao2020jointly` | 1 | P1, joint ad+organic framing | 9 | Direct fit (paper titled "Jointly Learning to Recommend and Advertise"). Anchors the joint-optimization framing the intro builds on. Sole anchor on the opening sentence after I1 resolution. |
| `sagtani2023quantifying` | 2 | P2 ad-fatigue/churn; P3 cannibalization | 9 | Strong ad-policy / industrial source. Distinct claims across the two uses, so the repetition is defensible. |
| `silberstein2023combating` | 1 | P2 ad fatigue | 9 | Direct fit on ad fatigue. |
| `yan2020ads` | 1 | P3 cannibalization | 9 | Strong industrial source on monetization-engagement trade-off (LinkedIn). |
| `hohnhold2015focusing` | 1 | P3 horizon-observability mismatch | 9 | Canonical long-horizon A/B testing source (Google). Direct fit. |
| `wang2022surrogate` | 1 | P3 horizon-observability mismatch | 9 | Direct fit on surrogate metrics for long-term outcomes. |
| `mcdonald2023spotify` | 1 | P3 horizon-observability mismatch | 8 | Strong industrial long-term value source (Spotify). Slightly broader than the specific claim, but appropriate. |
| `zou2019reinforcement` | 1 | P3 endogeneity / feedback | 9 | Direct fit on policy-induced effects in recommender RL. |
| `ie2019reinforcement` | 1 | P3 endogeneity / feedback | 8 | Strong fit (RecSim, simulating policy-induced dynamics). Slightly broader than the specific endogeneity claim but appropriate. |
| `mcmahan2013ad` | 2 | P4 SL paradigm anchor; P4 CTR-specific claim | 9 | Strong industrial CTR source. Per-clause anchoring after recent revision; both uses are distinct. |
| `covington2016deep` | 1 | P4 SL paradigm anchor (YouTube DNN) | 9 | Foundational industrial DL recsys paper. |
| `cheng2016wide` | 2 | P4 SL paradigm anchor; P4 engagement-specific claim | 9 | Strong industrial DL recsys (Wide & Deep, Google Play). Both uses are distinct after recent revision. |
| `yi2014beyond` | 1 | P4 dwell-time signal | 9 | Direct fit on the dwell-time signal mention. |
| `naumov2019deep` | 1 | P4 industrial backbone claim | 9 | Meta DLRM. Strong industrial-backbone anchor for the closing sentence of P4. |
| `swaminathan2015counterfactual` | 2 | P5 distribution shift; P6 off-policy estimators | 9 | Direct fit on both counterfactual evaluation and policy-induced distribution shift. Distinct claims across the two uses. |
| `dudik2011doubly` | 1 | P5 distribution shift | 9 | Doubly robust estimators. Strong canonical fit. |
| `agarwal2016statistical` | 1 | P5 outcomes are policy-dependent | 9 | Microsoft Decision Service. Strong fit for policy-dependent outcomes claim. |
| `afsar2022reinforcement` | 3 | P6 RL framework; P7 dynamic-programming infeasibility; P8 previous surveys | 8 | Strong RL recsys survey. All three uses are for distinct claims, but this is the most-cited source in the intro. Monitor. See I11. |
| `Sutton1998` | 1 | P6 MDP formalism | 9 | Foundational. Single use after recent citation cleanup. |
| `chen2022off` | 1 | P6 SL+RL embedding | 9 | Direct ad/recsys example of supervised function approximation embedded in off-policy actor-critic. |
| `dulac2019challenges` | 2 | P6 deep+RL machinery; P7 explainable RL interpretability | 7 | Defensible but broad. Each use is distinct. See I10 about possible duplication with `dulac2021challenges`. |
| `levine2020offline` | 1 | P6 deep+RL machinery | 9 | Offline RL tutorial. Strong fit. |
| `dulac2021challenges` | 1 | P7 RL real-world complexity | 8 | Updated journal version. Strong fit for the broad implementation-complexity claim. See I10 for the consistency concern with `dulac2019challenges`. |
| `zhu2021overview` | 1 | P7 infinite state/action spaces | 7 | Broad RL overview. Acceptable for the infinite-spaces claim, but a more recsys-specific source would strengthen it. |
| `everitt2021reward` | 1 | P7 reward function importance | 8 | Reward hacking / reward design source. Good fit for the broad reward-design importance claim. |
| `wu2017returning` | 1 | P7 clickbait/CTR pitfall | 8 | Recommender system source on returning users / CTR optimization pitfalls. Good fit for the clickbait example. |
| `sagtani2024ad` | 1 | P7 over-monetization / excessive ad load | 9 | Direct fit. Industrial ad-load balancing paper (Spotify, WSDM 2024) whose entire motivation is the exact reward-design trade-off the sentence describes. Added during I2 resolution; not used elsewhere in the intro. |
| `glanois2024survey` | 1 | P7 explainable RL | 8 | Explainable RL survey. Strong fit for the interpretability claim, paired appropriately with other explainability sources. |
| `vouros2022explainable` | 1 | P7 explainable RL | 8 | Same family as `glanois2024survey`. Both citations together substantiate the explainability claim across distinct angles (general survey + specifically explainable RL). |
| `lambert2023entangled` | 1 | P7 non-compliant / unethical behavior | 8 | Reward hacking / unintended-behavior source. Good fit for the hedged "extreme cases" claim. |
| `lin2023survey` | 1 | P8 previous surveys | 9 | Direct fit (RL recommender systems survey). Used alongside `afsar2022reinforcement` to establish the "previous surveys exist" claim. |

**Citation tally**

- Unique citations in the introduction: 31.
- Total citation tokens: 36.
- Re-cited sources: `afsar2022reinforcement` (3), and `sagtani2023quantifying`, `mcmahan2013ad`, `cheng2016wide`, `swaminathan2015counterfactual`, `dulac2019challenges` (2 each).
- All multi-use citations are currently attached to distinct claims (per the §7.1 "distinct facet" rule), so the repetition is defensible — but `afsar2022reinforcement` at 3 uses is at the upper bound and worth monitoring.

## Resolved Revision Items

Status assessed against the current introduction on May 17, 2026.

- <span style="background:#7c1d1d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P0</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **I1.** Removed `danescu2010competing` from paragraph 1 (line 91), leaving `zhao2020jointly` as the sole on-claim anchor for the joint monetization and engagement framing. The Danescu et al. paper studies organic vs sponsored search results in 2010-era search engines, which Reviewer 1 flagged as misaligned with the attached claim about modern feed recommenders. In the same pass, the platform-name list (Instagram, TikTok, Pinterest) was replaced with the generic phrase *"Large-scale content recommendation platforms in industry"*, since the named platforms were not all grounded by other citations in the paper (Pinterest in particular had no supporting citations elsewhere).
- <span style="background:#7c1d1d;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P0</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **I2.** Anchored the previously uncited over-monetization claim in paragraph 7 (line 109) with `sagtani2024ad`, the Spotify ad-load balancing paper (WSDM 2024). The paper directly studies the reward-design trade-off the sentence describes — naive revenue maximization in the learning objective leads to bad ad-load outcomes that degrade user engagement. Single anchor chosen for parallelism with `wu2017returning` in the preceding sentence; no redundancy introduced (first use of `sagtani2024ad` in the intro).
- <span style="background:#dc3545;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P1</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **I3.** Replaced *"designing appropriate reward functions is critical"* with *"designing appropriate reward functions is non-trivial"* at paragraph 7 (line 109). Removes the extreme adjective flagged by `revision_rules.md` §1; the trailing *"as poorly chosen reward functions can lead to..."* clause continues to carry the empirical grounding via `everitt2021reward`. The new adjective aligns with vocabulary used elsewhere in the introduction (P3 *"structurally difficult"*, P5 *"structurally insufficient"*).
- <span style="background:#dc3545;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P1</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **I4.** Removed the summary sentence *"Striking the right balance in reward function design is essential to achieve both user engagement and monetization objectives without compromising the platform's long-term goals"* from paragraph 7 (line 109). The sentence was redundant with the two contrasting examples that preceded it (clickbait extreme via `wu2017returning`, over-monetization extreme via `sagtani2024ad`), which already convey "balance matters" by demonstration. Removal eliminates both the extreme word *"essential"* and the absolute *"without compromising"* clause in one stroke, partially advances I7 (paragraph length), and leaves *"Furthermore, interpretability is a major challenge in RL deployment"* as a clean transition.
- <span style="background:#dc3545;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P1</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **I5 + I6.** Merged the two single-sentence opening paragraphs (former P1 at line 91 and former P2 at line 94) into a single problem-and-stakes paragraph by removing the blank line between them. The source-level section comments (`%What is the problem`, `% What happens if problem isn't solved`) are preserved as inline structural notes; in LaTeX comments do not break paragraphs, so the rendered output is now one paragraph. The merged paragraph leads naturally into the *"Jointly optimizing revenue and long-term engagement is structurally difficult..."* paragraph that follows.
- <span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **I7.** Reclassified as not-an-issue. P7 is conceptually unified ("implementing RL in real-world, large-scale platforms remains complex") and the "First / Second / Furthermore" inline enumeration already provides explicit navigation. Splitting into three paragraphs would either lose the unifying topic sentence or require redundant framing sentences at the top of each new paragraph, working against the broader revision cycle's effort to trim editorializing prose. Reviewer feedback never targeted this paragraph for length; the §4 single-sentence-paragraph rule (which I5/I6 addressed) does not extend to long-but-structured paragraphs with clear internal signposts. Keeping the paragraph as-is.
- <span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **R1.** Three-difficulties paragraph (P3, line 100) refactored from three vague difficulties to three sharply non-overlapping points (cannibalization, horizon-observability mismatch, endogeneity). Endogeneity term introduced with inline gloss.
- <span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **R2.** SL paradigm paragraph (P4, line 103): trimmed repeated citations (`covington2016deep` 3 to 1, `cheng2016wide` 3 to 1), softened "supervised deep learning" to "supervised machine learning" so `mcmahan2013ad` (FTRL/LR) is no longer mis-shelved, split per-clause anchor in S3, added `naumov2019deep` for industrial-backbone claim.
- <span style="background:#dc3545;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P1</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **R3.** SL-limitations closing sentence (P5, line 106) rewritten from ambiguous "Long-term outcomes are not fixed labels but functions of the policy" to clear "Long-term outcomes therefore depend not only on the current state-action pair but also on the policy that generates the subsequent trajectory."
- <span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **R4.** RL-as-solution paragraph (P6, line 109): S2 "addresses" softened to "explicitly represents... providing the framework within which RL algorithms can account for this dependence"; S3 rewritten to actually address counterfactual evaluation via off-policy estimators (now parallels SL "Second" critique); S4 SL+RL framing changed from "rather than replacing" with `chen2022off` as the load-bearing recsys anchor; citation cleanup (9 tokens to 6, each cite appearing once).
- <span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **R5.** Gap paragraph opener (P8, line 115) updated to name the MDP elements and policy learning as the unifying taxonomy axes, replacing "through the lens of" framing.
- <span style="background:#dc3545;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P1</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **R6.** Contributions paragraph (P9, line 118) expanded from a single sentence into a three-sentence block: taxonomy + 150 works (with grammar fix "a component-level taxonomy"), synthesis dimensions, practitioner audience.
- <span style="background:#fd7e14;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">P2</span> <span style="background:#198754;color:white;padding:2px 8px;border-radius:4px;font-weight:bold">DONE</span> **R7.** FrozenLake preview sentence removed from structure paragraph (P10, line 121) per Reviewer 1's explicit feedback. Subsequent methodology and Section 4 opener work removed the remaining FrozenLake table/source content from the rendered paper and replaced the early table with a compact RL-notation guide.

## Out of scope for this file

- Citation audits for body sections live in `reward_design_citation_audit.md`, `state_space_citation_audit.md`, and `policy_learning_citation_audit.md`.
- Abstract revisions live in `abstract_revision_todo.md`.
- Document-wide revision conventions live in `revision_rules.md`.
- Methodology Table 1 and the Section 4 opener are out of scope for this introduction audit; their current state is tracked in `methodology_audit.md` and `rl_formulation_opener_audit.md`.

## Working rules

- Apply changes one at a time, with explicit approval per item, consistent with the repo workflow.
- Preserve `paper.tex` paragraph style. Do not reflow existing paragraphs in the source unless the change explicitly says so.
- When proposing replacement text in chat, wrap suggestions in fenced `latex` blocks with short physical line widths, per `format-suggested-sentences.mdc`.
- When updating an item's status, swap the colored status badge in place (TODO -> IN PROGRESS -> PENDING REVIEW -> DONE).
- When an item is resolved, move it from Pending to Resolved with a one-line summary of how it was resolved.
- Apply the §7.1 citation audit checks (no redundancy, no orphans, claim-citation alignment) to every change.
