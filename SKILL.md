# Writing Skill: RL for Monetization-Aware Recommendation Systems (Review Paper)

**Agent instruction:** On **every** response while editing this project (the review paper at `/home/aordorica/Review-Paper-RL-Ad-Rec-Systems`), start the response with a 🏫 emoji. This is a non-optional signal that the project-specific skill is loaded and that every rule below (including the pedagogical-overemphasis guard) is being actively applied. If the emoji is missing, this file is not being consulted. This instruction applies to this project only and does not affect any other work.

## Paper Overview

This is a review paper titled *"A Review of Reinforcement Learning Applications for Monetization-Aware Content Ranking in Large-Scale Recommendation Systems"*, authored by Armando Ordorica and Yuri Lawryshyn at the University of Toronto. It targets ACM Transactions on Recommender Systems (ACM TORS).

The paper synthesizes RL methodologies for jointly optimizing ads and organic content, organized by MDP components: state, action, reward, and policy. It reviews 153 academic and industrial works.

## Paper Structure

1. **Introduction**: problem motivation, SL limitations, RL promise, gap in literature, contributions
2. **Paper Collection Methodology**: how 153 papers were sourced and ranked
3. **A Brief History**: rule-based to deep learning, three evolutionary tracks (pricing/objectives, representation, sequential horizon)
4. **The RL Formulation**: core section organized by MDP components
   - Reward Design (proxy metrics for revenue, engagement, fatigue; utility functions; structural challenges of blending ad and organic rewards)
   - Action Space Representation
   - State Space Representation
   - Policy Learning (offline vs online, value-based vs policy-based)
   - Exploration vs Exploitation (epsilon-greedy, UCB, Thompson Sampling)
5. **Conclusions**

## Authorial Contributions (Framing)

The paper's abstract positions the work as introducing a "component-level taxonomy that clarifies how existing systems operationalize state, action, reward, and policy." Several specific artifacts in the paper are synthesized by the authors across multiple systems rather than inherited from any single paper, and they should be framed explicitly as contributions. When editing, make it unambiguous that these are authorial syntheses (per the "Separate prior work from your own contribution" rule):

- **Three evolutionary tracks** (pricing/objectives, representation, sequential horizon) in the Brief History section.
- **Structural properties of the action space**: expressiveness, orthogonality, interpretability, consistency. Synthesized from recurring design considerations across industrial and academic systems.
- **Structural properties of the state space** (to be developed consistently with the action-space framing).
- **Proxy-metric taxonomies** for revenue, engagement, and fatigue in the Reward Design subsection.
- **Comparison tables** (e.g., `tab:utility-comparison`, `tab:action-space-comparison`) that map published systems onto these taxonomies and make the trade-offs each system accepts explicit.

When introducing any of these artifacts, signal authorial synthesis with phrasing such as "We introduce...", "This taxonomy is synthesized from...", or "We use this framework to compare...". Avoid phrasing that implies the taxonomy was lifted from a single cited source unless that is literally the case.

---

## Revision Context: Reviewer Feedback

The paper received reviews from two ACM TORS reviewers (Reviewer 1: Reject, Reviewer 2: Major Revision) and an Associate Editor. The following summarizes the actionable feedback, organized by priority.

### High Priority (both reviewers and AE agree)

1. **Strengthen the ad-specific focus.** The majority of the paper reads as a general study on RL and recommender systems. Emphasis on ad policies, joint optimization of ads and organic content, and the specific challenges of monetization-aware ranking is insufficient. Every section should clearly connect back to the core topic.
2. **Add depth and critical analysis.** The paper mentions techniques and papers without sufficient explanation or critical evaluation. Industrial deployments (YouTube, Meta, Pinterest) are referenced but under-explored. Provide detailed comparisons of methods, highlighting trade-offs, assumptions, and real-world performance. Do not just list approaches; evaluate them.
3. **Add evaluation coverage.** There is no systematic review of how evaluation is done in practice. Add coverage of common metrics, simulator-based testing (e.g., RecSim), counterfactual estimators, and quantitative results from cited studies. Summarize reported KPIs and outcomes from real-world deployments.
4. **Reduce pedagogical/tangential material.** The evolution from RNNs to Transformers, general embedding explanations, and the Frozen Lake example do not contribute enough to the core topic. Replace generic pedagogical examples with domain-specific illustrations tied directly to ads and recommendations (e.g., simplified bandit-based ad selection).
5. **Eliminate repetition.** There is repeated information across sections. Each point should appear once, in the most appropriate location.

