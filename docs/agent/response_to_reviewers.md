# Response to Reviewers: TORS-2025-0056

**Manuscript:** "A Practitioner-Oriented Review of Reinforcement Learning for
the Joint Optimization of Ads and Organic Content in Large-Scale Recommender
Systems" (formerly "A Review of Reinforcement Learning Applications in Ad
Policy Optimization for Large-Scale Recommender Systems")

Dear Prof. Jannach, Associate Editor, and Reviewers,

Thank you for the detailed and constructive feedback, and for granting the
extension to June 3. The reviews converged on a clear message: the topic is
timely and valuable to practitioners, but the original submission diluted its
focus with general RL/recsys material, did not critically compare methods, and
left evaluation underdeveloped. We have substantially restructured the
manuscript around these themes. Below we first summarize the major changes,
then respond to every comment from the Associate Editor and both reviewers.
Section and table references point to the revised manuscript.

---

## Summary of Major Changes

1. **Sharper, ad-specific focus and re-framing.** The title now leads with "A
   Practitioner-Oriented Review of…" and names "the Joint Optimization of Ads
   and Organic Content" explicitly. The abstract and introduction now state
   the central problem up front (jointly selecting, ranking, and placing ads
   within organic content) and frame the survey as a practitioner reference.

2. **Clear problem definition early.** A new subsection 4.1 ("Formulating
   Joint Ad and Organic Ranking as a Markov Decision Process") gives a single
   formal MDP definition with notation before the component-wise discussion,
   and Table 1 is a consolidated notation guide. This directly answers the AE's
   question of whether the goal is to rank ads independently or jointly: we make
   the joint formulation explicit, defining the action space as the union of the
   ad and organic candidate sets.

3. **Reduced pedagogical material.** The Frozen Lake example and the generic
   RNN-to-Transformer evolution narrative were removed. The remaining deep
   learning discussion (Section 3.2) is reframed around why interleaving ads in
   organic feeds creates a joint-optimization problem.

4. **New, dedicated evaluation section (Section 5).** It covers metric roles
   (primary, secondary, and guardrail KPIs), offline replay and counterfactual
   estimators (IPS, doubly robust), simulator-based testing (RecSim, SlateQ),
   and online A/B tests and long-term holdouts, plus two tables: an evaluation
   evidence/mechanism table and a **quantitative-results table** aggregating
   reported magnitudes from representative systems.

5. **More comparison and critical synthesis.** Comparison tables were added or
   restored (action-space designs, exploration-exploitation methods, evaluation
   mechanisms, quantitative results), and the conclusion now synthesizes
   recurring design trade-offs rather than re-listing methods.

6. **Citation alignment and depth fixes.** The misaligned citation R1 named was
   removed; a dedicated policy-gradient (REINFORCE) discussion was added; and
   terminology such as "displacement cost" is now introduced in context.

7. **Presentation fixes (AE + R2).** No references in the abstract; bold-face
   used sparingly; the acknowledgments rewritten to thank external
   collaborators only; all table/figure labels and cross-references corrected;
   Figure 1's note folded into its caption; tables positioned near their first
   mention.

---

## Response to the Associate Editor

> **"The focus of the work is not always entirely clear … A stronger focus on
> ad-related aspects is needed … clear definitions of the problems are needed
> at the beginning. E.g., is the goal to select and rank ads independently, or
> to rank ads and recommendations jointly; or both?"**

We restructured the manuscript around this. The title, abstract, and
introduction now foreground the joint optimization of ads and organic content.
The new subsection 4.1 gives the formal problem definition at the start of the
technical material: the action space is explicitly the union of ad and organic
candidates, and the policy "choos[es] both what to insert and where, rather
than treating ads and organic items as independent ranking problems." The
answer to the AE's question is therefore stated directly: the scope is the
**joint** problem (ad selection, ranking, and placement within organic
content), with independent ad ranking treated as the historical special case
that joint optimization generalizes (Section 3.2).

> **"A critical discussion and comparison of approaches seems missing."**

We added comparison tables and accompanying prose for action-space designs,
exploration-exploitation methods (with pros/cons and the contexts where each
is most effective), evaluation mechanisms, and reported quantitative results.
The conclusion was rewritten to synthesize cross-cutting trade-offs
(expressiveness vs. learnability, short- vs. long-horizon proxies,
support-limited off-policy estimation) instead of summarizing methods serially.

> **"Questions of evaluating the described methods are missing … at least some
> overview of common evaluation aspects, e.g., typical KPIs or outcomes of
> real-world studies, could be added."**

This is now a dedicated section (Section 5, "Evaluating Joint Ad and Organic
Ranking Policies"). It organizes KPIs into primary/secondary/guardrail roles,
explains offline replay, IPS/doubly-robust estimation, and simulators (RecSim,
SlateQ), and contrasts online A/B testing with long-term holdouts. A
quantitative-results table reports outcomes from real-world studies (e.g., DEAR
accumulated reward 10.96 vs. 10.27, \(p<0.05\); Jointly Learning +4.70% ad
revenue; Spotify multi-objective bandits +11.0% streams; Yahoo Gemini >20%
reduction in ad-close events with <0.4% revenue loss).

> **"Some parts seem repetitive and partially even not too relevant … the
> entire discussion of embeddings does not seem too specific for RL … policy
> learning is explained in some length, but the parts that are specific for
> ad-related aspects are not sufficiently emphasized."**

The embedding/deep-learning discussion was condensed and reframed (Section 3.2)
to explain specifically why feed-based ad insertion creates a joint
optimization problem that pointwise supervised models cannot capture, rather
than surveying representation learning generically. The policy-learning
material (Section 4.5) and the MDP framing (4.1) now tie each component to
ad-policy decisions (ad load, placement, eligibility, organic ordering) and the
off-policy/logging-policy conditions characteristic of ad systems.

> **"… re-framing of the work in the title and introductory sections,
> highlighting the introductory/tutorial nature … targeted at practitioners in
> industry."**

Done. The title now begins "A Practitioner-Oriented Review of…", and the
abstract and introduction state that the survey is aimed at industry
practitioners and is organized as a practical reference.

> **Minor: "please do not use references in the abstract."**

All citations were removed from the abstract.

> **Minor: "please use bold-face text sparingly."**

Bold-face was removed from running prose; it now appears only in table headers
and a small number of defined-term labels.

> **Minor: "the acknowledgment section looks quite uncommon, thanking the
> second author for the guidance."**

The acknowledgments were rewritten and no longer thank the second author; they
now thank external collaborators for feedback on industrial practice.

---

## Response to Reviewer 1

We appreciate the candid assessment. The revision targets the two reasons to
reject you identified (insufficient focus/depth and the absence of critical
comparison and evaluation) directly.

> **Major 1: Lack of depth in core content; real-world practices (YouTube,
> Meta, action abstraction) under-explored; needs comparison of trade-offs and
> real-world performance.**

We expanded the treatment of industrial systems and added explicit comparison.
The off-policy actor-critic deployment (YouTube), Horizon's offline→online
workflow, and constrained ad-allocation systems are now discussed in the
evaluation and policy-learning sections with their methods and outcomes, and
the quantitative-results table reports concrete magnitudes and significance
levels. Comparison tables make trade-offs (assumptions, action granularity,
evaluation mode) explicit rather than implied.

> **Major 2: Overemphasis on pedagogical material (RNN-to-Transformer evolution,
> Frozen Lake); prefer focused, domain-relevant illustrations (e.g.,
> bandit-based ad selection).**

The Frozen Lake example and the RNN-to-Transformer evolution narrative were
removed. Bandit "treatments" are now framed as concrete ad configurations
(displacement cost, reserve price, ad load, placement) where multi-armed
bandits are introduced (Section 3.1), and the exploration section (Section 4.6)
is organized around concrete ad-policy decisions, discussing the methods (with
pros/cons) in terms of when to explore new ads versus vary ad load. The
policy-learning section (Section 4.5) also gives a concrete ad-load
illustration contrasting value-based and policy-based choices.

> **Major 3: Evaluation is underdeveloped; metrics, simulator-based testing
> (RecSim), counterfactual estimators, and quantitative results missing.**

Addressed by the new Section 5, which explicitly covers metric roles, RecSim
and SlateQ, IPS and doubly-robust estimators, and online/holdout testing, and
by the quantitative-results table summarizing reported outcomes from existing
studies.

> **Major 4: Terminology used before definition (e.g., "displacement cost"
> defined only later in the appendix).**

Terminology is now introduced where first used. "Displacement cost" is defined
in context in Section 3.2 (every ad insertion displaces a candidate organic
item, with a cost that depends on the displaced item's value) and reused
consistently thereafter; Table 1 consolidates the recurring notation up front.

> **Major 5: Reference issues; e.g., a citation for "ads underperform relative
> to organic content" actually discusses user-generated reviews vs commercial
> messaging.**

The specific misaligned citation (`danescu2010competing`) was removed, and we
carried out a citation-alignment pass on the surrounding claims to ensure each
reference supports the statement it is attached to.

> **Major 6: Limited discussion of joint optimization / multi-objective
> balancing of engagement vs revenue.**

The joint, multi-objective formulation is now the organizing thread: the reward
section (4.2) reviews blended-utility and proxy-metric formulations, the MDP
section (4.1) shows ad and organic outcomes entering a single objective, and
the evaluation section frames success as improving the **trade-off** (weighted
utility, protected guardrails, reduced downside risk) rather than improving
each metric independently.

> **Major 7: Reward design and long-term metrics remain abstract; how
> surrogate metrics are identified and used in reward shaping.**

Section 4.2 (reward design) now discusses the properties a usable proxy must
satisfy (short-term observable, predictive of long-term value, dense enough to
learn from, decorrelated from inputs to avoid circular optimization), with
proxy-metric tables for revenue, engagement, and fatigue families and the
surrogate-metric literature (e.g., long-term value surrogates).

> **Suggestions (depth on deployments; comparison framework; terminology +
> citation alignment; evaluation strategies/simulators/toolkits).**

These are incorporated through the changes above: industrial-deployment depth
and quantitative outcomes, comparison tables organized around challenges
(exploration, long-term optimization, evaluation, constraints), in-context
terminology, and an evaluation section covering metrics, simulators, and
estimators.

> **Soundness: "many important methods are barely described (e.g. policy
> gradient methods such as REINFORCE, or methods to deal with extremely large
> action spaces)."**

A dedicated policy-gradient discussion (including REINFORCE) was added to the
policy-learning section, and the action-space section treats large/structured
action spaces (ad-vs-organic decomposition, ad-load and frequency constraints,
slate structure) with representative methods.

---

## Response to Reviewer 2

> **"Tables 3-4 are referred but there are no such tables; figures 3-4 look to
> be tables but are mentioned as figures."**

All float labels and cross-references were corrected; tables are now labeled and
referenced as tables and figures as figures. The manuscript compiles with zero
undefined references, citations, or labels, and every float is referenced in
the text.

> **"Make sure the text in the figures is readable and not too small. For notes
> under Figure 1, use footnotes or include in the figure caption."**

Figure 1's note is now part of its caption. We also reviewed the rendered PDF
for figure text size and table density and adjusted where needed.

> **"Position tables in the text where they are mentioned (tables were at the
> end but mentioned earlier)."**

Tables were repositioned to appear near their first mention (e.g., the notation
guide immediately follows the methodology paragraph that introduces it, and the
evaluation tables sit within Section 5).

> **"Section 3.2 (pg10 line 27): the MAB / clinical-trials paragraph may be
> confusing to a reader."**

That paragraph was rewritten to lead with the recommender/ad framing; the MAB
discussion now defines "treatments" directly as ad configurations and "rewards"
as engagement metrics, without the clinical-trials detour.

> **"The RL formulation (Section 4) is spread across subsections … better to
> have a separate subsection introducing the RL task (formulating as MDP, etc.)
> with notation. Include a table of notation if possible."**

We added subsection 4.1, which introduces the MDP formulation and notation in
one place before the component-by-component discussion, and Table 1 is a
dedicated notation guide for the recurring RL constructs.

> **"There is a notable amount of existing RL-based recommender research,
> including ad-serving approaches. Use more citations from this literature."**

We added further ad-serving and RL-recommender references (e.g., constrained
actor-critic for short-video, off-policy ad-load balancing, joint
recommendation-and-advertising, whole-page ad allocation) and anchored
ad-specific claims to ad/recsys sources rather than general RL works.

> **"Several statements about adaptability of RL … are not sufficiently backed
> by literature; some cited work is on general RL, not ad-policies/recsys."**

We carried out a citation-alignment pass to replace or hedge claims that were
anchored only to general RL sources, attaching ad- or recommender-specific
references where the claim is ad-specific.

> **"Writing and structure need improvement; repeated information across
> sections."**

The component-wise structure was tightened to reduce overlap (the deep-learning
and state-space material was condensed and refocused, and the conclusion now
synthesizes rather than restates), and the new MDP subsection removes the need
to re-introduce notation in each later section.

---

We believe these revisions address the substantive concerns (focus, critical
comparison, and evaluation) as well as the presentation items, and we thank
the reviewers and editors again for feedback that materially improved the
paper.