### Medium Priority

6. **Define terms when first introduced.** "Displacement cost" and other technical terms appear before definition. All terms must be defined at first use.
7. **Fix table/figure labeling.** Tables 3-4 are referenced but do not exist; Figures 3-4 appear to be tables. Ensure consistent and correct labeling throughout.
8. **Consolidate the RL formulation.** Add a dedicated subsection introducing the RL task (MDP formulation, notation) before splitting into component subsections. Include a notation table.
9. **Verify reference accuracy.** Some citations are misaligned with the claims they support. Review every citation to ensure it directly supports the specific claim made.
10. **Back claims with ad-specific literature.** Several statements about RL adaptability for recommenders cite general RL research rather than ad-policy-specific or recommender-specific work.

### Presentation Fixes

11. **No references in the abstract.**
12. **Use bold-face text sparingly.**
13. **Ensure all figure text is readable.** Notes under figures should use footnotes or be included in the figure caption.
14. **Position tables near where they are first referenced**, not at the end of the paper.
15. **Fix the acknowledgment section.** The current wording (thanking the second author for guidance) is uncommon for a co-authored paper.

### Reviewer-Identified Strengths to Preserve

- The focus on balancing advertising vs. organic content is timely and important to industry practitioners.
- The paper collection methodology and selection criteria for 153 papers are strong.
- The RL concepts are explained well and connected to the recommendation task.
- The topic has excellent relevance to TORS and real-world significance.

---

## Document Structure and Reader Guidance

### Lead the reader at every stage
- Organize material so the reader always knows what is coming next.
- Each section (except the first) should begin with a short introductory paragraph explaining what the section covers, how it is organized, and sometimes why that organization was chosen.
- Each section (except the first and last) should end with a summary.
- Each section should transition naturally into the next.
- Tell the reader why each part of the analysis is being presented.

### Make the "so what" explicit
- Every major point must explain why it matters.
- End each literature review subsection with a clear takeaway tied to the paper's core question (jointly optimizing ads and organic content).
- Do not present information without connecting it to the paper's contribution.

### Separate prior work from your own contribution
- Make it unambiguous what comes from the literature and what is the paper's own synthesis, taxonomy, or analysis.
- Use citations to distinguish external ideas, results, and methods from original contribution.
- Referencing adds credibility; use it liberally where appropriate.

### Avoid pedagogical overemphasis

Reviewer 1 explicitly flagged "Overemphasis on Pedagogical Material" as a top reason to reject. Reviewer 2 echoed it. Apply this as a per-edit check, not just an aspirational guideline.

**What counts as pedagogical overemphasis:**
- Textbook-style explanations of standard RL concepts (Bellman backups, policy-gradient machinery, formal MDP derivations) beyond what is strictly needed for the ad-policy argument the paragraph is making.
- Historical lineages of techniques (RNNs -> Transformers, CF -> MF -> neural -> two-tower) unless the lineage is itself the object of analysis.
- Generic illustrative examples (FrozenLake, grid worlds, cartpole, thumbs-up / thumbs-down YouTube signals) when the same point can be made with an ad or organic-content example.
- Definitions of terms that are already defined in the referenced textbook and that the review paper is not advancing or critiquing.

**Positive rule.** Every paragraph should earn its space against this check: *Does this sentence advance the paper's argument about jointly optimizing ads and organic content, or does it explain RL?* If the answer is "explain RL", cut or compress it and cite a textbook instead.

**Before inserting or retaining a sentence, ask:**
1. Is the claim ad-recsys-specific, or could it appear unchanged in a generic RL tutorial?
2. Is the example from the ad / organic-content / recsys domain?
3. Does the citation support an ad-policy claim rather than a generic RL claim?
4. If this sentence is cut, does the paragraph still make its point?

If the answer to any of (1)-(3) is "no", rewrite to anchor the sentence in the domain. If (4) is "yes", cut.

**Reviewer-cited examples of what to avoid:** FrozenLake, the RNN -> Transformer evolution narrative, generic embedding lineage, thumbs-up/down YouTube surveys, and any formal definition of Markovianity / Bellman updates / policy gradient that is not directly in service of an ad-recsys claim.

---

## Academic Rigor

### Support claims with references
- Back up nearly every nontrivial claim with a citation.
- Avoid unsupported assertions.
- Prefer paraphrasing with citation over direct quotation.
- Use quotations only sparingly.

### Use the literature review correctly
- Do not explain standard methods or common metrics in textbook style.
- Review literature that addressed the same or closely related problem.
- Use prior studies to justify methodological choices rather than explaining basic methods at length.
- If a standard method must be mentioned, cite a textbook or source rather than explaining the method in detail.

### Handle equations and variables rigorously
- All variables mentioned in text must appear in math mode.
- Define every variable the first time it is introduced.
- Where relevant, define domains or ranges.
- Do not use the same symbol for different concepts.
- Do not use multiple symbols for the same concept.
- Avoid redefining variables repeatedly; if needed later, explicitly remind the reader of the prior definition.
- Equations must read as part of the sentence and use proper punctuation.
- Use automatic equation numbering and cross-referencing.

### Handle figures, tables, and appendices properly
- Reference every figure and table in the text before it appears.
- Walk the reader through the figure or table; do not make the reader infer the takeaway alone.
- Put table titles before tables; figure captions after figures.
- Use automatic numbering and cross-referencing for all floats.
- If appendices exist, explicitly direct the reader to the relevant appendix sections from the main text.

---

## LaTeX Conventions

### Document Class and Format
- Document class: `acmsmall` via `acmart` (`\documentclass[acmsmall]{acmart}`)
- Journal: `\acmJournal{CSUR}`
- Citation style: `\citestyle{acmauthoryear}` (author-year inline citations)
- Bibliography: BibTeX with `ACM-Reference-Format` style, entries in `bibliography.bib`

### Build System
- Build with `latexmk` (pdflatex + bibtex, up to 6 passes)
- Timestamped PDFs via `build_timestamped_pdf.sh` for traceability
- Continuous preview via `latexmk -pvc paper.tex`

### Packages in Use
- `booktabs` (professional table rules: `\toprule`, `\midrule`, `\bottomrule`)
- `tabularx` (flexible-width tables)
- `adjustbox` (tables wider than `\textwidth`)
- `graphicx` (figures)
- `enumitem` (list customization)
- `makecell`, `multirow` (complex table cells)
- `setspace` (line spacing adjustments)
- `float` (`[H]` placement)
- `datetime` (build timestamp)

### Labeling Conventions
- Sections: `\label{sec:methodology}`
- Tables: `\label{tab:comparison}`, `\label{tab:evolution-tracks}`
- Figures: `\label{fig:ad_timeline}`
- Equations: `\label{eq:objective_function}`, `\label{eq:ucb}`
- Subsections using snake_case: `\label{state_space_representation}`, `\label{policy_learning}`

### Table Style
- Use `\renewcommand{\arraystretch}{1.15}` for readable row spacing
- Use `\setstretch{1}` inside table environments
- Use `\footnotesize` for table text
- Prefer `tabularx` with `\textwidth` or `\linewidth` for full-width tables
- Use `booktabs` rules, not `\hline`

### Citation Style
- Inline: `\cite{authorYEARkeyword}` producing (Author, Year) format
- BibTeX keys follow `authorYEARkeyword` pattern, e.g., `zhao2020jointly`, `levine2020offline`
- Narrative citation forms in prose:
  - One author: **Smith (2019)**
  - Two authors: **Smith and Jones (2019)**
  - More than two: **Smith et al. (2019)**
- If the citation appears at the end of the sentence, place it in parentheses before the period.
- Be consistent in punctuation and formatting of **et al.**

### Bibliography Title Casing
- Use **sentence case** for article and paper titles in `bibliography.bib` (References section), not Title Case.
- Capitalize the first word, the first word after a colon when it starts a subtitle, proper nouns (Google, Instagram, Meta, Thompson, Yahoo, Overture), system names (SlateQ), and acronyms (PPC, CTR, RL).
- Protect required capitals with BibTeX braces, e.g., `{Thompson}`, `{SlateQ}`, `{PPC}`.
- The paper's own `\title{}` stays mixed / title case; sentence case applies only to cited-work titles.
- `ACM-Reference-Format.bst` preserves `.bib` casing, so enforce consistency in the source entries.

### Emphasis and Bold

Per the ACM TORS Associate Editor's feedback (item 12 in the reviewer checklist above), bold-face text must be used sparingly. Apply the following rule during every edit:

- **Use `\textbf{}` only for structural labels.** The canonical case is a paragraph-leading property header (e.g., `\textbf{Markovianity.}`, `\textbf{Expressiveness.}`) when the subsection does not use `\subsubsection` and the bold is acting as a pseudo-subheading.
- **Do not use `\textbf{}` for emphasis in running prose.** This includes property-name enumerations in subsection introductions, key-term highlighting, and "the reader should notice this" decoration.
- For the first introduction of a technical term, rely on the surrounding sentence structure rather than bold. Italics (`\textit{}`) are acceptable for term introductions but should also be used sparingly.
- Before adding any `\textbf{}`, ask: *"Is this bold acting as a structural label, or as decorative emphasis?"* If decorative, cut it.

---

## Voice and Tone

Write formally and professionally. The document should read like it was written by a competent researcher, not generated by a language model. Avoid conversational language, contractions, slang, and informal expressions.

### Core Rules

1. **Never use em dashes or their substitutes.** Do not use `—`, `–` (as sentence connectors), or ` - ` as a parenthetical/appositive connector mid-sentence. Instead use a period, semicolon, colon, comma, parentheses, or restructure the sentence.

   Hyphens in compound words (`low-latency`, `per-user`, `cold-start`) and en-dashes in number ranges (`7–14 days`, `4–17 images`) are fine.

2. **Conciseness: every word must earn its place.** Cut filler phrases. Remove material that does not contribute to the paper's purpose. Avoid single-sentence paragraphs except in rare justified cases.

   | Wordy | Concise |
   |---|---|
   | Due to the fact that | Because |
   | In order to | To |
   | At this point in time | Now |
   | Has the ability to | Can |
   | It's worth noting that | *(delete)* |

3. **Avoid hedge stacking.** One qualifier is fine ("typically", "usually"). Two or more in the same sentence sounds uncertain.

4. **Use active voice by default.** Passive is acceptable when the subject is unknown or irrelevant (e.g., "Participants were selected randomly.").

5. **Use concrete language.** Prefer specific numbers, examples, and measurements over vague qualifiers like "significant", "various", "robust", "leverage".

6. **Do not pluralize abstract nouns.** Nouns like "retention", "engagement", "latency", "coverage", "diversity" are uncountable. Never write "retentions", "engagements", "latencies".

7. **No ambiguous pronouns.** Every pronoun ("it", "this", "they", "which") must have a single, unambiguous antecedent. If there's any doubt, replace the pronoun with the noun.

8. **No unintended changes in meaning.** When editing or restructuring, verify the revised version preserves the original meaning exactly.

9. **Define acronyms on first use only.** Spell out the full term with the acronym in parentheses the first time. Use the acronym alone afterward. Never re-define it.

10. **No redundant statements.** Do not repeat the same point in different words across sections.

11. **No internal contradictions.** Numbers, conclusions, and claims must be consistent throughout. Cross-check all quantitative claims after drafting.

12. **No grandiose statements or overclaiming.** State results for what they are. Avoid extreme words like "crucial", "imperative", "essential", "groundbreaking", "revolutionary", "dramatically", "massive" unless fully justified by evidence.

13. **Parallel structure.** Keep list items and comparisons grammatically consistent.

14. **Clear modifiers.** Place modifiers directly next to the word they describe.

15. **Subject-verb agreement.** Match the verb to the true subject, even when separated by a clause.

16. **Precise comparisons.** Always compare like with like.

17. **Correlation vs. causation.** Do not imply causation without sufficient evidence. Use hedging language in research: *suggests, indicates, may contribute to, is associated with, appears to*.

18. **Numerals.** Never start a sentence with a numeral. Spell out integers from zero to nine in text; use numerals for 10 and above unless sentence position requires rewording.

19. **Lexical consistency.** When referring back to something, use the same term. If it was introduced as an "issue", do not later call it a "problem" without reason.

20. **Capitalize formal references.** Write "see Section 3.1" and "as shown in Table 2" (capitalized), but "in this section" and "the following table" (lowercase for generic uses).

---

## Word Precision

| Word Pair | Rule |
|---|---|
| **Affect** vs. **Effect** | Affect = verb (to influence), Effect = noun (the result) |
| **Less** vs. **Fewer** | Fewer = countable nouns, Less = uncountable nouns |
| **Which** vs. **That** | That = essential clause, Which = non-essential clause |
| **Since** vs. **Because** | Because = causation, Since = time reference |
| **While** vs. **Although** | Although = contrast, While = simultaneous events |

---

## Domain Terminology

Use these terms consistently throughout the paper:

- **MDP** (Markov Decision Process): the core abstraction; components are state, action, reward, policy
- **Contextual bandits**: one-step RL with context; a special case of RL, not a separate paradigm
- **Off-policy learning / offline RL**: learning from logged data without online interaction
- **Ad load**: the density or frequency of ads in a feed
- **Ad fatigue**: user desensitization from overexposure to ads
- **Utility function**: a weighted combination of objectives (revenue, engagement, fatigue)
- **Proxy metrics**: observable short-term signals used to approximate long-term objectives
- **Logging policy**: the historical policy that generated the training data
- **Distribution shift**: the mismatch between logging policy and learned policy distributions

Avoid interchanging related but distinct terms (e.g., "reward" vs. "utility function", "state" vs. "context", "offline RL" vs. "off-policy evaluation").

---

## Logical Structure of Arguments

Every claim needs: **Claim -> Evidence -> Reasoning -> Conclusion**

- **Claim:** State the point clearly.
- **Evidence:** Support with data, citations, or examples.
- **Reasoning:** Explain why the evidence supports the claim.
- **Conclusion:** Tie back to the broader research question.

---

## Sentence and Paragraph Structure

### Sentences
- Vary sentence length. Mix short punchy sentences with longer ones.
- One idea per sentence when possible.
- Avoid sentences over 30-35 words.

### Paragraphs
- One main idea per paragraph.
- Start with a topic sentence.
- End with a transition to the next idea.

---

## Common Logical Flaws to Watch For

- **Unwarranted assumptions.** The author assumes something without evidence.
- **Correlation vs. causation.** Two related things do not imply one caused the other.
- **Hasty generalizations.** Broad conclusions from limited data.
- **False analogies.** Comparing things that aren't truly comparable.
- **Ignoring alternative explanations.** Failing to consider other reasons for a result.

---

## ACM TORS Submission and Review Checklist

This paper targets ACM TORS. The following checklist (from the ACM TORS Submission and Review Checklist v1.0, June 2024) should be used as an audit when revising. Although this is a survey paper and not all items apply directly, the methodology and evaluation standards inform how the paper should discuss and compare cited works.

### Reproducibility (for cited experimental works)
When discussing a cited system or method, note whether the following are reported:
- Code availability (proposed method, baselines, preprocessing, tuning, execution, analysis)
- Data availability (original datasets, preprocessed versions, splits, results, trained models)
- Configuration details (hyperparameter search strategy, search space, best hyperparameters, random seeds, library versions, hardware)
- Experiment-specific details (evaluation framework used, one-click reproducibility, runtime)

### Methodology (for evaluating cited work and structuring the survey's own analysis)
- Research question is clearly stated; hypothesis follows from it; experimental design matches
- Baselines are appropriate (strong and simple), fairly tuned, and clearly identified as rerun or sourced from prior work
- Evaluation metrics are appropriate, nonredundant, and tradeoffs are discussed
- Data collection and preprocessing are clearly explained, with biases acknowledged
- Datasets are appropriate and diverse enough to support generalization claims
- Hyperparameter optimization is specified, sufficiently broad, and reported consistently
- Experiment execution is fair and statistically sound (significance testing, p-values, confidence intervals, hardware details)
- Sensitivity analysis is reported for relevant parameters and dataset properties

---

## When Editing This Paper

- Preserve the author's voice and structure unless asked to change it.
- When fixing prose, rewrite naturally rather than doing mechanical find-and-replace.
- All LaTeX edits must compile cleanly. Test that cross-references (`\ref`, `\cite`) remain valid.
- When adding citations, add the BibTeX entry to `bibliography.bib` and use the `authorYEARkeyword` key format.
- Keep table formatting consistent with existing conventions (booktabs rules, footnotesize, arraystretch 1.15).
- Every revision should strengthen the ad-specific focus. When in doubt about whether content belongs, ask: "Does this directly serve the paper's core question of jointly optimizing ads and organic content?"
- The final document should read as a guided, evidence-based, professionally written analysis that stands on its own.
