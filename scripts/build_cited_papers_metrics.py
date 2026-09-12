#!/usr/bin/env python3
"""Regenerate CITED_PAPERS_METRICS.md from paper.tex, bibliography, and audit data."""

from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Metric families (column id, short header for table)
METRIC_FAMILIES: list[tuple[str, str]] = [
    ("ctr", "CTR / clicks"),
    ("auc", "AUC / log loss"),
    ("cvr", "CVR / conversion"),
    ("rev", "Revenue / RPM"),
    ("rank", "NDCG / HR / Recall"),
    ("dwell", "Dwell / watch time"),
    ("ltv", "Retention / LTV"),
    ("regret", "Regret / bandit loss"),
    ("rl", "RL reward / return"),
    ("ope", "OPE / RMSE"),
    ("adux", "Ad load / UX"),
]

FAMILY_IDS = [f[0] for f in METRIC_FAMILIES]

# Explicit overrides (most accurate for edge cases and verified papers)
KEY_FAMILIES: dict[str, set[str]] = {
    "Mehrotra2020": {"ctr", "rl"},
    "Theocharous-2015": {"ctr", "ltv"},
    "barajas2022online": {"cvr", "rev", "adux"},
    "bietti2021contextual": {"regret"},
    "cai2023two": {"dwell", "ctr", "rl"},
    "carrion2021blending": {"rev", "ltv", "rl", "ctr"},
    "chen2022off": {"rl", "ope", "ltv"},
    "dudik2011doubly": {"ope"},
    "foster2018contextual": {"regret", "rl"},
    "hohnhold2015focusing": {"rev", "ctr", "ltv", "adux"},
    "ie2019recsim": {"rl", "rank"},
    "ie2019slateq": {"ctr", "ltv", "rl"},
    "sagtani2023quantifying": {"ctr", "dwell", "adux"},
    "sagtani2024ad": {"ltv", "dwell", "ctr", "rev", "adux", "ope"},
    "silberstein2020ad": {"adux", "ctr", "rev"},
    "swaminathan2015counterfactual": {"regret", "ope"},
    "wang2022surrogate": {"ltv", "dwell", "rl"},
    "mcdonald2023spotify": {"ltv"},
    "wu2018budget": {"ctr", "rev", "rl"},
    "xu2023optimizing": {"cvr", "rl", "adux"},
    "yan2020ads": {"rev", "ctr"},
    "zhang2018whole": {"rev", "ctr", "adux"},
    "zhao2020jointly": {"dwell", "rev", "rl"},
    "zhao2021dear": {"rl", "rev", "ctr", "adux"},
    "zou2019reinforcement": {"ctr", "dwell", "ltv", "rl"},
    "afsar2022reinforcement": {"rank", "rl"},
    "lin2023survey": {"rank", "rl"},
    "levine2020offline": set(),
    "Jannach2023": set(),
    "mnih2016asynchronous": {"rl"},
    "schulman2015trust": {"rl"},
    "schulman2017proximal": {"rl"},
    "van2016deep": {"rl"},
    "vaswani2017attention": set(),  # BLEU/perplexity — not in our ad-rec families
    "williams1992simple": {"rl"},
    "dulac2019challenges": {"rl"},
    "dulac2021challenges": {"rl"},
    "everitt2021reward": {"rl"},
    "gauci2018horizon": {"ctr", "rl", "ope"},
    "deffayet2022offline": {"rank", "ope", "rl"},
    "li2010contextual": {"ctr", "regret"},
    "chapelle2011empirical": {"regret", "ctr"},
    "zhou2016latent": {"ctr", "regret"},
    "zhao2018deep": {"ctr", "rev", "rl", "rank"},
    "gao2022bidding": {"cvr", "rev", "ctr"},
    "schwartz2017customer": {"cvr", "ctr"},
    "zhang2024scaling": {"ctr", "cvr"},
    "mcmahan2013ad": {"auc", "ctr"},
    "Zhou2018": {"auc", "ctr"},
    "Zhou2019": {"auc", "ctr"},
    "yuan2020unbiased": {"auc", "ctr"},
    "naumov2019deep": {"auc"},
    "cheng2016wide": {"auc", "ctr"},
    "Kang2018": {"rank"},
    "kang2018sasrec": {"rank"},
    "pancha2022pinnerformer": {"rank"},
    "xia2023transact": {"rank", "dwell"},
    "zhao2018recommendations": {"rank", "rl"},
    "covington2016deep": {"dwell", "ctr"},
    "yi2014beyond": {"dwell", "ctr"},
    "pan2023learning": {"dwell"},
    "wu2018beyond": {"dwell", "ctr"},
    "wu2017returning": {"ltv", "dwell", "rl"},
    "mazoure2021improving": {"ltv", "rl"},
    "mcdonald2023impatient": {"ltv", "rl"},
    "yi2023progressive": {"ltv", "rl"},
    "ie2019reinforcement": {"rl", "ltv"},
    "wen2019learning": {"rl"},
    "tang2013ad": {"ctr", "rev"},
    "silberstein2023combating": {"ctr", "rev", "cvr", "adux"},
    "koutsopoulos2016native": {"rev", "ctr", "dwell"},
    "cui2015global": {"rev", "adux", "ctr"},
    "chen2009large": {"ctr", "cvr", "adux"},
    "yan2009much": {"ctr", "cvr", "adux"},
    "grbovic2018real": {"cvr", "rank"},
    "liu2022monolith": {"cvr", "dwell"},
    "lu2016partially": {"rank"},
    "agarwal2014budget": {"rev", "adux"},
    "abrams2007personalized": {"rev", "adux"},
    "saha2021advertiming": {"adux", "dwell"},
    "nielsen2017advertising": set(),  # brand recall — outside families
    "hu2004performance": {"rev"},
    "engel2008incorporating": {"rev"},
    "ellam2003overture": {"rev"},
    "burtini2015improving": {"regret", "rl"},
    "van2024practical": {"regret", "ctr", "rev"},
    "agarwal2014taming": {"regret"},
    "agarwal2019online": {"regret"},
    "auer2002finite": {"regret"},
    "bubeck2012regret": {"regret"},
    "kuleshov2014algorithms": {"regret"},
    "robbins1952sequential": {"regret"},
    "russo2018tutorial": {"regret"},
    "chakrabarti2008contextual": {"ctr", "rank"},
    "vouros2022explainable": {"rl"},
    "vorotilov2023scaling": {"dwell", "ltv"},
    "agarwal2020optimistic": {"rl", "ope"},
    "kaelbling1998planning": {"rl"},
}


def extract_cite_keys(tex: str) -> list[str]:
    return sorted(count_cite_keys(tex).keys())


def count_cite_keys(tex: str) -> dict[str, int]:
    """Count how many times each bib key appears in \\cite... commands in paper.tex."""
    skip_keys = {"acmauthoryear"}
    counts: dict[str, int] = {}
    for match in re.finditer(r"\\cite(?!style)[a-zA-Z]*\{([^}]+)\}", tex):
        for k in match.group(1).split(","):
            k = k.strip()
            if k and k not in skip_keys:
                counts[k] = counts.get(k, 0) + 1
    return counts


def _clean_bib_value(raw: str) -> str:
    text = re.sub(r"[\n\r\t]+", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("{", "").replace("}", "")


def _extract_bib_field(entry: str, field: str) -> str:
    """Extract a bib field value (handles nested braces for braced values)."""
    m = re.search(rf"{field}\s*=\s*\"", entry, re.IGNORECASE)
    if m:
        end = entry.find('"', m.end())
        if end != -1:
            return _clean_bib_value(entry[m.end():end])
    m = re.search(rf"{field}\s*=\s*\{{", entry, re.IGNORECASE)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(entry) and depth:
        ch = entry[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        i += 1
    return _clean_bib_value(entry[start : i - 1])


def parse_bib() -> dict[str, dict]:
    bib_content = (ROOT / "bibliography.bib").read_text()
    bib_db: dict[str, dict] = {}
    extra_fields = (
        "journal",
        "booktitle",
        "publisher",
        "organization",
        "howpublished",
        "institution",
        "school",
        "address",
        "note",
    )
    link_fields = ("url", "doi", "eprint", "eprinttype")
    for entry in re.split(r"\n@", "\n" + bib_content):
        if not entry.strip():
            continue
        match = re.match(r"([a-zA-Z]+)\s*\{([^,]+),", entry)
        if not match:
            continue
        entry_type = match.group(1).strip().lower()
        key = match.group(2).strip()
        title = _extract_bib_field(entry, "title") or "Unknown Title"
        info: dict[str, str] = {"title": title, "type": entry_type}
        for field in extra_fields + link_fields:
            value = _extract_bib_field(entry, field)
            if value:
                info[field] = value
        bib_db[key] = info
    return bib_db


PDF_URL_CACHE_PATH = ROOT / "scripts" / "citation_pdf_url_cache.json"

# Verified paper links (PDF when available; otherwise best official landing page).
# Overrides take precedence over the OpenAlex/Semantic Scholar cache.
PDF_URL_OVERRIDES: dict[str, str] = {
    "zhao2021dear": "https://arxiv.org/pdf/1909.03602.pdf",
    "zhao2020jointly": "https://arxiv.org/pdf/2003.00097.pdf",
    "Sutton1998": "http://incompleteideas.net/book/the-book-2nd.html",
    "wikipedia-cpm": "https://en.wikipedia.org/wiki/Cost_per_mille",
    # Corrections (previously wrong in auto-resolved cache)
    "agarwal2019online": "https://dl.acm.org/doi/pdf/10.1145/3292500.3330677",
    "kant2021history": "https://thereader.mitpress.mit.edu/a-history-of-the-data-tracked-user/",
    "yi2014beyond": "https://dl.acm.org/doi/pdf/10.1145/2645710.2645733",
    "vaswani2017attention": "https://arxiv.org/pdf/1706.03762",
    "Zhou2019": "https://ojs.aaai.org/index.php/AAAI/article/download/4545/4423",
    "vorotilov2023scaling": "https://engineering.fb.com/2023/08/09/ml-applications/scaling-instagram-explore-recommendations-system/",
    "mcdonald2023spotify": "https://research.atspotify.com/2023/07/optimizing-for-the-long-term-without-delay/",
    "mcdonald2023impatient": "https://arxiv.org/pdf/2307.09943",
    # Previously missing
    "Theocharous-2015": "https://www.ijcai.org/Proceedings/15/Papers/257.pdf",
    "abrams2007personalized": "https://link.springer.com/content/pdf/10.1007/978-3-540-77105-0_57.pdf",
    "auer2002finite": "https://link.springer.com/content/pdf/10.1023/A:1013689704352.pdf",
    "barajas2022online": "https://link.springer.com/content/pdf/10.1007/978-3-030-99739-7_72.pdf",
    "burtini2015improving": "https://www.scitepress.org/PublishedPapers/2015/54587/54587.pdf",
    "ccelik2023ad": "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/ijcs.12882",
    "chakrabarti2008contextual": "https://dl.acm.org/doi/pdf/10.1145/1367497.1367554",
    "chapelle2011empirical": "https://proceedings.neurips.cc/paper/2011/file/e53a0a2978c28872a4505bdb51db06dc-Paper.pdf",
    "chen2009large": "https://people.eecs.berkeley.edu/~jfc/papers/09/KDD09.pdf",
    "cui2015global": "https://link.springer.com/content/pdf/10.1007/s11390-015-1523-4.pdf",
    "dimitrakakis2018decision": "https://www.cse.chalmers.se/~chrdimi/downloads/book.pdf",
    "engel2008incorporating": "https://dl.acm.org/doi/pdf/10.5555/1402790.1403055",
    "grbovic2018real": "https://dl.acm.org/doi/pdf/10.1145/3219819.3219885",
    "kaelbling1998planning": "https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf",
    "koutsopoulos2016native": "https://link.springer.com/content/pdf/10.1007/978-3-319-46128-1_37.pdf",
    "sagtani2023quantifying": "https://dl.acm.org/doi/pdf/10.1145/3539618.3592044",
    "saha2021advertiming": "https://dl.acm.org/doi/pdf/10.1145/3411764.3445394",
    "shahriari2015taking": "https://arxiv.org/pdf/1502.05700",
    "silberstein2020ad": "https://dl.acm.org/doi/pdf/10.1145/3336191.3371798",
    "silberstein2023combating": "https://dl.acm.org/doi/pdf/10.1145/3583780.3615461",
    "yan2009much": "https://dl.acm.org/doi/pdf/10.1145/1526709.1526745",
    "yan2020ads": "https://dl.acm.org/doi/pdf/10.1145/3394486.3403391",
    "yuan2020unbiased": "https://dl.acm.org/doi/pdf/10.1145/3383313.3412241",
    # Best official link when no open PDF exists
    "nielsen2017advertising": "https://www.nielsen.com/insights/2017/when-it-comes-to-advertising-effectiveness-what-is-key/",
    "wsj2003yahoooverture": "https://www.wsj.com/articles/SB105818965623153600",
    "hu2004performance": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=501082",
    "agarwal2016statistical": "https://www.cambridge.org/highereducation/products/statistical-methods-for-recommender-systems/F9781107036075",
    "puterman2014markov": "https://onlinelibrary.wiley.com/doi/book/10.1002/9780470317195",
    "russell2016artificial": "https://aima.cs.berkeley.edu/",
}


def _strip_latex_url(raw: str) -> str:
    text = raw.strip()
    if text.lower().startswith(r"\url{") and text.endswith("}"):
        text = text[5:-1].strip()
    return text.replace("{", "").replace("}", "")


def _arxiv_id_from_text(text: str) -> str:
    if not text:
        return ""
    match = re.search(r"arxiv[:\s]*([\d]{4}\.[\d]{4,5}(?:v\d+)?)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"([\d]{4}\.[\d]{4,5}(?:v\d+)?)", text)
    return match.group(1) if match else ""


def _arxiv_pdf_url(arxiv_id: str) -> str:
    arxiv_id = arxiv_id.strip().removesuffix(".pdf")
    if not arxiv_id:
        return ""
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"


def _normalize_http_url(raw: str) -> str:
    url = _strip_latex_url(raw)
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return ""


def _pdf_url_from_doi(doi: str) -> str:
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
    if not doi:
        return ""
    if doi.startswith("10.1145/"):
        return f"https://dl.acm.org/doi/pdf/{doi}"
    if doi.startswith("10.1007/"):
        return f"https://link.springer.com/content/pdf/{doi}.pdf"
    if doi.startswith("10.1111/"):
        return f"https://onlinelibrary.wiley.com/doi/pdfdirect/{doi}"
    if doi.startswith("10.24963/ijcai."):
        match = re.match(r"10\.24963/ijcai\.(\d{4})/(\d+)", doi)
        if match:
            year, paper_id = match.group(1), match.group(2)
            return f"https://www.ijcai.org/proceedings/{year}/{int(paper_id):04d}.pdf"
    if doi.startswith("10.48550/") or "arxiv" in doi.lower():
        arxiv_id = doi.split("arXiv.")[-1] if "arxiv" in doi.lower() else ""
        if arxiv_id:
            return _arxiv_pdf_url(arxiv_id)
    return ""


def _pdf_url_from_bib_info(info: dict[str, str]) -> str:
    """Best-effort PDF URL from bib url/doi/eprint fields only."""
    url = _normalize_http_url(info.get("url", ""))
    if url:
        lower = url.lower()
        if lower.endswith(".pdf") or "/pdf/" in lower or "pdfdirect" in lower:
            return url
        abs_match = re.search(r"arxiv\.org/abs/([\d]{4}\.[\d]{4,5}(?:v\d+)?)", url, re.I)
        if abs_match:
            return _arxiv_pdf_url(abs_match.group(1))
        nips_match = re.search(r"papers\.nips\.cc/paper/\d+", url, re.I)
        if nips_match:
            return url if url.endswith(".pdf") else url + ".pdf"

    doi = info.get("doi", "").strip()
    if doi:
        from_doi = _pdf_url_from_doi(doi)
        if from_doi:
            return from_doi

    eprint = info.get("eprint", "").strip()
    eprinttype = info.get("eprinttype", "").strip().lower()
    if eprint and (eprinttype == "arxiv" or re.match(r"[\d]{4}\.", eprint)):
        return _arxiv_pdf_url(_arxiv_id_from_text(eprint) or eprint)

    journal = info.get("journal", "")
    arxiv_id = _arxiv_id_from_text(journal)
    if arxiv_id:
        return _arxiv_pdf_url(arxiv_id)

    return ""


def _fallback_url_from_bib_info(info: dict[str, str]) -> str:
    """Non-PDF official URL from bib when no PDF could be resolved."""
    return _normalize_http_url(info.get("url", ""))


def load_pdf_url_cache() -> dict[str, str]:
    if not PDF_URL_CACHE_PATH.exists():
        return {}
    try:
        data = json.loads(PDF_URL_CACHE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if isinstance(data, dict):
        return {str(k): str(v) for k, v in data.items() if v}
    return {}


def save_pdf_url_cache(cache: dict[str, str]) -> None:
    PDF_URL_CACHE_PATH.write_text(
        json.dumps(dict(sorted(cache.items())), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _pdf_from_openalex_work(work: dict) -> str:
    if not isinstance(work, dict):
        return ""
    for location_key in ("best_oa_location", "primary_location"):
        location = work.get(location_key)
        if isinstance(location, dict):
            pdf_url = location.get("pdf_url") or ""
            if pdf_url:
                return _normalize_http_url(pdf_url)
    oa_info = work.get("open_access")
    if isinstance(oa_info, dict):
        oa_url = oa_info.get("oa_url") or ""
        if oa_url.lower().endswith(".pdf"):
            return _normalize_http_url(oa_url)
    return ""


def _title_match_score(query_title: str, candidate_title: str) -> float:
    def norm(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", (text or "").lower())

    query = norm(query_title)
    candidate = norm(candidate_title)
    if not query or not candidate:
        return 0.0
    if query == candidate:
        return 1.0
    if query in candidate or candidate in query:
        return 0.9
    return 0.0


def _openalex_pdf_url(*, doi: str = "", title: str = "") -> str:
    """Query OpenAlex for an open-access PDF URL (network call)."""
    if doi:
        doi_clean = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        endpoint = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi_clean)}"
    elif title:
        endpoint = (
            "https://api.openalex.org/works?"
            + urllib.parse.urlencode({"search": title, "per_page": 5})
        )
    else:
        return ""

    request = urllib.request.Request(
        endpoint,
        headers={"User-Agent": "Review-Paper-RL-Ad-Rec-Systems/1.0 (mailto:local-build)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return ""

    if "results" in payload:
        results = payload.get("results") or []
        if not results:
            return ""
        if title:
            ranked: list[tuple[float, int, dict]] = []
            for idx, work in enumerate(results):
                if not isinstance(work, dict):
                    continue
                score = _title_match_score(title, work.get("title", ""))
                has_pdf = 1 if _pdf_from_openalex_work(work) else 0
                ranked.append((score, has_pdf, work))
            ranked.sort(key=lambda item: (item[0], item[1], -item[2].get("cited_by_count", 0)), reverse=True)
            for score, _has_pdf, work in ranked:
                if score <= 0:
                    break
                pdf_url = _pdf_from_openalex_work(work)
                if pdf_url:
                    return pdf_url
            if ranked and ranked[0][0] > 0:
                return _pdf_from_openalex_work(ranked[0][2])
            work = results[0]
        else:
            work = results[0]
    else:
        work = payload

    return _pdf_from_openalex_work(work)


def _semantic_scholar_pdf(*, doi: str = "", title: str = "") -> str:
    """Fallback PDF lookup via Semantic Scholar (network call)."""
    if doi:
        doi_clean = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        endpoint = (
            "https://api.semanticscholar.org/graph/v1/paper/"
            + urllib.parse.quote(f"DOI:{doi_clean}")
            + "?fields=openAccessPdf,title"
        )
    elif title:
        endpoint = (
            "https://api.semanticscholar.org/graph/v1/paper/search?"
            + urllib.parse.urlencode(
                {"query": title, "limit": 5, "fields": "openAccessPdf,title"}
            )
        )
    else:
        return ""

    request = urllib.request.Request(
        endpoint,
        headers={"User-Agent": "Review-Paper-RL-Ad-Rec-Systems/1.0 (mailto:local-build)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return ""

    if "data" in payload:
        papers = payload.get("data") or []
        if not papers:
            return ""
        if title:
            ranked: list[tuple[float, dict]] = []
            for paper in papers:
                if not isinstance(paper, dict):
                    continue
                ranked.append((_title_match_score(title, paper.get("title", "")), paper))
            ranked.sort(key=lambda item: item[0], reverse=True)
            for score, paper in ranked:
                if score <= 0:
                    break
                oa_pdf = paper.get("openAccessPdf") or {}
                if isinstance(oa_pdf, dict) and oa_pdf.get("url"):
                    return _normalize_http_url(str(oa_pdf["url"]))
            paper = ranked[0][1] if ranked else papers[0]
        else:
            paper = papers[0]
    else:
        paper = payload

    if isinstance(paper, dict):
        oa_pdf = paper.get("openAccessPdf") or {}
        if isinstance(oa_pdf, dict) and oa_pdf.get("url"):
            return _normalize_http_url(str(oa_pdf["url"]))
    return ""


def resolve_pdf_url(
    key: str,
    info: dict[str, str],
    cache: dict[str, str],
    *,
    fetch_missing: bool = False,
) -> str:
    """Resolve a direct PDF (or best open-access) URL for a cited paper."""
    if key in PDF_URL_OVERRIDES:
        return PDF_URL_OVERRIDES[key]
    if key in cache and cache[key]:
        return cache[key]

    from_bib = _pdf_url_from_bib_info(info)
    if from_bib:
        cache[key] = from_bib
        return from_bib

    if fetch_missing:
        fetched = _openalex_pdf_url(doi=info.get("doi", ""), title=info.get("title", ""))
        if not fetched:
            fetched = _semantic_scholar_pdf(doi=info.get("doi", ""), title=info.get("title", ""))
        if fetched:
            cache[key] = fetched
            return fetched

    fallback = _fallback_url_from_bib_info(info)
    if fallback:
        return fallback

    doi = info.get("doi", "").strip()
    if doi:
        doi_clean = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
        return f"https://doi.org/{doi_clean}"

    return ""


def format_title_cell(title: str, pdf_url: str) -> str:
    escaped = html.escape(title)
    if not pdf_url:
        return escaped
    href = html.escape(pdf_url, quote=True)
    is_pdf = pdf_url.lower().rstrip("/").endswith(".pdf") or "/pdf" in pdf_url.lower()
    link_title = "Open paper PDF" if is_pdf else "Open paper"
    return (
        f'<a class="paper-pdf-link" href="{href}" target="_blank" '
        f'rel="noopener noreferrer" title="{link_title}">{escaped}</a>'
    )


# Primary affiliation labels for industrial / institutional papers (manual curation).
AFFILIATION_OVERRIDES: dict[str, str] = {
    "zhao2021dear": "ByteDance / TikTok; Michigan State Univ.",
    "zhao2020jointly": "Academic + industry (joint ad–organic lists)",
    "chen2022off": "Google / YouTube",
    "gauci2018horizon": "Meta",
    "yan2020ads": "LinkedIn",
    "zhang2018whole": "Alibaba",
    "Mehrotra2020": "Spotify",
    "sagtani2024ad": "Meta",
    "sagtani2023quantifying": "Spotify",
    "silberstein2020ad": "Yahoo / Verizon Media (Gemini)",
    "silberstein2023combating": "Meta",
    "hohnhold2015focusing": "Google",
    "covington2016deep": "Google / YouTube",
    "cheng2016wide": "Google",
    "Zhou2018": "Alibaba",
    "Zhou2019": "Alibaba",
    "mcmahan2013ad": "Google",
    "gao2022bidding": "LinkedIn",
    "agarwal2014budget": "LinkedIn",
    "tang2013ad": "LinkedIn",
    "wu2018budget": "Alibaba",
    "xu2023optimizing": "Meta",
    "zhang2024scaling": "Meta",
    "vorotilov2023scaling": "Meta (Instagram)",
    "carrion2021blending": "JD.com",
    "grbovic2018real": "Airbnb",
    "pancha2022pinnerformer": "Pinterest",
    "xia2023transact": "Pinterest",
    "liu2022monolith": "ByteDance",
    "mcdonald2023spotify": "Spotify",
    "mcdonald2023impatient": "Spotify",
    "wang2022surrogate": "Google",
    "yi2023progressive": "Microsoft",
    "yi2014beyond": "Yahoo!",
    "naumov2019deep": "Meta",
    "li2010contextual": "Yahoo!",
    "chapelle2011empirical": "Yahoo! / Criteo",
    "yan2009much": "Yahoo!",
    "engel2008incorporating": "Microsoft (Live Labs) / U. Michigan",
    "chakrabarti2008contextual": "Yahoo!",
    "chen2009large": "Microsoft / Yahoo!",
    "hu2004performance": "Google",
    "ie2019recsim": "Google",
    "ie2019slateq": "Google",
    "ie2019reinforcement": "Google",
    "vaswani2017attention": "Google",
    "zhao2018recommendations": "Google / YouTube",
    "zhou2016latent": "Microsoft",
    "Kang2018": "Microsoft",
    "dudik2011doubly": "Microsoft Research",
    "swaminathan2015counterfactual": "Microsoft Research / Cornell",
    "agarwal2016statistical": "Microsoft Research",
    "agarwal2014taming": "Microsoft Research / Cornell",
    "agarwal2019online": "Google",
    "agarwal2020optimistic": "Google",
    "zou2019reinforcement": "Huawei Noah's Ark Lab",
    "pan2023learning": "Kuaishou (industrial short-video)",
    "cai2023two": "Kuaishou / short-video industry",
    "yuan2020unbiased": "Alibaba",
    "saha2021advertiming": "Meta",
    "barajas2022online": "Adobe",
    "Theocharous-2015": "Adobe",
    "van2024practical": "Spotify / industry",
    "deffayet2022offline": "Criteo / Univ. of Amsterdam",
    "wen2019learning": "Baidu",
    "cui2015global": "Google / Tencent (native ads)",
    "nielsen2017advertising": "Nielsen",
    "ellam2003overture": "Yahoo / Overture",
    "wsj2003yahoooverture": "Wall Street Journal (news)",
    "wikipedia-cpm": "Wikipedia",
    "Sutton1998": "Academic (RL textbook)",
    "russell2016artificial": "Academic (AI textbook)",
    "puterman2014markov": "Academic (MDP textbook)",
    "kaelbling1998planning": "MIT",
    "kaelbling1996reinforcement": "Academic",
    "robbins1952sequential": "Academic",
    "van2016deep": "DeepMind",
    "mnih2016asynchronous": "DeepMind",
    "dulac2019challenges": "DeepMind",
    "dulac2021challenges": "DeepMind",
    "everitt2021reward": "DeepMind",
    "levine2020offline": "UC Berkeley",
    "schulman2015trust": "OpenAI / UC Berkeley",
    "schulman2017proximal": "OpenAI",
    "williams1992simple": "Academic",
    "auer2002finite": "Academic",
    "bubeck2012regret": "Academic",
    "foster2018contextual": "Academic",
    "bietti2021contextual": "Academic",
    "afsar2022reinforcement": "Academic (survey)",
    "lin2023survey": "Academic (survey)",
    "zhao2024survey": "Academic (survey)",
    "glanois2024survey": "Academic (survey)",
    "gama2014survey": "Academic (survey)",
    "vouros2022explainable": "Academic (survey)",
    "zhu2021overview": "Academic (survey)",
    "Jannach2023": "Academic (survey)",
    "russo2018tutorial": "Spotify / Cornell",
    "kant2021history": "MIT Press Reader",
    "acmauthoryear": "ACM (citation style)",
    "shahriari2015taking": "Univ. of British Columbia",
    "kang2018sasrec": "Korea Univ. / academic",
    "lu2016partially": "Academic",
    "mazoure2021improving": "Mila / academic",
    "wu2017returning": "Academic",
    "wu2018beyond": "Academic (ANU / UTS)",
    "koutsopoulos2016native": "Academic",
    "zhao2018deep": "Academic (RTB)",
    "schwartz2017customer": "Academic",
    "burtini2015improving": "Academic",
    "kuleshov2014algorithms": "Columbia Univ.",
    "dimitrakakis2018decision": "Academic",
    "abrams2007personalized": "Academic",
    "fain2006sponsored": "Academic",
    "lambert2023entangled": "Academic",
    "ccelik2023ad": "Academic (systematic review)",
}

# Regex patterns applied to title + bib metadata when no override exists.
AFFILIATION_PATTERNS: list[tuple[str, str]] = [
    (r"\b(Engineering at Meta|Meta Platforms?|Facebook|Instagram)\b", "Meta"),
    (r"\b(Google|YouTube|Alphabet)\b", "Google"),
    (r"\bLinkedIn\b", "LinkedIn"),
    (r"\b(Spotify)\b", "Spotify"),
    (r"\b(Alibaba|Ant Financial)\b", "Alibaba"),
    (r"\b(ByteDance|TikTok|Monolith)\b", "ByteDance"),
    (r"\bPinterest\b", "Pinterest"),
    (r"\bAirbnb\b", "Airbnb"),
    (r"\b(JD\.?COM|JD\.com)\b", "JD.com"),
    (r"\b(Yahoo|Overture|Gemini)\b", "Yahoo"),
    (r"\b(Microsoft)\b", "Microsoft"),
    (r"\b(DeepMind)\b", "DeepMind"),
    (r"\b(Netflix)\b", "Netflix"),
    (r"\b(Adobe)\b", "Adobe"),
    (r"\b(Huawei)\b", "Huawei"),
    (r"\b(Kuaishou)\b", "Kuaishou"),
    (r"\b(Criteo)\b", "Criteo"),
    (r"\b(Nielsen)\b", "Nielsen"),
    (r"\b(Baidu)\b", "Baidu"),
    (r"\b(Tencent)\b", "Tencent"),
]


def infer_affiliation(title: str, bib_info: dict[str, str]) -> str:
    """Best-effort affiliation from bib metadata and title."""
    parts = [title]
    for field in (
        "journal",
        "booktitle",
        "publisher",
        "organization",
        "howpublished",
        "institution",
        "school",
        "address",
        "note",
    ):
        if field in bib_info:
            parts.append(bib_info[field])
    haystack = " ".join(parts)
    for pattern, label in AFFILIATION_PATTERNS:
        if re.search(pattern, haystack, re.IGNORECASE):
            return label
    entry_type = bib_info.get("type", "")
    if entry_type == "book":
        return "Academic (book)"
    if re.search(r"\bsurvey\b|\breview\b|\btutorial\b", haystack, re.IGNORECASE):
        return "Academic (survey/review)"
    return "Academic / industry unclear"


def affiliation_for_key(key: str, title: str, bib_info: dict[str, str]) -> str:
    if key in AFFILIATION_OVERRIDES:
        return AFFILIATION_OVERRIDES[key]
    return infer_affiliation(title, bib_info)


def parse_audit_metrics(audit_text: str) -> dict[str, str]:
    metrics_by_key: dict[str, str] = {}
    blocks = re.split(r"\n\*\*", audit_text)
    for block in blocks:
        key_match = re.search(r"\[`([^`]+)`\]", block)
        metrics_match = re.search(r"\*\*Metrics Used:\*\*\s*(.+)", block, re.DOTALL)
        if key_match and metrics_match:
            key = key_match.group(1)
            if key in metrics_by_key:
                continue
            raw = metrics_match.group(1).split("\n")[0].strip()
            raw = re.sub(r"\$[^$]+\$", lambda m: m.group(0).replace("$", ""), raw)
            raw = raw.replace("\\", "")
            metrics_by_key[key] = raw
    return metrics_by_key


def _clean_audit_line(text: str) -> str:
    text = re.sub(r"\$([^$]+)\$", r"\1", text)
    return text.replace("\\", "").strip()


def parse_audit_metric_details(audit_text: str) -> dict[str, tuple[str, str, str]]:
    """Parse evaluation_audit blocks into (definition, reported_value, setting) tuples."""
    details: dict[str, tuple[str, str, str]] = {}
    blocks = re.split(r"\n\*\*", audit_text)
    for block in blocks:
        key_match = re.search(r"\[`([^`]+)`\]", block)
        if not key_match:
            continue
        key = key_match.group(1)
        if key in details:
            continue
        context_m = re.search(r"\*\*Context:\*\*\s*(.+)", block)
        metrics_m = re.search(r"\*\*Metrics Used:\*\*\s*(.+)", block)
        results_m = re.search(r"\*\*Reported Results:\*\*\s*(.+)", block)
        if not metrics_m:
            continue
        defn = _clean_audit_line(metrics_m.group(1).split("\n")[0])
        reported = _clean_audit_line(results_m.group(1).split("\n")[0]) if results_m else ""
        setting = _clean_audit_line(context_m.group(1).split("\n")[0]) if context_m else ""
        details[key] = (defn, reported, setting)
    return details


# Curated RL reward/return definitions and reported values (overrides audit parsing).
# Tuple: (how calculated, reported value/magnitude, evaluation setting).
RL_REWARD_DETAILS: dict[str, tuple[str, str, str]] = {
    "zhao2021dear": (
        "Session return R = Σ r_t with r_t = r_t^{ad} + α·r_t^{ex}; r_t^{ad} = ad-video revenue; r_t^{ex} = browse-continue UX signal.",
        "Offline mean R = 10.96 vs. HDQN 10.27, GRU 9.87, DeepFM 9.23, Wide&Deep 9.12 (p < 0.01); sensitivity also plots Rad (Σ r^{ad}) and Rex (Σ r^{ex}).",
        "Offline off-policy training on Douyin logs; evaluation via simulated online environment (Algorithm 2), not live A/B.",
    ),
    "zhao2020jointly": (
        "Two-level MDP: R^rs = session dwell time (rec list); R^as = session length; R^rev = session ad revenue; combined via level weights α, β.",
        "Simulated online env on TikTok logs: vs. RAM-l: dwell +0.61%, session length +0.83%, ad revenue +4.70% (all p < 0.01).",
        "Offline off-policy training + simulated online test (KDD 2020); no live A/B in source.",
    ),
    "wu2017returning": (
        "RL reward combines return rate, session length, and long-term engagement proxies for returning-user recommendation.",
        "Improves return rate and session-length metrics vs. baselines on logged recommender data (verify magnitudes in source).",
        "Offline recommender experiments.",
    ),
    "chen2022off": (
        "Discounted long-horizon return / value; Monte Carlo returns and critic targets for off-policy actor-critic on logged recommender trajectories.",
        "Higher offline long-horizon policy value vs. REINFORCE / full-trajectory IS; deployed on YouTube with long-term engagement gains (exact lifts not in audit).",
        "Offline logged YouTube data → production.",
    ),
    "cai2023two": (
        "Primary reward = WatchTime; constrained actor-critic with interaction constraints (Like, Comment, Share, Download).",
        "Offline WatchTime +2.23% vs. behavior cloning; online A/B: WatchTime +0.379%, Shares +3.376%, Downloads +1.733%.",
        "Offline + live A/B (short video).",
    ),
    "xu2023optimizing": (
        "On-policy TD learning optimizing long-term return tied to conversion outcomes in auction-based recommender (Meta).",
        "Online A/B: conversion count and rate +4–10% vs. base policy; total impressions neutral (supply guardrail).",
        "Online A/B (~billions of daily impressions).",
    ),
    "Mehrotra2020": (
        "Multi-objective contextual bandit; GGI scalarizes competing objectives (clicks, streams, supplier exposure).",
        "MO-LinCB vs. single-objective: +6.9%, +11.0%, +10.0% on three interaction metrics.",
        "Spotify production bandits.",
    ),
    "ie2019slateq": (
        "Slate LTV decomposed into item-wise LTVs under a click/choice model; episode reward = long-term engagement value of the slate.",
        "Simulations: higher CTR and average reward/episode vs. myopic baselines; validated in YouTube live experiments.",
        "Simulation + YouTube production validation.",
    ),
    "wu2018budget": (
        "DRLB bidding reward = value of acquired clicks under budget; R/R* = winning impression value / optimal value.",
        "Up to +100.92% vs. FLB; +4.3% acquired real clicks overall on offline RTB logs.",
        "Offline RTB replay.",
    ),
    "zou2019reinforcement": (
        "FeedRec: hierarchical LSTM Q-network with S-Network simulator; reward proxies = avg clicks/session, browsing depth, return time.",
        "Outperforms DDPG and baselines on all three engagement metrics (p < 0.01) on real-world dataset eval.",
        "Offline simulator + logged data.",
    ),
    "Theocharous-2015": (
        "RL optimizes estimated Life-Time Value (LTV) instead of myopic click reward.",
        "LTV-optimizing RL beats CTR-myopic policies under high-confidence off-policy evaluation (HCOPE) before deployment.",
        "Offline OPE → deployment.",
    ),
    "carrion2021blending": (
        "Virtual bids encode platform valuation of blended sponsored/organic outcomes; policy learns bid values in repeated auctions.",
        "Full JD.COM mobile deployment; tens of millions of auctions/day (exact scalar reward values not disclosed).",
        "Online production (JD.COM).",
    ),
    "foster2018contextual": (
        "Instantaneous reward = observed label (click/conversion); RegCB minimizes cumulative regret vs. regression oracle.",
        "RegCB within ~20% of best oracle performance; beats ε-greedy on regret across benchmark datasets.",
        "Offline contextual-bandit benchmarks.",
    ),
    "gauci2018horizon": (
        "Task-specific reward per Horizon application; policy value estimated with doubly robust offline evaluation before rollout.",
        "Task-dependent returns; workflow is offline DR screening → gated online A/B (verify per-task numbers in source).",
        "Offline DR → gated online A/B (Meta Horizon).",
    ),
    "wang2022surrogate": (
        "Immediate engagement sequences used as surrogate reward predicting long-term platform revisits in RL recommender.",
        "Surrogates predict 5-month revisit; live industrial experiments improved long-term UX (exact reward scale not quoted).",
        "Offline validation + live experiments.",
    ),
    "agarwal2020optimistic": (
        "Normalized episodic return on standard offline RL benchmark tasks.",
        "Optimistic/pessimistic offline RL methods improve normalized return vs. behavior cloning (task-specific scores).",
        "Offline RL benchmarks (D4RL-style; not ad/rec KPIs).",
    ),
    "deffayet2022offline": (
        "Cumulative return / policy value under sequential recommender RL vs. one-step offline protocols.",
        "Shows offline next-item metrics underestimate long-term RL policy value (simulation + empirical study).",
        "Offline RL-rec evaluation.",
    ),
    "ie2019recsim": (
        "Configurable simulated user-engagement / satisfaction reward in RecSim environments.",
        "Example environments report engagement-based rewards for comparing RL ranking policies.",
        "Simulator platform.",
    ),
    "ie2019reinforcement": (
        "Slate reward from choice-model decomposition over recommendation sets (SlateQ tractability).",
        "Methodology paper defining slate-level long-term value; verify reported magnitudes in source.",
        "Theoretical + slate simulations.",
    ),
    "burtini2015improving": (
        "Cumulative reward in drifting multi-armed bandit online marketing experiments.",
        "Bandit policies improve cumulative reward vs. static A/B allocations (verify exact lifts in source).",
        "Online marketing experiments.",
    ),
    "mnih2016asynchronous": (
        "Average score per Atari game episode (standard RL return).",
        "Superhuman scores on many Atari games (e.g., Breakout, Pong); not ad/rec KPIs.",
        "Atari simulator benchmarks.",
    ),
    "schulman2015trust": (
        "Average episodic return on continuous-control (MuJoCo) tasks.",
        "TRPO improves return vs. policy gradient baselines on locomotion tasks.",
        "MuJoCo benchmarks.",
    ),
    "schulman2017proximal": (
        "Average episodic return on continuous-control tasks.",
        "PPO matches or exceeds TRPO returns with simpler updates.",
        "MuJoCo / robotics benchmarks.",
    ),
    "van2016deep": (
        "Average Atari game score per episode.",
        "DQN human-level performance on many Atari games.",
        "Atari simulator.",
    ),
    "williams1992simple": (
        "Episodic return (total reward until failure) on pole-balancing benchmark.",
        "REINFORCE learns stable balancing policies (classic control demo).",
        "Toy control benchmark.",
    ),
    "dulac2019challenges": (
        "Normalized score on Real-World RL (RWRL) benchmark environments.",
        "Reports normalized return ranges across RWRL tasks; not ad/rec production KPIs.",
        "RWRL benchmark suite.",
    ),
    "dulac2021challenges": (
        "Normalized return on RWRL benchmark environments with analysis of real-world RL failure modes.",
        "Benchmark normalized returns; used for cross-task comparison, not monetization metrics.",
        "RWRL benchmarks.",
    ),
    "everitt2021reward": (
        "Reward defined on synthetic RL environments illustrating reward tampering / misspecification.",
        "Demonstrates pathological returns under tampered reward channels (illustrative, not industrial KPIs).",
        "Synthetic RL environments.",
    ),
    "vouros2022explainable": (
        "Reward on synthetic explainable-RL benchmark tasks cited in the survey.",
        "Example task returns for comparing interpretable RL methods.",
        "Synthetic XRL examples.",
    ),
    "kaelbling1998planning": (
        "Expected cumulative reward in POMDP planning benchmarks.",
        "Planning quality on classic POMDP domains (not ad/rec).",
        "POMDP planning benchmarks.",
    ),
    "mazoure2021improving": (
        "Long-term engagement / retention proxies as RL reward for recommender policies.",
        "Improves long-term engagement metrics vs. myopic baselines (verify exact definition in source).",
        "Offline + recommender experiments.",
    ),
    "mcdonald2023impatient": (
        "Delayed retention and long-term engagement folded into bandit/RL proxy reward.",
        "Proxy rewards tuned for impatient bandit evaluation of long-term value (verify magnitudes in source).",
        "Spotify-style long-term proxy evaluation.",
    ),
    "yi2023progressive": (
        "Progressive-horizon proxy reward approximating long-term engagement return.",
        "Proxy improves sensitivity to long-term effects vs. short-horizon rewards (verify values in source).",
        "Industrial recommender experiments.",
    ),
    "wen2019learning": (
        "Multi-objective reward vector learned jointly with user utility function in recommender RL.",
        "Learns reward weights aligning with user utility; verify reported online metrics in source.",
        "Recommender simulations / experiments.",
    ),
    "zhao2018deep": (
        "RTB/page-wise objective combines click cost, total clicks, and budget consumption in DeepPage DQN.",
        "Offline: Precision@20 0.0491, Recall@20 0.3576, NDCG@20 0.1872 vs. display baselines.",
        "Offline e-commerce / RTB logs.",
    ),
    "zhao2018recommendations": (
        "Reward incorporates negative feedback signals in RL recommender training.",
        "Improves ranking metrics (HR/NDCG) vs. baselines ignoring negative feedback (verify in source).",
        "Offline recommender experiments.",
    ),
    "afsar2022reinforcement": (
        "↺ Catalogues how surveyed RL-rec papers define reward/return (clicks, NDCG, dwell, etc.).",
        "No original experiments; synthesizes reward choices from prior work.",
        "Survey.",
    ),
    "lin2023survey": (
        "↺ Catalogues reward/return metrics used across surveyed RL recommender papers.",
        "No original experiments.",
        "Survey.",
    ),
}


def format_metric_detail_cell(defn: str, reported: str, setting: str = "") -> str:
    if not defn and not reported:
        return "—"
    parts: list[str] = []
    if defn:
        parts.append(f'<span class="metric-def"><strong>How:</strong> {html.escape(defn)}</span>')
    if reported:
        parts.append(f'<span class="metric-val"><strong>Value:</strong> {html.escape(reported)}</span>')
    if setting:
        parts.append(f'<span class="metric-set"><em>{html.escape(setting)}</em></span>')
    return "<br>".join(parts)


# Curated CTR / clicks definitions and reported values.
# Tuple: (how calculated, reported value/magnitude, evaluation setting).
CTR_CLICKS_DETAILS: dict[str, tuple[str, str, str]] = {
    "Zhou2018": (
        "pCTR = P(click | user, ad, context) from Deep Interest Network; aggregate CTR = clicks / impressions.",
        "Offline Alibaba dataset: improves AUC and log loss vs. baselines (exact AUC in paper; verify before quoting).",
        "Offline CTR prediction benchmark.",
    ),
    "Zhou2019": (
        "pCTR with interest evolution network; CTR = clicks / impressions at serving time.",
        "Offline AUC / log loss gains vs. DIN and other CTR baselines on production-scale data.",
        "Offline CTR prediction.",
    ),
    "Mehrotra2020": (
        "Clicks = user click on recommended track/item; one of three bandit objectives (with streams, supplier exposure), scalarized via GGI.",
        "MO-LinCB +6.9% on clicks objective vs. single-objective baselines (also +11.0%, +10.0% on other objectives).",
        "Spotify production contextual bandits.",
    ),
    "Theocharous-2015": (
        "Myopic CTR = clicks / ad impressions for greedy click-maximizing ad recommendation baseline.",
        "CTR-optimal policies underperform LTV-optimizing RL under HCOPE before deployment (directional; verify effect sizes).",
        "Offline OPE.",
    ),
    "yan2020ads": (
        "Engagement CTR and total clicks as guardrail metrics; revenue (REV/RPM) as primary objective in constrained feed ad allocation.",
        "Best algorithm balanced revenue and engagement; fully deployed on LinkedIn newsfeed (exact % lifts confidential).",
        "Online A/B → full production (LinkedIn).",
    ),
    "zhang2018whole": (
        "Click Yield = platform engagement proxy (click-based yield on whole Taobao page); optimized subject to threshold T.",
        "Online A/B: revenue increased while Click Yield stayed above satisfaction threshold T.",
        "Online A/B (Alibaba Taobao).",
    ),
    "sagtani2023quantifying": (
        "CTR = clicks / impressions; ACN = average click numbers per user; measured across feed refreshes.",
        "Online A/B: fatigue models yield 2–6% relative CTR and dwell improvements across refresh counts.",
        "Online A/B.",
    ),
    "sagtani2024ad": (
        "Ad Clicks = count of ad click events; also impressions and revenue in multi-objective ad-load policy.",
        "Online A/B (80M+ users): β=0.9 variant +0.52% ad clicks, +0.2% revenue, +0.22% time spent.",
        "Online A/B (Meta-scale feed).",
    ),
    "silberstein2020ad": (
        "CTR = clicks / ad impressions; ACR = ad close rate; revenue = total auction revenue (Yahoo Gemini GSP).",
        "Online: ad closes −20%+; revenue decrease capped at <0.4%.",
        "Online A/B (Gemini native).",
    ),
    "li2010contextual": (
        "Click = binary reward if user clicks recommended news article (contextual bandit on Yahoo! Front Page).",
        "LinUCB and related policies reduce cumulative regret vs. random; click-through rates reported on logged Yahoo data.",
        "Offline replay + Yahoo! live experiments.",
    ),
    "chapelle2011empirical": (
        "CTR = clicks / impressions on display ad slots; Thompson sampling selects ads to maximize click rate.",
        "Empirical study: Thompson sampling competitive with or better than UCB/greedy on multiple ad datasets.",
        "Offline / online ad experiments.",
    ),
    "chen2009large": (
        "CTR lift from behavioral targeting models predicting click probability at ad selection time.",
        "Reports measurable CTR improvements from large-scale behavioral targeting at Microsoft (verify exact % in source).",
        "Industrial online experiments.",
    ),
    "hohnhold2015focusing": (
        "User click propensity on search ads (related to per-impression click probability); LTRPM for long-term revenue.",
        "Long-term holdout justified 50% mobile ad-load reduction as revenue-neutral/long-term positive.",
        "Long-term holdout experiments (Google Search ads).",
    ),
    "koutsopoulos2016native": (
        "CTR = clicks / native ad impressions in social feed; revenue from allocated native ad slots.",
        "Optimization improves revenue and engagement vs. baselines on social feed data (verify magnitudes in source).",
        "Offline + social feed evaluation.",
    ),
    "covington2016deep": (
        "Candidate ranking uses predicted engagement probabilities including expected watch time and click-like engagement signals.",
        "Large-scale YouTube recommender; offline and live metrics improved vs. prior rankers (verify CTR component in source).",
        "Industrial YouTube ranking.",
    ),
    "wu2018budget": (
        "Acquired real clicks = count of won RTB auctions resulting in user clicks under budget constraint.",
        "+4.3% acquired real clicks overall vs. FLB/RLB baselines; up to +100.92% vs. FLB on R/R* metric.",
        "Offline RTB replay.",
    ),
    "ie2019slateq": (
        "CTR = clicks / recommended slate impressions under choice-model simulation.",
        "Simulations: higher CTR vs. myopic slate baselines; validated in YouTube live experiments.",
        "Simulation + YouTube production.",
    ),
    "zou2019reinforcement": (
        "Average clicks per session = total item clicks / sessions in FeedRec RL framework.",
        "Outperforms DDPG on clicks/session (p < 0.01) on real-world dataset evaluation.",
        "Offline simulator + logged data.",
    ),
    "zhao2018deep": (
        "Click cost, total clicks, and budget consumption in sponsored-search RTB; page-wise display strategy optimizes click yield under budget.",
        "Offline: Precision@20 0.0491, Recall@20 0.3576, NDCG@20 0.1872 vs. display baselines; click/budget metrics in RTB eval.",
        "Offline e-commerce / RTB logs.",
    ),
    "chakrabarti2008contextual": (
        "CTR = clicks / impressions; combines relevance scores with click feedback for contextual ad matching.",
        "Improves CTR and relevance vs. relevance-only or click-only baselines on ad datasets.",
        "Offline / experimental ad retrieval.",
    ),
    "gao2022bidding": (
        "Click and conversion outcomes from LinkedIn auto-bidding agent optimizing spend efficiency.",
        "Production bidding agent; ROI and click/conversion efficiency gains vs. prior strategies (verify in source).",
        "Industrial LinkedIn ads.",
    ),
    "tang2013ad": (
        "CTR = clicks / ad impressions for LinkedIn sponsored-update ad format selection.",
        "Format-selection policies improve CTR and revenue vs. static allocation in LinkedIn experiments.",
        "LinkedIn online experiments.",
    ),
    "schwartz2017customer": (
        "Clicks and conversions as bandit rewards for display-ad creative/customer selection.",
        "Bandit policies outperform uniform allocation on conversion efficiency (click-level rewards in bandit loop).",
        "Online display advertising experiments.",
    ),
    "yan2009much": (
        "CTR lift = relative change in click-through rate from behavioral targeting vs. control.",
        "Reports CTR and conversion lifts from large-scale behavioral targeting deployment.",
        "Industrial online experiments.",
    ),
    "zhang2024scaling": (
        "Ad CTR = ad clicks / ad impressions in Meta ads personalization stack.",
        "Online A/B: improved ad CTR and conversion rate vs. prior personalization (verify exact lifts in source).",
        "Online A/B (Meta ads).",
    ),
    "zhou2016latent": (
        "CTR = clicks / impressions; latent contextual bandit for unobserved user segments in ad targeting.",
        "Lower cumulative regret and improved CTR vs. LinUCB on synthetic and real ad datasets.",
        "Bandit benchmarks + ad data.",
    ),
    "mcmahan2013ad": (
        "pCTR = predicted click probability; trained with log loss / calibration at Google ad scale.",
        "Reported AUC and log-loss improvements on industrial CTR prediction (billions of examples).",
        "Industrial offline + online (Google ads).",
    ),
    "yuan2020unbiased": (
        "Position-aware debiased pCTR for ad ranking; CTR = clicks / impressions after position correction.",
        "Improves AUC and log loss vs. position-agnostic CTR models on ad click logs.",
        "Offline ad CTR prediction.",
    ),
    "cai2023two": (
        "Click = user click on recommended short video (auxiliary metric alongside primary WatchTime reward).",
        "Reported in offline/live eval tables; primary lift is WatchTime (+2.23% offline, +0.379% online).",
        "Offline + live A/B (short video).",
    ),
    "foster2018contextual": (
        "Instantaneous reward = observed click (or conversion label) on each round.",
        "RegCB regret within ~20% of oracle; click labels drive bandit updates across datasets.",
        "Offline contextual-bandit benchmarks.",
    ),
    "burtini2015improving": (
        "Click/conversion events as bandit rewards in drifting online marketing experiments.",
        "Drifting bandits improve cumulative click reward vs. static A/B (verify magnitudes in source).",
        "Online marketing experiments.",
    ),
    "cui2015global": (
        "Click yield and revenue in sponsored-search ad selection optimization.",
        "Global optimization improves revenue and click outcomes vs. greedy baselines.",
        "Sponsored search evaluation.",
    ),
    "pan2023learning": (
        "Implicit click-like engagement signals (likes, shares) and watch behavior on short-video feeds.",
        "Engagement model improves watch/implicit-feedback metrics vs. baselines (verify CTR-like metrics in source).",
        "Industrial short-video experiments.",
    ),
    "yi2014beyond": (
        "CTR = clicks / impressions alongside dwell time for personalized content ranking.",
        "Joint optimization improves CTR and dwell vs. CTR-only or dwell-only baselines.",
        "Online personalization experiments.",
    ),
    "wu2018beyond": (
        "Views and engagement rate (click-through to content) on online video platform.",
        "Improved engagement rate and watch metrics vs. prior rankers.",
        "Industrial online video.",
    ),
    "silberstein2023combating": (
        "CTR, CPM, conversion as ad fatigue feature evaluation metrics.",
        "Fatigue-aware models improve CTR/engagement while managing ad exposure (verify lifts in source).",
        "Industrial ad systems.",
    ),
    "zhao2021dear": (
        "Ad-side reward r_t^{ad} = revenue of the inserted ad video; ad features include platform predicted-CTR; W&D/DeepFM/GRU baselines add heads to predict ad CTR and whether to insert an ad.",
        "Table 2: session accumulated reward R = 10.96 vs. HDQN 10.27 (+6.7%, p=0.002); sensitivity analysis tracks Rad = Σ r^{ad} (ad revenue) and Rex = Σ r^{ex} separately vs. α.",
        "Simulated online environment on Douyin logs (Mar 2019); Table 2 reports session R on held-out sessions. No live A/B or deployment results in the AAAI paper.",
    ),
    "gauci2018horizon": (
        "CTR is reported as a task metric in Horizon's applied RL examples; policies are screened with counterfactual/off-policy estimators before controlled rollout.",
        "Task-dependent CTR and reward/value outcomes; use as production RL workflow evidence, not as an ad-specific benchmark.",
        "Offline DR / counterfactual evaluation plus gated online validation (Meta Horizon).",
    ),
    "carrion2021blending": (
        "Virtual bids encode platform valuation of sponsored clicks in blended sponsored/organic auctions on JD.COM.",
        "Full mobile deployment; tens of millions of auctions/day (exact click-valuation lifts not disclosed in audit).",
        "Online production (JD.COM).",
    ),
    "cui2015global": (
        "Click yield and revenue in sponsored-search ad selection; global optimization over click and revenue outcomes.",
        "Improves revenue and click yield vs. greedy baselines on commercial search-engine logs.",
        "Offline evaluation on commercial search-engine ad logs (no live A/B reported).",
    ),
    "van2024practical": (
        "Production CTR and revenue KPIs alongside cumulative regret in large-scale contextual bandit deployments.",
        "Industry perspective on balancing regret minimization with live CTR/revenue guardrails (no new experiments reported).",
        "Conceptual / practitioner WSDM perspective paper.",
    ),
    "cheng2016wide": (
        "pCTR / engagement prediction with Wide & Deep; aggregate CTR and online engagement at Google Play scale.",
        "Reported AUC and log-loss improvements plus online engagement gains vs. prior rankers.",
        "Industrial offline + online (Google Play).",
    ),
}


def metric_detail_for_key(
    key: str,
    fam_cells: dict[str, str],
    audit_details: dict[str, tuple[str, str, str]],
    manual_details: dict[str, tuple[str, str, str]],
    family_id: str,
    content_keywords: tuple[str, ...],
    placeholder_label: str,
    survey_label: str,
) -> str:
    if key in manual_details:
        defn, reported, setting = manual_details[key]
        return format_metric_detail_cell(defn, reported, setting)
    if key in audit_details:
        defn, reported, setting = audit_details[key]
        if fam_cells.get(family_id) or any(k in defn.lower() for k in content_keywords):
            return format_metric_detail_cell(defn, reported, setting)
    marker = fam_cells.get(family_id, "")
    if marker == "✓":
        return format_metric_detail_cell(
            f"Uses {placeholder_label}; definition not yet catalogued.",
            "Verify calculation and reported magnitudes in source.",
            "",
        )
    if marker == "↺":
        return format_metric_detail_cell(
            f"↺ Survey catalogues {survey_label} from prior papers.",
            "No original values.",
            "Survey.",
        )
    return "—"


def ctr_clicks_detail_for_key(
    key: str,
    fam_cells: dict[str, str],
    audit_details: dict[str, tuple[str, str, str]],
) -> str:
    ctr_kw = (
        "ctr", "click-through", "click through", "clicks", "pctr",
        "click yield", "total clicks", "acn", "click propensity", "acquired real clicks",
    )
    return metric_detail_for_key(
        key,
        fam_cells,
        audit_details,
        CTR_CLICKS_DETAILS,
        "ctr",
        ctr_kw,
        "CTR / clicks",
        "CTR and click metrics",
    )


def rl_reward_detail_for_key(
    key: str,
    fam_cells: dict[str, str],
    audit_details: dict[str, tuple[str, str, str]],
) -> str:
    reward_kw = ("reward", "return", "ggi", "ltv", "monte carlo", "cumulative", "episodic", "value")
    return metric_detail_for_key(
        key,
        fam_cells,
        audit_details,
        RL_REWARD_DETAILS,
        "rl",
        reward_kw,
        "RL reward/return",
        "RL reward/return definitions",
    )


# Backward-compatible alias
format_rl_detail_cell = format_metric_detail_cell


# Evaluation modality flags: (offline, simulation, online) per paper.
EVAL_MODALITY_COLS: list[tuple[str, str]] = [
    ("eval-off", "Offline eval"),
    ("eval-sim", "Simulation"),
    ("eval-on", "Online eval"),
]
EVAL_MODALITY_IDS = [c[0] for c in EVAL_MODALITY_COLS]

EVAL_MODALITY_FLAGS: dict[str, tuple[bool, bool, bool]] = {
    "zhao2021dear": (True, True, False),  # offline logs + simulated online env; no live A/B in AAAI paper
    "zhao2020jointly": (True, True, False),  # same TikTok logs + simulated online env as DEAR; no live A/B in KDD paper
    "zhang2018whole": (True, False, True),  # VERIFIED: offline replay of logged request stream (Sec 5.1) + online A/B on live Alibaba traffic (Sec 5.2)
    "yan2020ads": (True, True, True),  # offline replay (simulation-based) on logged feed sessions + online A/B + production
    "sagtani2024ad": (True, False, True),
    "chen2022off": (True, False, True),
    "gauci2018horizon": (True, True, True),  # VERIFIED: offline CPE on logged data + Gym/Gridworld simulators + real A/B (push notifications)
    "ie2019slateq": (False, True, True),
    "ie2019recsim": (False, True, False),
    "swaminathan2015counterfactual": (True, False, False),
    "dudik2011doubly": (True, False, False),
    "levine2020offline": (False, False, False),
    "bietti2021contextual": (True, False, False),
    "li2010contextual": (True, False, False),  # VERIFIED: offline replay via unbiased offline evaluator on logged random-bucket data; no live A/B of LinUCB
    "van2024practical": (False, False, False),  # industry perspective; no new empirical eval in 4-page WSDM paper
    "Mehrotra2020": (False, False, True),
    "xu2023optimizing": (False, False, True),
    "cai2023two": (True, False, True),
    "hohnhold2015focusing": (False, False, True),
    "wang2022surrogate": (True, False, True),
    "mcdonald2023spotify": (False, False, True),
    "yi2023progressive": (False, False, True),
    "Theocharous-2015": (True, False, False),
    "zhao2018deep": (True, False, False),
    "wu2018budget": (True, False, False),
    "carrion2021blending": (False, False, True),
    "silberstein2020ad": (False, False, True),
    "sagtani2023quantifying": (False, False, True),
    "zou2019reinforcement": (True, True, False),
    "barajas2022online": (False, False, True),
    "foster2018contextual": (True, False, False),
    "deffayet2022offline": (True, False, False),
    "agarwal2020optimistic": (True, False, False),
    "Kang2018": (True, False, False),
    "kang2018sasrec": (True, False, False),
    "Zhou2018": (True, False, True),  # DIN: offline AUC + online A/B (CTR/RPM lift) at Alibaba display ads
    "Zhou2019": (True, False, True),  # DIEN: offline AUC + online A/B (CTR lift) at Alibaba display ads
    "mcmahan2013ad": (True, False, True),
    "covington2016deep": (True, False, True),
    "cheng2016wide": (True, False, True),
    "pancha2022pinnerformer": (True, False, True),  # offline retrieval metrics + online A/B at Pinterest
    "xia2023transact": (True, False, True),  # offline engagement-prediction experiments + online A/B at Pinterest
    "zhang2024scaling": (True, False, True),  # VERIFIED: offline NE results (Sec 6.2) + online A/B (Sec 6.3, +2.67%) at Meta
    "gao2022bidding": (False, False, True),
    "liu2022monolith": (True, False, True),  # VERIFIED: offline AUC on MovieLens ml-25m + Criteo Display Ads + live A/B on production ads model
    "pan2023learning": (False, False, True),
    "vorotilov2023scaling": (True, False, True),  # VERIFIED (eng blog): offline metrics / offline tuning + online engagement experiments
    "grbovic2018real": (True, False, True),
    "schwartz2017customer": (False, False, True),
    "tang2013ad": (False, False, True),
    "chen2009large": (False, False, True),
    "yan2009much": (False, False, True),
    "chapelle2011empirical": (True, True, False),  # VERIFIED: simulations (Bernoulli + simulated-click display ads) + offline replay (news rec); no live A/B
    "chakrabarti2008contextual": (True, False, False),
    "koutsopoulos2016native": (True, False, False),
    "lu2016partially": (False, True, False),
    "ie2019reinforcement": (False, True, False),
    "zhao2018recommendations": (True, False, False),
    "mazoure2021improving": (True, False, False),
    "mcdonald2023impatient": (False, False, True),
    "wen2019learning": (True, True, False),
    "wu2017returning": (True, False, False),
    "wu2018beyond": (False, False, True),
    "yi2014beyond": (False, False, True),
    "yuan2020unbiased": (True, False, False),
    "naumov2019deep": (True, False, False),
    "zhou2016latent": (True, False, False),
    "burtini2015improving": (False, False, True),
    "agarwal2019online": (False, False, True),
    "agarwal2014budget": (False, False, True),
    "agarwal2014taming": (True, False, False),
    "auer2002finite": (False, True, False),  # VERIFIED: Section 4 experiments on simulated Bernoulli bandit distributions; not logged-data replay
    "schulman2015trust": (False, True, False),
    "schulman2017proximal": (False, True, False),
    "mnih2016asynchronous": (False, True, False),
    "van2016deep": (False, True, False),
    "williams1992simple": (False, True, False),
    "dulac2019challenges": (False, True, False),
    "dulac2021challenges": (False, True, False),
    "everitt2021reward": (False, True, False),
    "vouros2022explainable": (False, True, False),
    "kaelbling1998planning": (False, True, False),
    # Explicit flags for cited papers not covered above (surveys, textbooks, edge cases).
    "Jannach2023": (False, False, False),
    "Sutton1998": (False, False, False),
    "abrams2007personalized": (True, False, False),
    "acmauthoryear": (False, False, False),
    "afsar2022reinforcement": (False, False, False),
    "agarwal2016statistical": (False, False, False),
    "bubeck2012regret": (False, False, False),
    "ccelik2023ad": (False, False, False),
    "cui2015global": (True, False, False),  # commercial search-engine logs; no live A/B reported
    "dimitrakakis2018decision": (False, False, False),
    "ellam2003overture": (False, False, False),
    "engel2008incorporating": (False, True, False),  # VERIFIED: Sec 5 simulation experiments on real Microsoft Live Search bid data (470 queries, 2557 bids); no offline replay or live A/B
    "fain2006sponsored": (False, False, False),
    "gama2014survey": (False, False, False),
    "glanois2024survey": (False, False, False),
    "hu2004performance": (False, False, False),
    "kaelbling1996reinforcement": (False, False, False),
    "kant2021history": (False, False, False),
    "kuleshov2014algorithms": (False, False, False),
    "lambert2023entangled": (False, False, False),
    "lin2023survey": (False, False, False),
    "nielsen2017advertising": (False, False, True),  # controlled advertising field experiments
    "puterman2014markov": (False, False, False),
    "robbins1952sequential": (True, False, False),
    "russell2016artificial": (False, False, False),
    "russo2018tutorial": (False, False, False),
    "saha2021advertiming": (False, False, True),  # large-scale social-media ad consumption study
    "shahriari2015taking": (False, False, False),
    "silberstein2023combating": (True, False, True),  # offline feature eval + online A/B at Meta
    "vaswani2017attention": (False, False, False),
    "wikipedia-cpm": (False, False, False),
    "wsj2003yahoooverture": (False, False, False),
    "zhao2024survey": (False, False, False),
    "zhu2021overview": (False, False, False),
}


def parse_audit_eval_modalities(audit_text: str) -> dict[str, tuple[bool, bool, bool]]:
    """Parse evaluation modality from the audit inventory table."""
    out: dict[str, tuple[bool, bool, bool]] = {}
    for line in audit_text.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4:
            continue
        key_cell = cells[1]
        mod_cell = cells[2]
        keys_found = re.findall(r"`([^`]+)`", key_cell)
        if not keys_found or mod_cell.lower().startswith("evaluation modality"):
            continue
        flags = classify_eval_modality_flags(mod_cell)
        for key in keys_found:
            if key not in out:
                out[key] = flags
    return out


def classify_eval_modality_flags(text: str) -> tuple[bool, bool, bool]:
    """Return (offline, simulation, online) flags from free-text modality description."""
    t = text.lower()
    offline = any(
        k in t
        for k in (
            "offline", "logged", "replay", "off-policy", "off policy",
            "ope", "counterfactual", "doubly robust", "ips",
            "offline experiment", "offline eval", "benchmark dataset",
            "offline training", "offline actor", "offline rl",
            "offline replay", "offline next-item", "offline policy",
            "hcope", "off-policy learning",
        )
    )
    online = any(
        k in t
        for k in (
            "online", "a/b", "a/b test", "live experiment", "production deployment",
            "deployed", "holdout", "live a", "industrial evaluation",
            "production or industrial", "online learning", "geo-testing",
            "live production", "live validation", "live experiments",
        )
    )
    sim = any(
        k in t
        for k in (
            "simulator", "simulation", "simulated", "recsim", "slate model",
            "mujoco", "atari", "rwrl", "benchmark environment", "s-network",
            "simulated online",
        )
    )
    return offline, sim, online


def modality_flags_from_detail_settings(key: str) -> tuple[bool, bool, bool] | None:
    """Infer modality flags from CTR/RL detail setting strings."""
    settings: list[str] = []
    for details in (CTR_CLICKS_DETAILS, RL_REWARD_DETAILS):
        if key in details:
            settings.append(details[key][2])
    if not settings:
        return None
    return classify_eval_modality_flags(" ".join(settings))


def eval_modality_cells_for_key(
    key: str,
    reports: str,
    audit_modalities: dict[str, tuple[bool, bool, bool]],
) -> dict[str, str]:
    """Return eval-off / eval-sim / eval-on cell markers (✓ or empty)."""
    if key in EVAL_MODALITY_FLAGS:
        off, sim, on = EVAL_MODALITY_FLAGS[key]
    elif reports in ("❌ No", "⚠️ Partial"):
        # Surveys and non-empirical sources should not inherit modality from audit prose.
        off, sim, on = False, False, False
    elif key in audit_modalities:
        off, sim, on = audit_modalities[key]
    elif (from_details := modality_flags_from_detail_settings(key)):
        off, sim, on = from_details
    else:
        off, sim, on = False, False, False

    col_ids = ("eval-off", "eval-sim", "eval-on")
    flags = (off, sim, on)
    return {cid: ("✓" if flag else "") for cid, flag in zip(col_ids, flags)}


def eval_modality_marker(cell: str) -> str:
    """Map ✓/empty to filter attribute check/empty."""
    return "check" if cell == "✓" else "empty"


# Color buckets for the eval-modality citation chart (id, legend label, hex color).
EVAL_MODALITY_BUCKET_META: list[tuple[str, str, str]] = [
    ("offline-only", "Offline only", "#2563eb"),
    ("online-only", "Online only", "#059669"),
    ("offline-online", "Offline + online only", "#0891b2"),
    ("offline-sim", "Offline + simulation only", "#7c3aed"),
    ("offline-sim-online", "Offline + simulation + online", "#dc2626"),
    ("other-combo", "Other combination", "#f59e0b"),
    ("none", "None / not catalogued", "#94a3b8"),
]
EVAL_MODALITY_BUCKET_LABELS = {bid: label for bid, label, _c in EVAL_MODALITY_BUCKET_META}
EVAL_MODALITY_BUCKET_COLORS = {bid: color for bid, _label, color in EVAL_MODALITY_BUCKET_META}


def eval_modality_flags_from_cells(cells: dict[str, str]) -> tuple[bool, bool, bool]:
    return (
        cells.get("eval-off") == "✓",
        cells.get("eval-sim") == "✓",
        cells.get("eval-on") == "✓",
    )


def eval_modality_bucket_from_cells(cells: dict[str, str]) -> str:
    """Map offline/sim/online flags to a color-bucket id for plotting."""
    off, sim, on = eval_modality_flags_from_cells(cells)
    if off and not sim and not on:
        return "offline-only"
    if not off and not sim and on:
        return "online-only"
    if off and not sim and on:
        return "offline-online"
    if off and sim and not on:
        return "offline-sim"
    if off and sim and on:
        return "offline-sim-online"
    if not off and not sim and not on:
        return "none"
    return "other-combo"


MANUAL_METRICS: dict[str, str] = {
    "Jannach2023": "N/A (survey; synthesizes multi-objective metrics from prior work)",
    "Kang2018": "HR@K, NDCG@K",
    "Sutton1998": "N/A (textbook)",
    "Zhou2018": "AUC, log loss (CTR prediction)",
    "Zhou2019": "AUC, log loss (CTR prediction)",
    "abrams2007personalized": "Revenue, user satisfaction / ad fatigue (optimization objective)",
    "acmauthoryear": "N/A (ACM natbib style alias)",
    "afsar2022reinforcement": "Catalogues Recall, Hit Ratio, NDCG, reward across surveyed RL-rec papers",
    "agarwal2014budget": "Budget utilization, pacing error, spend delivery",
    "agarwal2014taming": "Cumulative regret",
    "agarwal2016statistical": "N/A (methods textbook)",
    "agarwal2019online": "Regret, parameter-selection performance",
    "agarwal2020optimistic": "Normalized return on offline RL benchmarks (e.g., D4RL-style tasks)",
    "auer2002finite": "Cumulative regret (theoretical + empirical bandit benchmarks)",
    "bubeck2012regret": "Regret bounds (theory survey; references empirical regret)",
    "burtini2015improving": "Cumulative reward / regret in online marketing experiments",
    "ccelik2023ad": "N/A (systematic literature review)",
    "chakrabarti2008contextual": "CTR, relevance, click feedback",
    "chapelle2011empirical": "Cumulative regret, CTR (display ads)",
    "chen2009large": "CTR lift, conversion-related outcomes",
    "cheng2016wide": "AUC, log loss, online engagement",
    "covington2016deep": "Watch time, CTR, session metrics (YouTube)",
    "cui2015global": "Revenue, click yield (sponsored search)",
    "deffayet2022offline": "Hit Ratio, NDCG, offline policy value (RL-rec evaluation study)",
    "dimitrakakis2018decision": "N/A (decision-making survey)",
    "dulac2019challenges": "Normalized score on Real-World RL benchmark environments",
    "dulac2021challenges": "Normalized return on RWRL benchmark suite",
    "ellam2003overture": "Auction/pricing case metrics (historical industry analysis)",
    "engel2008incorporating": "Advertiser utility, revenue, welfare (sponsored-search auctions)",
    "everitt2021reward": "Reward on synthetic RL environments (reward tampering study)",
    "fain2006sponsored": "N/A (historical overview)",
    "gama2014survey": "N/A (concept-drift survey)",
    "gao2022bidding": "ROI, spend efficiency, click/conversion outcomes (LinkedIn bidding)",
    "gauci2018horizon": "CTR, task-specific reward, policy value (doubly robust offline evaluation)",
    "glanois2024survey": "N/A (interpretable RL survey)",
    "grbovic2018real": "Booking conversion, search ranking quality (Airbnb)",
    "hu2004performance": "Pricing-model performance (CPM/CPC/CPA analysis)",
    "ie2019recsim": "Simulated user engagement, reward, diversity (simulator platform)",
    "ie2019reinforcement": "Slate reward, choice-model fit, long-term value (methodology paper)",
    "kaelbling1996reinforcement": "N/A (RL survey)",
    "kaelbling1998planning": "POMDP planning benchmarks",
    "kang2018sasrec": "HR@K, NDCG@K",
    "kant2021history": "N/A (historical essay)",
    "koutsopoulos2016native": "Revenue, engagement, CTR (native ad allocation)",
    "kuleshov2014algorithms": "Regret (bandit algorithms survey)",
    "lambert2023entangled": "N/A (history/commentary)",
    "levine2020offline": "Discusses normalized return / OPE metrics; no original ad-rec experiments",
    "li2010contextual": "CTR, cumulative regret (news recommendation)",
    "lin2023survey": "Catalogues Recall, Hit Ratio, NDCG across surveyed RL-rec papers",
    "liu2022monolith": "Online A/B conversion and engagement metrics (industrial DLRM)",
    "lu2016partially": "Hit Ratio, NDCG (POMDP recommender simulations)",
    "mazoure2021improving": "Long-term engagement, retention proxies",
    "mcdonald2023impatient": "Retention, long-term reward, recommendation quality",
    "mcmahan2013ad": "Log loss, AUC, calibration (CTR prediction at scale)",
    "mnih2016asynchronous": "Average game score (Atari)",
    "naumov2019deep": "AUC, log loss (DLRM recommendation)",
    "nielsen2017advertising": "N/A (brand recall / advertising effectiveness metrics outside configured ad-rec/RL metric families)",
    "pan2023learning": "Watch time, implicit negative-feedback engagement (short video)",
    "pancha2022pinnerformer": "HR@K, NDCG@K (Pinterest online)",
    "puterman2014markov": "N/A (MDP textbook)",
    "robbins1952sequential": "Regret / design-of-experiments (foundational theory)",
    "russell2016artificial": "N/A (AI textbook)",
    "russo2018tutorial": "Catalogues cumulative regret for Thompson-sampling and bandit evaluation; tutorial, not original industrial KPIs",
    "saha2021advertiming": "Ad consumption timing, engagement, allocation outcomes",
    "schulman2015trust": "Average episodic return (MuJoCo / robotics benchmarks)",
    "schulman2017proximal": "Average episodic return (continuous-control benchmarks)",
    "schwartz2017customer": "Conversion rate, customer-acquisition cost (display-ad bandits)",
    "shahriari2015taking": "N/A (Bayesian optimization review)",
    "silberstein2023combating": "CTR, CPM, conversion (ad fatigue features)",
    "tang2013ad": "CTR, revenue (LinkedIn ad format selection)",
    "van2016deep": "Average game score (Atari)",
    "van2024practical": "Regret, production KPIs (industry bandit perspective)",
    "vaswani2017attention": "N/A (BLEU / perplexity metrics outside configured ad-rec/RL metric families)",
    "vorotilov2023scaling": "Engagement, session metrics (Instagram Explore)",
    "vouros2022explainable": "Synthetic RL task reward (XRL survey with examples)",
    "wen2019learning": "Multi-objective reward components, user utility",
    "wikipedia-cpm": "N/A (CPM definition)",
    "williams1992simple": "Episodic return (pole-balancing benchmark)",
    "wsj2003yahoooverture": "N/A (news article)",
    "wu2017returning": "Return rate, session length, long-term engagement",
    "wu2018beyond": "Engagement rate, watch time, views (online video)",
    "xia2023transact": "HR@K, NDCG@K, online engagement (Pinterest)",
    "yan2009much": "CTR lift, conversion (behavioral targeting)",
    "yi2014beyond": "Dwell time, CTR (personalization)",
    "yi2023progressive": "Long-term engagement, progressive-horizon proxy metrics",
    "yuan2020unbiased": "AUC, log loss (position-aware ad CTR)",
    "zhao2018deep": "Click cost, total clicks, budget consumption (sponsored-search RTB)",
    "zhao2018recommendations": "HR@K, NDCG@K (negative-feedback RL rec)",
    "zhao2024survey": "N/A (retrieval survey)",
    "zhang2024scaling": "Ad CTR, conversion rate, online A/B engagement (Meta ads personalization)",
    "zhou2016latent": "CTR, cumulative regret (latent contextual bandits)",
    "zhu2021overview": "N/A (action-space overview; no primary experiments)",
}


def infer_families_from_text(text: str) -> set[str]:
    """Keyword-based family assignment from free-text metrics description."""
    if not text or text.startswith("N/A") or text.startswith("Discusses"):
        return set()

    t = text.lower()
    fams: set[str] = set()

    ctr_kw = [
        "ctr", "click-through", "click through", "clicks", "pctr",
        "click yield", "total clicks", "acquired real clicks", "acn",
    ]
    if any(k in t for k in ctr_kw):
        fams.add("ctr")

    auc_kw = ["auc", "log loss", "logloss", "calibration"]
    if any(k in t for k in auc_kw):
        fams.add("auc")
    # Avoid matching "auc" inside "auction".
    if fams.intersection({"auc"}) and "auction" in t and not re.search(r"\bauc\b", t):
        fams.discard("auc")

    cvr_kw = [
        "conversion", "cvr", "booking conversion", "cpic", "roas",
        "incremental roas",
    ]
    if any(k in t for k in cvr_kw):
        fams.add("cvr")

    rev_kw = [
        "revenue", "rpm", "ltrpm", "cpm", "roi", "monetization",
        "virtual bid", "spend", "budget", "rev/", "ad revenue",
    ]
    if any(k in t for k in rev_kw):
        fams.add("rev")

    rank_kw = [
        "ndcg", "hr@", "hr@k", "hit ratio", "recall@", "precision@",
        "map ", "f1-score", "precision",
    ]
    if any(k in t for k in rank_kw):
        fams.add("rank")
    # Avoid matching ranking "recall" inside "brand recall".
    if fams.intersection({"rank"}) and "brand recall" in t and "recall@" not in t and "ndcg" not in t:
        fams.discard("rank")

    dwell_kw = [
        "dwell", "watch time", "watchtime", "session length",
        "browsing depth", "session dwell", "time spent", "views",
        "session metrics", "engagement depth", "video plays",
    ]
    if any(k in t for k in dwell_kw):
        fams.add("dwell")

    ltv_kw = [
        "retention", "ltv", "life-time", "lifetime", "return rate",
        "return time", "time-to-inactivity", "churn", "survival",
        "repeat visit", "revisiting", "long-term engagement",
        "long-term value", "long-horizon",
    ]
    if any(k in t for k in ltv_kw):
        fams.add("ltv")

    regret_kw = [
        "regret", "pv loss", "progressive validation", "win-loss",
        "hamming loss", "normalized relative loss",
    ]
    if any(k in t for k in regret_kw):
        fams.add("regret")

    rl_kw = [
        "reward", "return", "normalized return", "policy value",
        "monte carlo", "critic", "game score", "episodic",
        "accumulated reward", "ggi", "streams",
    ]
    if any(k in t for k in rl_kw):
        fams.add("rl")

    ope_kw = [
        "rmse", "bias", "standard deviation", "ips", "doubly robust",
        "counterfactual", "propensity score", "offline policy", "ope",
        "importance", "hcope",
    ]
    if any(k in t for k in ope_kw):
        fams.add("ope")
    # "Click propensity" is an engagement metric, not an OPE propensity model.
    if fams.intersection({"ope"}) and "click propensity" in t and "propensity score" not in t:
        fams.discard("ope")

    adux_kw = [
        "ad load", "ad close", "acr", "fatigue", "incrementality",
        "lift", "pacing", "ad consumption", "click propensity",
        "user satisfaction", "arn", "refresh", "total impressions",
        "impressions neutral", "impression cap", "ad impressions",
    ]
    if any(k in t for k in adux_kw):
        fams.add("adux")
    # RTB "winning impression value" is a bidding metric, not ad-load UX.
    if fams.intersection({"adux"}) and re.search(
        r"\b(?:winning|optimal)\s+impression|\bimpression value\b", t
    ):
        fams.discard("adux")

    return fams


def families_for_key(key: str, metrics_text: str, title: str, partial: bool) -> dict[str, str]:
    """
    Return mapping family_id -> cell marker.
    ✓ = paper reports this metric family empirically
    ↺ = survey/catalogue only (partial)
    · = empty
    """
    if key in KEY_FAMILIES:
        fams = KEY_FAMILIES[key]
    else:
        combined = f"{metrics_text} {title}"
        fams = infer_families_from_text(combined)

    marker = "↺" if partial else "✓"
    return {fid: (marker if fid in fams else "") for fid in FAMILY_IDS}


def classify_reports_metrics(
    key: str, title: str, entry_type: str, metrics: str, audit_keys: set[str]
) -> str:
    if metrics.startswith("N/A"):
        return "❌ No"
    if key in audit_keys and key not in MANUAL_METRICS:
        return "✅ Yes"
    if any(w in title.lower() for w in ["survey", "review", "history", "tutorial", "overview"]):
        if "catalogues" in metrics.lower():
            return "⚠️ Partial"
        return "❌ No"
    if entry_type == "book" or key.lower() == "sutton1998":
        return "❌ No"
    if metrics.startswith("Discusses") or metrics.startswith("Catalogues"):
        return "⚠️ Partial"
    return "✅ Yes"


def notes_for(key: str, metrics: str, reports: str, audit_keys: set[str]) -> str:
    if key in audit_keys and key not in MANUAL_METRICS:
        return "Verified in evaluation_audit.md"
    if reports == "❌ No":
        if metrics.startswith("N/A") and "outside configured" in metrics:
            return metrics
        return "No empirical metrics reported"
    if reports == "⚠️ Partial":
        return "Synthesizes metrics from other papers"
    return "Inferred; verify in source"


def metric_val(cell: str) -> str:
    """Normalize cell marker for data attributes and filtering."""
    if cell == "✓":
        return "check"
    if cell == "↺":
        return "survey"
    return "empty"


def reports_val(reports: str) -> str:
    if reports == "✅ Yes":
        return "yes"
    if reports == "⚠️ Partial":
        return "partial"
    return "no"


def render_matrix_table_rows(rows: list) -> tuple[str, int]:
    """Return matrix table HTML and total min table width."""
    col_widths = {
        "num": "56px",
        "cite-count": "72px",
        "key": "260px",
        "title": "480px",
        "affiliation": "240px",
        "reports": "100px",
        **{eid: "110px" for eid in EVAL_MODALITY_IDS},
        **{fid: "130px" for fid in FAMILY_IDS},
        "ctr-detail": "420px",
        "rl-detail": "420px",
        "notes": "240px",
    }

    def _filter_menu_inner(col_id: str, kind: str) -> str:
        """Per-kind body for a column's filter dropdown."""
        if kind in ("marker", "enum"):
            if kind == "enum":
                opts = [
                    ("yes", "✅ Yes"),
                    ("partial", "⚠️ Partial"),
                    ("no", "❌ No"),
                ]
            else:
                opts = [("check", "✓ Yes")]
                if col_id in FAMILY_IDS:
                    opts.append(("survey", "↺ Survey"))
                opts.append(("empty", "— No"))
            return "".join(
                f'<label><input type="checkbox" checked data-val="{val}"> {html.escape(text)}</label>'
                for val, text in opts
            )
        if kind == "number":
            return (
                '<div class="filter-num">'
                '<label>Min <input type="number" class="filter-min" step="any"></label>'
                '<label>Max <input type="number" class="filter-max" step="any"></label>'
                "</div>"
            )
        # text
        return (
            '<input type="search" class="filter-text" '
            'placeholder="Contains\u2026" aria-label="Filter text">'
        )

    def th(col_id: str, label: str, kind: str, *, center: bool = False) -> str:
        cls_parts = ["sortable-col"]
        if center:
            cls_parts.append("center")
        if kind == "marker":
            cls_parts.append("metric-col")
        cls = f' class="{" ".join(cls_parts)}"'
        menu_inner = _filter_menu_inner(col_id, kind)
        return (
            f'<th{cls} data-col="{col_id}" data-kind="{kind}">'
            f'<div class="th-inner">'
            f'<span class="th-label sort-btn" data-col="{col_id}" role="button" '
            f'tabindex="0" title="Sort column">'
            f'{html.escape(label)}<span class="sort-ind" aria-hidden="true"></span>'
            f"</span>"
            f'<button type="button" class="filter-btn" data-col="{col_id}" '
            f'aria-label="Filter {html.escape(label)}" title="Filter column">▾</button>'
            f"</div>"
            f'<div class="filter-menu" data-col="{col_id}" data-kind="{kind}" hidden>'
            f"{menu_inner}"
            f'<div class="filter-menu-actions">'
            f'<button type="button" class="filter-apply">Apply</button>'
            f'<button type="button" class="filter-clear">Clear</button>'
            f"</div></div></th>"
        )

    def td(col_id: str, content: str, *, center: bool = False, metric: bool = False, val: str = "") -> str:
        cls_parts = []
        if center:
            cls_parts.append("center")
        if metric:
            cls_parts.append("metric-col")
        cls = f' class="{" ".join(cls_parts)}"' if cls_parts else ""
        extra = f' data-metric-val="{val}"' if metric else ""
        return f'<td{cls} data-col="{col_id}"{extra}>{content}</td>'

    column_kinds: dict[str, str] = {
        "num": "number",
        "cite-count": "number",
        "key": "text",
        "title": "text",
        "affiliation": "text",
        "reports": "enum",
        **{eid: "marker" for eid in EVAL_MODALITY_IDS},
        **{fid: "marker" for fid in FAMILY_IDS},
        "ctr-detail": "text",
        "rl-detail": "text",
        "notes": "text",
    }

    header = (
        "<tr>"
        + th("num", "#", "number", center=True)
        + th("cite-count", "Cites", "number", center=True)
        + th("key", "Citation Key", "text")
        + th("title", "Title", "text")
        + th("affiliation", "Affiliation", "text")
        + th("reports", "Reports?", "enum", center=True)
        + "".join(
            th(eid, label, "marker", center=True)
            for eid, label in EVAL_MODALITY_COLS
        )
        + "".join(th(fid, label, "marker", center=True) for fid, label in METRIC_FAMILIES)
        + th("ctr-detail", "CTR / clicks (how & value)", "text")
        + th("rl-detail", "RL reward / return (how & value)", "text")
        + th("notes", "Notes", "text")
        + "</tr>"
    )

    body_rows = []
    for i, key, title, pdf_url, affiliation, reports, fam_cells, notes, _metrics, ctr_detail, rl_detail, eval_cells, cite_count in rows:
        eval_tds = "".join(
            td(
                eid,
                html.escape(eval_cells[eid] or "—"),
                center=True,
                metric=True,
                val=eval_modality_marker(eval_cells[eid]),
            )
            for eid in EVAL_MODALITY_IDS
        )
        fam_tds = "".join(
            td(
                fid,
                html.escape(fam_cells[fid] or "—"),
                center=True,
                metric=True,
                val=metric_val(fam_cells[fid] or ""),
            )
            for fid in FAMILY_IDS
        )
        has_any = any(fam_cells[fid] for fid in FAMILY_IDS)
        has_check = any(fam_cells[fid] == "✓" for fid in FAMILY_IDS)
        data_attrs = (
            f' data-reports="{reports_val(reports)}"'
            f' data-has-any-metric="{"1" if has_any else "0"}"'
            f' data-has-empirical="{"1" if has_check else "0"}"'
            f' data-search="{html.escape(f"{key} {title} {affiliation}".lower())}"'
        )
        for fid in FAMILY_IDS:
            data_attrs += f' data-m-{fid}="{metric_val(fam_cells[fid] or "")}"'
        for eid in EVAL_MODALITY_IDS:
            data_attrs += f' data-m-{eid}="{eval_modality_marker(eval_cells[eid])}"'
        has_ctr_detail = "0" if ctr_detail == "—" else "1"
        has_rl_detail = "0" if rl_detail == "—" else "1"
        data_attrs += f' data-has-ctr-detail="{has_ctr_detail}"'
        data_attrs += f' data-has-rl-detail="{has_rl_detail}"'
        body_rows.append(
            f"<tr{data_attrs}>"
            + td("num", str(i), center=True)
            + td("cite-count", str(cite_count), center=True)
            + td("key", f"<code>{html.escape(key)}</code>")
            + td("title", format_title_cell(title, pdf_url))
            + td("affiliation", html.escape(affiliation))
            + td("reports", html.escape(reports), center=True)
            + eval_tds
            + fam_tds
            + f'<td class="metric-detail ctr-detail" data-col="ctr-detail">{ctr_detail}</td>'
            + f'<td class="metric-detail rl-detail" data-col="rl-detail">{rl_detail}</td>'
            + td("notes", html.escape(notes))
            + "</tr>"
        )

    total_min = sum(int(v.replace("px", "")) for v in col_widths.values())
    kinds_json = json.dumps(column_kinds, ensure_ascii=False).replace("<", "\\u003c")
    table = (
        f'<table id="citation-matrix" class="matrix" style="min-width:{total_min}px">\n'
        f"<thead>\n{header}\n</thead>\n"
        f"<tbody>\n" + "\n".join(body_rows) + "\n</tbody>\n</table>\n"
        f'<script type="application/json" id="column-kinds">{kinds_json}</script>'
    )
    return table, total_min


def _json_script_payload(obj) -> str:
    """JSON safe to embed in a <script type=\"application/json\"> tag."""
    return json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")


def render_filter_toolbar() -> str:
    """Toolbar: search, row presets, column visibility, metric row filter."""
    metric_toggles = "".join(
        f'<label class="col-toggle">'
        f'<input type="checkbox" class="col-show" data-col="{fid}" checked>'
        f" {html.escape(label)}"
        f"</label>"
        for fid, label in METRIC_FAMILIES
    )
    metric_require = "".join(
        f'<label class="metric-require">'
        f'<input type="checkbox" class="row-require" data-col="{fid}">'
        f" {html.escape(label)}"
        f"</label>"
        for fid, label in METRIC_FAMILIES
    )
    family_ids_json = _json_script_payload(FAMILY_IDS)
    eval_modality_ids_json = _json_script_payload(EVAL_MODALITY_IDS)
    return f"""
<div id="matrix-filters" class="filter-toolbar">
  <div class="filter-row">
    <label class="filter-field">
      <span>Search</span>
      <input type="search" id="filter-search" placeholder="Citation key, title, or affiliation…">
    </label>
    <label class="filter-field">
      <span>Row preset</span>
      <select id="filter-preset">
        <option value="all">All papers</option>
        <option value="empirical">Reports empirical metrics (✅)</option>
        <option value="any-metric">Has any metric marked (✓ or ↺)</option>
        <option value="empirical-mark">Has ✓ in any column</option>
        <option value="ctr-detail">Has CTR / clicks detail catalogued</option>
        <option value="rl-detail">Has RL reward detail catalogued</option>
        <option value="eval-off">Reports offline evaluation (✓)</option>
        <option value="eval-sim">Reports simulation evaluation (✓)</option>
        <option value="eval-on">Reports online evaluation (✓)</option>
        <option value="require-selected">Must match selected metrics below</option>
      </select>
    </label>
    <label class="filter-field">
      <span>Match mode</span>
      <select id="filter-match">
        <option value="any">Any selected metric</option>
        <option value="all">All selected metrics</option>
      </select>
    </label>
    <span id="filter-count" class="filter-count"></span>
  </div>
  <details class="filter-panel" open>
    <summary>Column visibility</summary>
    <div class="filter-actions">
      <button type="button" id="cols-show-all">Show all</button>
      <button type="button" id="cols-hide-empty">Hide empty columns</button>
      <button type="button" id="cols-metrics-only">Metrics only (hide #, Notes)</button>
    </div>
    <div class="col-toggles">{metric_toggles}</div>
  </details>
  <details class="filter-panel">
    <summary>Filter rows by metric (used with “Must match selected metrics” preset)</summary>
    <p class="filter-hint">Spreadsheet-style controls: <strong>click any column header</strong> to sort (ascending → descending → original), and use the column-header <strong>▾</strong> menu to filter that column (✓/↺/— or Yes/Partial/No checkboxes, a “contains” box for text columns, or min/max for numeric columns like Cites). Check metrics below a paper must report for the “Must match selected metrics” preset.</p>
    <div class="filter-actions">
      <button type="button" id="require-clear">Clear selection</button>
      <button type="button" id="preset-apply">Apply row filter</button>
    </div>
    <div class="metric-requires">{metric_require}</div>
  </details>
</div>
<script type="application/json" id="family-ids">{family_ids_json}</script>
<script type="application/json" id="eval-modality-ids">{eval_modality_ids_json}</script>
"""


def _eval_yes_no(cell: str) -> str:
    return "Yes" if cell == "✓" else "No"


def build_citation_plot_json(rows: list) -> str:
    """JSON payload for Plotly citation-frequency chart (sorted by count desc)."""
    sorted_rows = sorted(rows, key=lambda r: (-r[-1], r[1].lower()))
    payload = {
        "keys": [],
        "counts": [],
        "titles": [],
        "affiliations": [],
        "offline": [],
        "simulation": [],
        "online": [],
        "reports": [],
    }
    for _i, key, title, _pdf_url, affiliation, reports, _fam, _notes, _metrics, _ctr, _rl, eval_cells, cite_count in sorted_rows:
        payload["keys"].append(key)
        payload["counts"].append(cite_count)
        payload["titles"].append(title)
        payload["affiliations"].append(affiliation)
        payload["offline"].append(_eval_yes_no(eval_cells.get("eval-off", "")))
        payload["simulation"].append(_eval_yes_no(eval_cells.get("eval-sim", "")))
        payload["online"].append(_eval_yes_no(eval_cells.get("eval-on", "")))
        payload["reports"].append(reports)
    return json.dumps(payload, ensure_ascii=False)


def build_citation_eval_modality_plot_json(rows: list) -> str:
    """JSON for cite-frequency chart colored by evaluation-modality bucket."""
    sorted_rows = sorted(rows, key=lambda r: (-r[-1], r[1].lower()))
    payload = {
        "keys": [],
        "counts": [],
        "titles": [],
        "affiliations": [],
        "evalBuckets": [],
        "evalBucketLabels": EVAL_MODALITY_BUCKET_LABELS,
        "evalBucketColors": EVAL_MODALITY_BUCKET_COLORS,
        "bucketOrder": [bid for bid, _label, _color in EVAL_MODALITY_BUCKET_META],
    }
    for _i, key, title, _pdf_url, affiliation, _reports, _fam, _notes, _metrics, _ctr, _rl, eval_cells, cite_count in sorted_rows:
        payload["keys"].append(key)
        payload["counts"].append(cite_count)
        payload["titles"].append(title)
        payload["affiliations"].append(affiliation)
        payload["evalBuckets"].append(eval_modality_bucket_from_cells(eval_cells))
    return json.dumps(payload, ensure_ascii=False)


def build_eval_modality_summary_payload(rows: list) -> dict:
    """Count and percent of cited papers per evaluation-modality bucket."""
    total = len(rows)
    bucket_to_keys: dict[str, list[str]] = {
        bid: [] for bid, _label, _color in EVAL_MODALITY_BUCKET_META
    }
    for _i, key, _title, _pdf_url, _aff, _reports, _fam, _notes, _metrics, _ctr, _rl, eval_cells, _cite_count in rows:
        bid = eval_modality_bucket_from_cells(eval_cells)
        bucket_to_keys.setdefault(bid, []).append(key)

    items: list[tuple[int, str, str, str, list[str]]] = []
    for bid, label, color in EVAL_MODALITY_BUCKET_META:
        keys = sorted(bucket_to_keys.get(bid, []), key=str.lower)
        count = len(keys)
        items.append((count, bid, label, color, keys))
    items.sort(key=lambda item: (-item[0], item[2].lower()))

    percents = [round(100.0 * count / total, 1) if total else 0.0 for count, *_ in items]
    return {
        "total": total,
        "bucketIds": [bid for _c, bid, _l, _col, _k in items],
        "labels": [label for _c, _bid, label, _col, _k in items],
        "counts": [count for count, *_ in items],
        "percents": percents,
        "colors": [color for _c, _bid, _l, color, _k in items],
        "paperKeys": [keys for *_rest, keys in items],
        "evalBucketLabels": EVAL_MODALITY_BUCKET_LABELS,
    }


def build_eval_modality_summary_json(rows: list) -> str:
    return json.dumps(build_eval_modality_summary_payload(rows), ensure_ascii=False)


def build_affiliation_histogram_payload(rows: list) -> dict:
    """Papers-per-affiliation counts (sorted by count desc)."""
    aff_to_keys: dict[str, list[str]] = {}
    for _i, key, _title, _pdf_url, affiliation, *_rest in rows:
        aff_to_keys.setdefault(affiliation, []).append(key)

    sorted_items = sorted(
        aff_to_keys.items(),
        key=lambda item: (-len(item[1]), item[0].lower()),
    )
    payload = {
        "affiliations": [],
        "counts": [],
        "paperKeys": [],
    }
    for affiliation, keys in sorted_items:
        payload["affiliations"].append(affiliation)
        payload["counts"].append(len(keys))
        payload["paperKeys"].append(sorted(keys, key=str.lower))
    return payload


def build_affiliation_histogram_json(rows: list) -> str:
    """JSON payload for papers-per-affiliation bar chart (sorted by count desc)."""
    return json.dumps(build_affiliation_histogram_payload(rows), ensure_ascii=False)


def render_citation_plot_section(rows: list) -> str:
    # Raw JSON in script tag (json.dumps is HTML-safe except </script>; titles unlikely to contain it)
    plot_json = build_citation_plot_json(rows).replace("<", "\\u003c")
    return f"""
  <section id="cite-plot">
    <h2>Citation frequency in paper.tex</h2>
    <p class="plot-hint">
      Each bar is a citation key (ticker), sorted by times cited (highest first).
      Hover for title, affiliation, cite count, and evaluation modality flags.
      Use the range slider below the chart to pan across all {len(rows)} papers.
    </p>
    <div id="cite-frequency-plot"></div>
    <script type="application/json" id="cite-plot-data">{plot_json}</script>
  </section>
"""


def render_citation_eval_modality_plot_section(rows: list) -> str:
    plot_json = build_citation_eval_modality_plot_json(rows).replace("<", "\\u003c")
    legend_items = "".join(
        f"<li><span class=\"eval-swatch\" style=\"background:{color}\"></span>"
        f"{html.escape(label)}</li>"
        for _bid, label, color in EVAL_MODALITY_BUCKET_META
    )
    return f"""
  <section id="cite-eval-modality-plot">
    <h2>Citation frequency by evaluation modality</h2>
    <p class="plot-hint">
      Same layout as the citation-frequency chart: each bar is a citation key (ticker),
      sorted by times cited (highest first). Bar color shows which evaluation modalities
      the source paper reports: offline only, online only, offline + simulation only,
      or offline + simulation + online. Other flag combinations and uncatalogued papers
      use separate colors (see legend).
    </p>
    <ul class="eval-modality-legend">{legend_items}</ul>
    <div id="cite-eval-modality-plot"></div>
    <script type="application/json" id="cite-eval-modality-plot-data">{plot_json}</script>
  </section>
"""


def render_eval_modality_summary_section(rows: list) -> str:
    payload = build_eval_modality_summary_payload(rows)
    summary_json = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    return f"""
  <section id="eval-modality-summary">
    <h2>Papers by evaluation modality (share of cited set)</h2>
    <p class="plot-hint">
      Each bar is one evaluation-modality bucket across all {payload["total"]} unique cited papers
      (each paper counted once, regardless of cite frequency in paper.tex).
      Bar length is the number of papers; labels show count and percentage of the total.
      Hover for citation keys in each bucket.
    </p>
    <div id="eval-modality-summary-plot"></div>
    <script type="application/json" id="eval-modality-summary-data">{summary_json}</script>
  </section>
"""


def render_affiliation_histogram_section(rows: list) -> str:
    payload = build_affiliation_histogram_payload(rows)
    hist_json = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    return f"""
  <section id="affiliation-histogram">
    <h2>Papers by affiliation</h2>
    <p class="plot-hint">
      Histogram of the {len(rows)} unique cited papers in this survey, grouped by affiliation label.
      Each bar is one affiliation (x-axis ticker); height is the number of papers with that label.
      Hover for the paper count and citation keys.
      Chart height grows with the number of affiliations so y-axis labels do not overlap.
    </p>
    <div id="affiliation-histogram-plot"></div>
    <script type="application/json" id="affiliation-histogram-data">{hist_json}</script>
  </section>
"""


def render_full_html(
    rows: list,
    keys_count: int,
    verified: int,
    with_any: int,
    no_empirical: int,
    family_counts: dict[str, int],
) -> str:
    examples = {
        "ctr": "CTR, pCTR, clicks, click yield",
        "auc": "AUC, log loss, calibration error",
        "cvr": "CVR, conversion count, ROAS, CPIC",
        "rev": "Revenue, RPM, LTRPM, ROI, CPM",
        "rank": "NDCG, HR@K, Recall, Hit Ratio, MAP",
        "dwell": "Dwell time, watch time, session length",
        "ltv": "Retention, LTV, return rate, churn",
        "regret": "Cumulative regret, PV loss, Hamming loss",
        "rl": "Episode reward, policy value, normalized return",
        "ope": "RMSE, IPS, doubly robust, offline policy value",
        "adux": "Ad load, ad close rate, incrementality lift, fatigue",
    }

    legend_rows = "".join(
        f"<tr><td><code>{html.escape(fid)}</code></td>"
        f"<td>{html.escape(header)}</td>"
        f"<td>{html.escape(examples[fid])}</td></tr>"
        for fid, header in METRIC_FAMILIES
    )

    family_summary = "".join(
        f"<tr><td>{html.escape(header)}</td><td class=\"center\">{family_counts[fid]}</td></tr>"
        for fid, header in METRIC_FAMILIES
    )

    raw_rows = "".join(
        f"<tr><td class=\"center\">{i}</td>"
        f"<td><code>{html.escape(key)}</code></td>"
        f"<td>{html.escape(metrics)}</td></tr>"
        for i, key, _title, _pdf_url, _aff, _reports, _fam, _notes, metrics, _ctr, _rl, _eval, _cc in rows
    )

    matrix_table, _ = render_matrix_table_rows(rows)
    cite_plot_section = render_citation_plot_section(rows)
    cite_eval_modality_plot_section = render_citation_eval_modality_plot_section(rows)
    eval_modality_summary_section = render_eval_modality_summary_section(rows)
    affiliation_hist_section = render_affiliation_histogram_section(rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cited Papers and Metrics — RL Ad Rec Review</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
  :root {{
    --bg: #fafafa;
    --card: #fff;
    --border: #d8d8d8;
    --head: #eef1f5;
    --text: #1a1a1a;
    --muted: #555;
    --accent: #2563eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 15px;
    line-height: 1.45;
    color: var(--text);
    background: var(--bg);
  }}
  header {{
    background: var(--card);
    border-bottom: 1px solid var(--border);
    padding: 1.25rem 2rem;
  }}
  header h1 {{ margin: 0 0 0.35rem; font-size: 1.5rem; }}
  header p {{ margin: 0; color: var(--muted); max-width: 72rem; }}
  main {{ padding: 1.5rem 2rem 3rem; max-width: none; }}
  section {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
  }}
  h2 {{ margin: 0 0 1rem; font-size: 1.15rem; }}
  .plot-hint {{ margin: 0 0 1rem; color: var(--muted); font-size: 14px; max-width: 56rem; }}
  #cite-frequency-plot {{ width: 100%; min-height: 680px; }}
  #cite-eval-modality-plot {{ width: 100%; min-height: 680px; }}
  #eval-modality-summary-plot {{ width: 100%; min-height: 360px; }}
  #affiliation-histogram-plot {{ width: 100%; min-height: 560px; overflow-y: auto; }}
  ul.eval-modality-legend {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem 1.5rem;
    margin: 0 0 1rem;
    padding: 0;
    list-style: none;
    font-size: 13px;
    color: var(--muted);
  }}
  ul.eval-modality-legend li {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }}
  .eval-swatch {{
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid rgba(0,0,0,0.12);
    flex-shrink: 0;
  }}
  .scroll {{ overflow-x: auto; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    font-size: 14px;
  }}
  table.legend, table.summary, table.raw {{
    min-width: auto;
    max-width: 56rem;
  }}
  th, td {{
    border-bottom: 1px solid var(--border);
    padding: 8px 12px;
    vertical-align: top;
    text-align: left;
  }}
  th {{
    background: var(--head);
    font-weight: 600;
    white-space: normal;
  }}
  table.matrix th[data-col="num"] {{ min-width: 56px; }}
  table.matrix th[data-col="cite-count"] {{ min-width: 72px; }}
  table.matrix th[data-col="key"] {{ min-width: 260px; }}
  table.matrix th[data-col="title"] {{ min-width: 480px; }}
  table.matrix th[data-col="reports"] {{ min-width: 100px; }}
  table.matrix th[data-col="eval-off"],
  table.matrix th[data-col="eval-sim"],
  table.matrix th[data-col="eval-on"] {{ min-width: 110px; }}
  table.matrix th[data-col="ctr"],
  table.matrix th[data-col="auc"],
  table.matrix th[data-col="cvr"],
  table.matrix th[data-col="rev"],
  table.matrix th[data-col="rank"],
  table.matrix th[data-col="dwell"],
  table.matrix th[data-col="ltv"],
  table.matrix th[data-col="regret"],
  table.matrix th[data-col="rl"],
  table.matrix th[data-col="ope"],
  table.matrix th[data-col="adux"] {{ min-width: 130px; }}
  table.matrix th[data-col="ctr-detail"],
  table.matrix th[data-col="rl-detail"],
  table.matrix td.metric-detail {{
    min-width: 420px;
    max-width: 520px;
    font-size: 13px;
    line-height: 1.35;
  }}
  td.metric-detail .metric-def,
  td.metric-detail .metric-val {{ display: block; margin-bottom: 0.25rem; }}
  td.metric-detail .metric-set {{ color: var(--muted); font-size: 12px; }}
  table.matrix th[data-col="notes"] {{ min-width: 240px; }}
  td.center, th.center {{ text-align: center; }}
  td[data-col="title"] a.paper-pdf-link {{
    color: #1d4ed8;
    text-decoration: none;
  }}
  td[data-col="title"] a.paper-pdf-link:hover {{
    text-decoration: underline;
  }}
  tbody tr:hover {{ background: #f5f8ff; }}
  code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.92em;
    background: #f0f0f0;
    padding: 0.1em 0.35em;
    border-radius: 4px;
  }}
  ul.stats {{ margin: 0; padding-left: 1.25rem; }}
  ul.stats li {{ margin: 0.25rem 0; }}
  .marker-key {{ margin-top: 0.75rem; color: var(--muted); font-size: 0.95rem; }}

  /* Filter toolbar */
  .filter-toolbar {{
    margin-bottom: 1rem;
    padding: 1rem;
    background: #f8f9fb;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 14px;
  }}
  .filter-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 1rem 1.5rem;
    align-items: flex-end;
    margin-bottom: 0.75rem;
  }}
  .filter-field {{
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 180px;
  }}
  .filter-field span {{ font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.03em; }}
  .filter-field input, .filter-field select {{
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 14px;
  }}
  .filter-count {{
    margin-left: auto;
    font-weight: 600;
    color: var(--accent);
    white-space: nowrap;
  }}
  .filter-panel {{
    margin-top: 0.5rem;
    border-top: 1px solid var(--border);
    padding-top: 0.75rem;
  }}
  .filter-panel summary {{
    cursor: pointer;
    font-weight: 600;
    user-select: none;
  }}
  .filter-hint {{ margin: 0.5rem 0; color: var(--muted); font-size: 13px; }}
  .filter-actions {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.5rem 0; }}
  .filter-actions button, .filter-menu-actions button {{
    padding: 4px 10px;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--card);
    cursor: pointer;
    font-size: 13px;
  }}
  .filter-actions button:hover, .filter-menu-actions button:hover {{ background: #eef1f5; }}
  .col-toggles, .metric-requires {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem 1rem;
    margin-top: 0.5rem;
  }}
  .col-toggle, .metric-require {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    white-space: nowrap;
    font-size: 13px;
  }}

  /* Column header sort + filters (all matrix columns) */
  table.matrix th {{ position: relative; padding: 0; }}
  .th-inner {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 4px;
    padding: 8px 8px 8px 12px;
    min-height: 100%;
  }}
  .th-label {{ flex: 1; }}
  .th-label.sort-btn {{
    cursor: pointer;
    user-select: none;
    border-radius: 3px;
  }}
  .th-label.sort-btn:hover {{ color: var(--accent); }}
  .th-label.sort-btn:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .th-label.sort-btn.sorted {{ color: var(--accent); }}
  .sort-ind {{ color: var(--accent); font-size: 11px; font-weight: 700; }}
  .filter-num {{ display: flex; flex-direction: column; gap: 6px; }}
  .filter-num label {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    font-size: 13px;
  }}
  .filter-menu input.filter-text,
  .filter-menu input.filter-min,
  .filter-menu input.filter-max {{
    width: 150px;
    padding: 4px 6px;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 13px;
  }}
  .filter-num input.filter-min,
  .filter-num input.filter-max {{ width: 90px; }}
  .filter-btn {{
    flex-shrink: 0;
    border: none;
    background: transparent;
    cursor: pointer;
    padding: 2px 6px;
    border-radius: 3px;
    color: var(--muted);
    font-size: 12px;
    line-height: 1;
  }}
  .filter-btn:hover, .filter-btn.active {{ background: #dbeafe; color: var(--accent); }}
  .filter-menu {{
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 20;
    min-width: 160px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    padding: 8px;
    font-weight: normal;
    text-align: left;
  }}
  .filter-menu label {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 2px;
    font-size: 13px;
    cursor: pointer;
  }}
  .filter-menu-actions {{
    display: flex;
    gap: 6px;
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid var(--border);
  }}

  /* Hidden state */
  .col-hidden {{ display: none !important; }}
  tr.row-hidden {{ display: none !important; }}
</style>
</head>
<body>
<header>
  <h1>Cited Papers and Metrics Reporting</h1>
  <p>All <strong>{keys_count}</strong> unique citations in <code>paper.tex</code> (numbered 1–{keys_count}).
  Metrics are normalized into metric-family columns. Generated by
  <code>scripts/build_cited_papers_metrics.py</code>.</p>
  <p class="marker-key"><strong>✓</strong> = paper reports that family empirically &nbsp;|&nbsp;
  <strong>↺</strong> = survey/catalogue only &nbsp;|&nbsp; <strong>—</strong> = not reported</p>
</header>
<main>
  <section id="legend">
    <h2>Metric family columns</h2>
    <table class="legend">
      <thead><tr><th>ID</th><th>Family</th><th>Examples</th></tr></thead>
      <tbody>{legend_rows}</tbody>
    </table>
  </section>

{cite_plot_section}

{cite_eval_modality_plot_section}

{eval_modality_summary_section}

{affiliation_hist_section}

  <section id="matrix">
    <h2>Citation matrix</h2>
    {render_filter_toolbar()}
    <div class="scroll">{matrix_table}</div>
  </section>

  <section id="summary">
    <h2>Summary</h2>
    <ul class="stats">
      <li><strong>Total cited keys:</strong> {keys_count}</li>
      <li><strong>Verified in evaluation_audit.md:</strong> {verified}</li>
      <li><strong>Rows with ≥1 metric family:</strong> {with_any}</li>
      <li><strong>Rows with no empirical metrics:</strong> {no_empirical}</li>
    </ul>
    <h2 style="margin-top:1.25rem">Papers per metric family</h2>
    <table class="summary">
      <thead><tr><th>Family</th><th>Papers (✓ or ↺)</th></tr></thead>
      <tbody>{family_summary}</tbody>
    </table>
  </section>

  <section id="raw">
    <h2>Raw metric descriptions (audit reference)</h2>
    <div class="scroll">
      <table class="raw">
        <thead><tr><th>#</th><th>Citation Key</th><th>Raw metrics text</th></tr></thead>
        <tbody>{raw_rows}</tbody>
      </table>
    </div>
  </section>
</main>
<script>
(function () {{
  const plotEl = document.getElementById('cite-frequency-plot');
  const plotDataEl = document.getElementById('cite-plot-data');
  if (!plotEl || !plotDataEl) return;

  function renderCitePlot() {{
    if (!window.Plotly) {{
      window.setTimeout(renderCitePlot, 50);
      return;
    }}

    const data = JSON.parse(plotDataEl.textContent);
    const affiliations = data.affiliations || [];
    const hovertext = data.keys.map(function (key, i) {{
      return (
        '<b>' + data.titles[i] + '</b><br>' +
        '<b>Affiliation:</b> ' + (affiliations[i] || '—') + '<br>' +
        'Key: ' + key + '<br>' +
        'Cites in paper: ' + data.counts[i] + '<br>' +
        'Offline eval: ' + data.offline[i] + '<br>' +
        'Simulation: ' + data.simulation[i] + '<br>' +
        'Online eval: ' + data.online[i] + '<br>' +
        'Reports metrics: ' + data.reports[i]
      );
    }});

    Plotly.newPlot(
      plotEl,
      [{{
        type: 'bar',
        x: data.keys,
        y: data.counts,
        text: hovertext,
        hovertemplate: '%{{text}}<extra></extra>',
        marker: {{ color: '#2563eb' }},
      }}],
      {{
        margin: {{ t: 24, r: 24, b: 220, l: 64 }},
        height: 680,
        xaxis: {{
          title: 'Citation key (ticker)',
          tickangle: -55,
          automargin: true,
          rangeslider: {{ visible: true, thickness: 0.06 }},
        }},
        yaxis: {{ title: 'Times cited in paper.tex', rangemode: 'tozero' }},
        hovermode: 'closest',
      }},
      {{ responsive: true, displayModeBar: true }}
    );
  }}

  renderCitePlot();
}})();
</script>
<script>
(function () {{
  const plotEl = document.getElementById('cite-eval-modality-plot');
  const plotDataEl = document.getElementById('cite-eval-modality-plot-data');
  if (!plotEl || !plotDataEl) return;

  function renderEvalModalityCitePlot() {{
    if (!window.Plotly) {{
      window.setTimeout(renderEvalModalityCitePlot, 50);
      return;
    }}

    const data = JSON.parse(plotDataEl.textContent);
    const colors = data.evalBucketColors || {{}};
    const labels = data.evalBucketLabels || {{}};
    const affiliations = data.affiliations || [];
    const barColors = (data.evalBuckets || []).map(function (bid) {{
      return colors[bid] || '#94a3b8';
    }});

    const hovertext = data.keys.map(function (key, i) {{
      const bucketLabel = labels[data.evalBuckets[i]] || data.evalBuckets[i] || '—';
      return (
        '<b>' + data.titles[i] + '</b><br>' +
        '<b>Eval modality:</b> ' + bucketLabel + '<br>' +
        '<b>Affiliation:</b> ' + (affiliations[i] || '—') + '<br>' +
        'Key: ' + key + '<br>' +
        'Cites in paper: ' + data.counts[i]
      );
    }});

    const barTrace = {{
      type: 'bar',
      x: data.keys,
      y: data.counts,
      text: hovertext,
      hovertemplate: '%{{text}}<extra></extra>',
      marker: {{ color: barColors }},
      showlegend: false,
    }};

    const legendTraces = (data.bucketOrder || []).map(function (bid) {{
      return {{
        type: 'bar',
        x: [null],
        y: [null],
        name: labels[bid] || bid,
        marker: {{ color: colors[bid] || '#94a3b8' }},
        showlegend: true,
        hoverinfo: 'skip',
      }};
    }});

    Plotly.newPlot(
      plotEl,
      [barTrace].concat(legendTraces),
      {{
        margin: {{ t: 24, r: 24, b: 220, l: 64 }},
        height: 680,
        xaxis: {{
          title: 'Citation key (ticker)',
          tickangle: -55,
          automargin: true,
          rangeslider: {{ visible: true, thickness: 0.06 }},
        }},
        yaxis: {{ title: 'Times cited in paper.tex', rangemode: 'tozero' }},
        hovermode: 'closest',
        legend: {{
          orientation: 'h',
          yanchor: 'bottom',
          y: 1.02,
          xanchor: 'left',
          x: 0,
          font: {{ size: 11 }},
        }},
      }},
      {{ responsive: true, displayModeBar: true }}
    );
  }}

  renderEvalModalityCitePlot();
}})();
</script>
<script>
(function () {{
  const plotEl = document.getElementById('eval-modality-summary-plot');
  const plotDataEl = document.getElementById('eval-modality-summary-data');
  if (!plotEl || !plotDataEl) return;

  function renderEvalModalitySummary() {{
    if (!window.Plotly) {{
      window.setTimeout(renderEvalModalitySummary, 50);
      return;
    }}

    const data = JSON.parse(plotDataEl.textContent);
    const labels = data.labels || [];
    const counts = data.counts || [];
    const percents = data.percents || [];
    const colors = data.colors || [];
    const paperKeys = data.paperKeys || [];
    const total = data.total || 0;

    const displayLabels = labels.slice().reverse();
    const displayCounts = counts.slice().reverse();
    const displayPercents = percents.slice().reverse();
    const displayColors = colors.slice().reverse();
    const displayKeys = paperKeys.slice().reverse();

    const barText = displayCounts.map(function (n, i) {{
      return n + ' (' + displayPercents[i] + '%)';
    }});

    const hovertext = displayLabels.map(function (label, i) {{
      const keys = displayKeys[i] || [];
      const preview = keys.length <= 12
        ? keys.join(', ')
        : keys.slice(0, 12).join(', ') + ' … (' + keys.length + ' papers)';
      return (
        '<b>' + label + '</b><br>' +
        'Papers: ' + displayCounts[i] + ' of ' + total +
        ' (' + displayPercents[i] + '%)<br>' +
        'Citation keys: ' + preview
      );
    }});

    const plotHeight = Math.max(360, displayLabels.length * 52 + 100);

    Plotly.newPlot(
      plotEl,
      [{{
        type: 'bar',
        orientation: 'h',
        y: displayLabels,
        x: displayCounts,
        text: barText,
        textposition: 'outside',
        cliponaxis: false,
        customdata: hovertext,
        hovertemplate: '%{{customdata}}<extra></extra>',
        marker: {{ color: displayColors }},
      }}],
      {{
        margin: {{ t: 24, r: 96, b: 56, l: 12 }},
        height: plotHeight,
        xaxis: {{
          title: 'Number of papers (' + total + ' total)',
          rangemode: 'tozero',
          dtick: 1,
          automargin: true,
        }},
        yaxis: {{
          title: 'Evaluation modality bucket',
          automargin: true,
          tickfont: {{ size: 12 }},
        }},
        hovermode: 'closest',
        bargap: 0.25,
      }},
      {{ responsive: true, displayModeBar: true }}
    );
  }}

  renderEvalModalitySummary();
}})();
</script>
<script>
(function () {{
  const plotEl = document.getElementById('affiliation-histogram-plot');
  const plotDataEl = document.getElementById('affiliation-histogram-data');
  if (!plotEl || !plotDataEl) return;

  function renderAffiliationHistogram() {{
    if (!window.Plotly) {{
      window.setTimeout(renderAffiliationHistogram, 50);
      return;
    }}

    const data = JSON.parse(plotDataEl.textContent);
    const paperKeys = data.paperKeys || [];
    // Horizontal bars: largest counts at top; one y-axis label per affiliation.
    const affiliations = data.affiliations.slice().reverse();
    const counts = data.counts.slice().reverse();
    const keysByAff = paperKeys.slice().reverse();
    const maxCount = Math.max.apply(null, counts.concat([1]));

    const hovertext = affiliations.map(function (aff, i) {{
      const keys = keysByAff[i] || [];
      const preview = keys.length <= 10
        ? keys.join(', ')
        : keys.slice(0, 10).join(', ') + ' … (' + keys.length + ' papers)';
      return (
        '<b>' + aff + '</b><br>' +
        'Papers in survey: ' + counts[i] + '<br>' +
        'Citation keys: ' + preview
      );
    }});

    const plotHeight = Math.max(560, affiliations.length * 26 + 120);
    const countStep = maxCount <= 8 ? 1 : maxCount <= 20 ? 2 : 5;

    Plotly.newPlot(
      plotEl,
      [{{
        type: 'bar',
        orientation: 'h',
        y: affiliations,
        x: counts,
        text: hovertext,
        hovertemplate: '%{{text}}<extra></extra>',
        marker: {{ color: '#059669' }},
      }}],
      {{
        margin: {{ t: 24, r: 32, b: 72, l: 12 }},
        height: plotHeight,
        xaxis: {{
          title: 'Number of papers',
          rangemode: 'tozero',
          tickmode: 'linear',
          tick0: 0,
          dtick: countStep,
          automargin: true,
        }},
        yaxis: {{
          title: 'Affiliation',
          automargin: true,
          tickfont: {{ size: 11 }},
          ticklabelposition: 'outside',
          ticklabeloverflow: 'allow',
          categoryorder: 'array',
          categoryarray: affiliations,
        }},
        hovermode: 'closest',
        bargap: 0.2,
      }},
      {{ responsive: true, displayModeBar: true }}
    );
  }}

  renderAffiliationHistogram();
}})();
</script>
<script>
(function () {{
  const table = document.getElementById('citation-matrix');
  const searchInput = document.getElementById('filter-search');
  const presetSelect = document.getElementById('filter-preset');
  const matchSelect = document.getElementById('filter-match');
  const countEl = document.getElementById('filter-count');
  const familyIdsEl = document.getElementById('family-ids');
  const evalModalityIdsEl = document.getElementById('eval-modality-ids');
  if (!table || !searchInput || !presetSelect || !matchSelect || !countEl || !familyIdsEl || !evalModalityIdsEl) {{
    return;
  }}

  let familyIds;
  let evalModalityIds;
  try {{
    familyIds = JSON.parse(familyIdsEl.textContent);
    evalModalityIds = JSON.parse(evalModalityIdsEl.textContent);
  }} catch (err) {{
    console.error('Citation matrix filters: failed to parse column IDs', err);
    return;
  }}

  const columnKindsEl = document.getElementById('column-kinds');
  let columnKinds = {{}};
  try {{
    if (columnKindsEl) columnKinds = JSON.parse(columnKindsEl.textContent);
  }} catch (err) {{
    console.error('Citation matrix: failed to parse column kinds', err);
  }}

  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const totalRows = rows.length;
  const originalOrder = rows.slice();

  function markerDefaults(col) {{
    if (evalModalityIds.includes(col)) return ['check', 'empty'];
    if (familyIds.includes(col)) return ['check', 'survey', 'empty'];
    if (col === 'reports') return ['yes', 'partial', 'no'];
    return [];
  }}

  // Per-column filter state, keyed by column kind.
  const setFilters = {{}};   // marker / enum -> Set of allowed values
  const textFilters = {{}};  // text          -> lowercased substring
  const numFilters = {{}};   // number        -> {{ min, max }}
  Object.keys(columnKinds).forEach(col => {{
    const kind = columnKinds[col];
    if (kind === 'marker' || kind === 'enum') setFilters[col] = new Set(markerDefaults(col));
    else if (kind === 'text') textFilters[col] = '';
    else if (kind === 'number') numFilters[col] = {{ min: null, max: null }};
  }});

  function cellEl(tr, col) {{ return tr.querySelector('[data-col="' + col + '"]'); }}
  function cellText(tr, col) {{ const el = cellEl(tr, col); return (el ? el.textContent : '').trim(); }}
  function cellNumber(tr, col) {{
    const raw = cellText(tr, col).replace(/[^0-9.\\-]/g, '');
    const n = parseFloat(raw);
    return isNaN(n) ? null : n;
  }}
  function markerValue(tr, col, kind) {{
    if (kind === 'enum') return tr.getAttribute('data-reports') || 'no';
    return tr.getAttribute('data-m-' + col) || 'empty';
  }}

  function getVisibleCols() {{
    return new Set(
      Array.from(document.querySelectorAll('.col-show'))
        .filter(cb => cb.checked)
        .map(cb => cb.dataset.col)
    );
  }}

  function getRequiredMetrics() {{
    return Array.from(document.querySelectorAll('.row-require:checked')).map(cb => cb.dataset.col);
  }}

  function rowMatchesPreset(tr) {{
    const preset = presetSelect.value;
    if (preset === 'all') return true;
    if (preset === 'empirical') return tr.dataset.reports === 'yes';
    if (preset === 'any-metric') return tr.dataset.hasAnyMetric === '1';
    if (preset === 'empirical-mark') return tr.dataset.hasEmpirical === '1';
    if (preset === 'ctr-detail') return tr.dataset.hasCtrDetail === '1';
    if (preset === 'rl-detail') return tr.dataset.hasRlDetail === '1';
    if (preset === 'eval-off') return tr.getAttribute('data-m-eval-off') === 'check';
    if (preset === 'eval-sim') return tr.getAttribute('data-m-eval-sim') === 'check';
    if (preset === 'eval-on') return tr.getAttribute('data-m-eval-on') === 'check';
    if (preset === 'require-selected') {{
      const required = getRequiredMetrics();
      if (required.length === 0) return true;
      const match = matchSelect.value;
      const hits = required.filter(col => {{
        const val = tr.getAttribute('data-m-' + col);
        return val === 'check' || val === 'survey';
      }});
      return match === 'all' ? hits.length === required.length : hits.length > 0;
    }}
    return true;
  }}

  function rowMatchesColFilters(tr) {{
    for (const col in columnKinds) {{
      const kind = columnKinds[col];
      if (kind === 'marker' || kind === 'enum') {{
        const allowed = setFilters[col];
        if (!allowed) continue;
        if (allowed.size === markerDefaults(col).length) continue;
        if (!allowed.has(markerValue(tr, col, kind))) return false;
      }} else if (kind === 'text') {{
        const q = textFilters[col];
        if (q && !cellText(tr, col).toLowerCase().includes(q)) return false;
      }} else if (kind === 'number') {{
        const f = numFilters[col];
        if (f && (f.min !== null || f.max !== null)) {{
          const v = cellNumber(tr, col);
          if (v === null) return false;
          if (f.min !== null && v < f.min) return false;
          if (f.max !== null && v > f.max) return false;
        }}
      }}
    }}
    return true;
  }}

  function rowMatchesSearch(tr) {{
    const q = (searchInput.value || '').trim().toLowerCase();
    if (!q) return true;
    const haystack = (
      tr.getAttribute('data-search') ||
      tr.dataset.search ||
      ''
    ).toLowerCase();
    if (haystack.includes(q)) return true;
    const keyCell = tr.querySelector('[data-col="key"]');
    const keyText = (keyCell ? keyCell.textContent : '').toLowerCase();
    return keyText.includes(q);
  }}

  function applyFilters() {{
    let visible = 0;
    rows.forEach(tr => {{
      const show = rowMatchesSearch(tr) && rowMatchesPreset(tr) && rowMatchesColFilters(tr);
      tr.classList.toggle('row-hidden', !show);
      if (show) visible++;
    }});
    countEl.textContent = `Showing ${{visible}} of ${{totalRows}} papers`;
  }}

  function applyColumnVisibility() {{
    const visibleMetricCols = getVisibleCols();
    const metricsOnly = document.getElementById('cols-metrics-only')?.dataset.active === '1';

    table.querySelectorAll('[data-col]').forEach(el => {{
      const col = el.dataset.col;
      if (familyIds.includes(col)) {{
        el.classList.toggle('col-hidden', !visibleMetricCols.has(col));
      }} else if (metricsOnly && (col === 'num' || col === 'notes')) {{
        el.classList.add('col-hidden');
      }} else if (col === 'num' || col === 'notes' || col === 'key' || col === 'title' || col === 'reports') {{
        el.classList.remove('col-hidden');
      }}
    }});
  }}

  function hideEmptyColumns() {{
    familyIds.forEach(col => {{
      const hasData = rows.some(tr => {{
        const v = tr.getAttribute('data-m-' + col);
        return v === 'check' || v === 'survey';
      }});
      const cb = document.querySelector('.col-show[data-col="' + col + '"]');
      if (cb) cb.checked = hasData;
    }});
    document.getElementById('cols-metrics-only').dataset.active = '0';
    applyColumnVisibility();
  }}

  // Events
  searchInput.addEventListener('input', applyFilters);
  searchInput.addEventListener('keyup', applyFilters);
  searchInput.addEventListener('search', applyFilters);
  presetSelect.addEventListener('change', applyFilters);
  matchSelect.addEventListener('change', applyFilters);
  document.querySelectorAll('.row-require').forEach(cb => cb.addEventListener('change', () => {{
    if (presetSelect.value !== 'require-selected') presetSelect.value = 'require-selected';
    applyFilters();
  }}));

  document.querySelectorAll('.col-show').forEach(cb => cb.addEventListener('change', () => {{
    document.getElementById('cols-metrics-only').dataset.active = '0';
    applyColumnVisibility();
  }}));

  document.getElementById('cols-show-all').addEventListener('click', () => {{
    document.querySelectorAll('.col-show').forEach(cb => {{ cb.checked = true; }});
    document.getElementById('cols-metrics-only').dataset.active = '0';
    applyColumnVisibility();
  }});
  document.getElementById('cols-hide-empty').addEventListener('click', hideEmptyColumns);
  document.getElementById('cols-metrics-only').addEventListener('click', (e) => {{
    document.querySelectorAll('.col-show').forEach(cb => {{ cb.checked = true; }});
    e.target.dataset.active = '1';
    applyColumnVisibility();
  }});
  document.getElementById('require-clear').addEventListener('click', () => {{
    document.querySelectorAll('.row-require').forEach(cb => {{ cb.checked = false; }});
    applyFilters();
  }});
  document.getElementById('preset-apply').addEventListener('click', () => {{
    presetSelect.value = 'require-selected';
    applyFilters();
  }});

  // ---- Sorting (click any header: ascending -> descending -> original) ----
  let sortState = {{ col: null, dir: 0 }};
  const sortRank = {{
    marker: {{ empty: 0, survey: 1, check: 2 }},
    enum: {{ no: 0, partial: 1, yes: 2 }},
  }};
  function sortValue(tr, col, kind) {{
    if (kind === 'number') {{ const v = cellNumber(tr, col); return v === null ? -Infinity : v; }}
    if (kind === 'marker' || kind === 'enum') {{
      const rank = sortRank[kind] || {{}};
      const v = markerValue(tr, col, kind);
      return (v in rank) ? rank[v] : -1;
    }}
    return cellText(tr, col).toLowerCase();
  }}
  function applySort() {{
    let ordered;
    if (!sortState.col || sortState.dir === 0) {{
      ordered = originalOrder;
    }} else {{
      const col = sortState.col;
      const kind = columnKinds[col] || 'text';
      const dir = sortState.dir;
      ordered = originalOrder.slice().sort((a, b) => {{
        const va = sortValue(a, col, kind);
        const vb = sortValue(b, col, kind);
        let cmp;
        if (typeof va === 'number' && typeof vb === 'number') cmp = va - vb;
        else cmp = String(va).localeCompare(String(vb), undefined, {{ numeric: true }});
        return cmp * dir;
      }});
    }}
    const frag = document.createDocumentFragment();
    ordered.forEach(tr => frag.appendChild(tr));
    tbody.appendChild(frag);
    updateSortIndicators();
  }}
  function updateSortIndicators() {{
    table.querySelectorAll('.sort-btn').forEach(btn => {{
      const ind = btn.querySelector('.sort-ind');
      const active = btn.dataset.col === sortState.col && sortState.dir !== 0;
      btn.classList.toggle('sorted', active);
      if (ind) ind.textContent = active ? (sortState.dir === 1 ? ' \\u25B2' : ' \\u25BC') : '';
    }});
  }}
  function cycleSort(col) {{
    if (sortState.col !== col) sortState = {{ col: col, dir: 1 }};
    else if (sortState.dir === 1) sortState = {{ col: col, dir: -1 }};
    else sortState = {{ col: null, dir: 0 }};
    applySort();
  }}
  table.querySelectorAll('.sort-btn').forEach(btn => {{
    btn.addEventListener('click', () => cycleSort(btn.dataset.col));
    btn.addEventListener('keydown', e => {{
      if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); cycleSort(btn.dataset.col); }}
    }});
  }});

  // ---- Column header filter menus (toggle open/close) ----
  document.querySelectorAll('.filter-btn').forEach(btn => {{
    btn.addEventListener('click', (e) => {{
      e.stopPropagation();
      const col = btn.dataset.col;
      const menu = document.querySelector('.filter-menu[data-col="' + col + '"]');
      const open = !menu.hidden;
      document.querySelectorAll('.filter-menu').forEach(m => {{ m.hidden = true; }});
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      if (!open) {{
        menu.hidden = false;
        btn.classList.add('active');
        const focusable = menu.querySelector('input[type="search"], input[type="number"]');
        if (focusable) focusable.focus();
      }}
    }});
  }});

  document.querySelectorAll('.filter-menu').forEach(menu => {{
    const col = menu.dataset.col;
    const kind = menu.dataset.kind || columnKinds[col] || 'text';
    const applyBtn = menu.querySelector('.filter-apply');
    const clearBtn = menu.querySelector('.filter-clear');
    const filterBtn = menu.closest('th').querySelector('.filter-btn');
    function markActive(active) {{ if (filterBtn) filterBtn.classList.toggle('active', active); }}

    function commit() {{
      if (kind === 'marker' || kind === 'enum') {{
        const allowed = new Set();
        menu.querySelectorAll('input[data-val]').forEach(inp => {{
          if (inp.checked) allowed.add(inp.dataset.val);
        }});
        const defs = markerDefaults(col);
        setFilters[col] = allowed.size ? allowed : new Set(defs);
        markActive(setFilters[col].size < defs.length);
      }} else if (kind === 'text') {{
        const inp = menu.querySelector('.filter-text');
        textFilters[col] = (inp ? inp.value : '').trim().toLowerCase();
        markActive(!!textFilters[col]);
      }} else if (kind === 'number') {{
        const minEl = menu.querySelector('.filter-min');
        const maxEl = menu.querySelector('.filter-max');
        const minV = minEl ? minEl.value : '';
        const maxV = maxEl ? maxEl.value : '';
        numFilters[col] = {{
          min: minV === '' ? null : parseFloat(minV),
          max: maxV === '' ? null : parseFloat(maxV),
        }};
        markActive(numFilters[col].min !== null || numFilters[col].max !== null);
      }}
      menu.hidden = true;
      applyFilters();
    }}

    function reset() {{
      if (kind === 'marker' || kind === 'enum') {{
        menu.querySelectorAll('input[data-val]').forEach(inp => {{ inp.checked = true; }});
        setFilters[col] = new Set(markerDefaults(col));
      }} else if (kind === 'text') {{
        const inp = menu.querySelector('.filter-text');
        if (inp) inp.value = '';
        textFilters[col] = '';
      }} else if (kind === 'number') {{
        menu.querySelectorAll('input').forEach(inp => {{ inp.value = ''; }});
        numFilters[col] = {{ min: null, max: null }};
      }}
      markActive(false);
      menu.hidden = true;
      applyFilters();
    }}

    if (applyBtn) applyBtn.addEventListener('click', commit);
    if (clearBtn) clearBtn.addEventListener('click', reset);
    menu.querySelectorAll('input[type="search"], input[type="number"]').forEach(inp => {{
      inp.addEventListener('keydown', e => {{
        if (e.key === 'Enter') {{ e.preventDefault(); commit(); }}
      }});
    }});
  }});

  document.addEventListener('click', () => {{
    document.querySelectorAll('.filter-menu').forEach(m => {{ m.hidden = true; }});
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  }});
  document.querySelectorAll('.filter-menu').forEach(m => {{
    m.addEventListener('click', e => e.stopPropagation());
  }});

  applyColumnVisibility();
  applyFilters();
}})();
</script>
</body>
</html>
"""


def audit_key_families_coverage(keys: list[str], audit_metrics: dict[str, str]) -> list[str]:
    """
    Compare KEY_FAMILIES against MANUAL_METRICS / evaluation_audit text.
    Returns human-readable warnings when curated families omit inferred metrics.
    """
    warnings: list[str] = []
    for key in keys:
        if key not in KEY_FAMILIES:
            continue
        metrics = MANUAL_METRICS.get(key) or audit_metrics.get(key) or ""
        if not metrics or metrics.startswith("N/A") or metrics.startswith("Catalogues"):
            continue
        if metrics.startswith("Discusses"):
            continue
        inferred = infer_families_from_text(metrics)
        curated = KEY_FAMILIES[key]
        missing = sorted(inferred - curated)
        if missing:
            warnings.append(
                f"{key}: KEY_FAMILIES missing {missing} "
                f"(from: {metrics[:72]}{'…' if len(metrics) > 72 else ''})"
            )
    return warnings


def audit_eval_modality_coverage(keys: list[str]) -> list[str]:
    """Warn when cited papers lack explicit evaluation-modality flags."""
    missing = sorted(k for k in keys if k not in EVAL_MODALITY_FLAGS)
    if not missing:
        return []
    return [f"{k}: missing EVAL_MODALITY_FLAGS entry" for k in missing]


def main() -> None:
    import os
    import sys

    fetch_pdf_urls = "--fetch-pdf-urls" in sys.argv or os.environ.get("CITE_METRICS_FETCH_PDF") == "1"

    tex = (ROOT / "paper.tex").read_text()
    audit_text = (ROOT / "docs/agent/evaluation_audit.md").read_text()
    bib_db = parse_bib()
    audit_metrics = parse_audit_metrics(audit_text)
    audit_metric_details = parse_audit_metric_details(audit_text)
    audit_eval_modalities = parse_audit_eval_modalities(audit_text)
    audit_keys = set(audit_metrics.keys())
    pdf_url_cache = load_pdf_url_cache()
    initial_pdf_cache = dict(pdf_url_cache)
    for key, url in PDF_URL_OVERRIDES.items():
        pdf_url_cache[key] = url

    keys = extract_cite_keys(tex)
    cite_counts = count_cite_keys(tex)
    for warning in audit_key_families_coverage(keys, audit_metrics):
        print(f"WARNING: {warning}")
    for warning in audit_eval_modality_coverage(keys):
        print(f"WARNING: {warning}")
    rows = []
    family_counts = {fid: 0 for fid in FAMILY_IDS}

    for i, key in enumerate(keys, start=1):
        info = bib_db.get(key, {})
        title = info.get("title", "Title not found in bib")
        entry_type = info.get("type", "")
        metrics = MANUAL_METRICS.get(key) or audit_metrics.get(key) or "Not yet catalogued"
        reports = classify_reports_metrics(key, title, entry_type, metrics, audit_keys)
        partial = reports == "⚠️ Partial"
        fam_cells = families_for_key(key, metrics, title, partial)
        notes = notes_for(key, metrics, reports, audit_keys)

        for fid in FAMILY_IDS:
            if fam_cells[fid]:
                family_counts[fid] += 1

        ctr_detail = ctr_clicks_detail_for_key(key, fam_cells, audit_metric_details)
        rl_detail = rl_reward_detail_for_key(key, fam_cells, audit_metric_details)
        eval_cells = eval_modality_cells_for_key(key, reports, audit_eval_modalities)
        affiliation = affiliation_for_key(key, title, info)
        pdf_url = resolve_pdf_url(key, info, pdf_url_cache, fetch_missing=fetch_pdf_urls)
        rows.append((
            i, key, title, pdf_url, affiliation, reports, fam_cells, notes, metrics,
            ctr_detail, rl_detail, eval_cells, cite_counts.get(key, 0),
        ))

    if pdf_url_cache != initial_pdf_cache:
        save_pdf_url_cache(pdf_url_cache)

    linked = sum(1 for r in rows if r[3])
    print(f"Title PDF links: {linked}/{len(rows)}")

    verified = sum(1 for r in rows if r[7] == "Verified in evaluation_audit.md")
    with_any = sum(1 for r in rows if any(r[6][fid] for fid in FAMILY_IDS))
    no_empirical = sum(1 for r in rows if r[5] == "❌ No")

    html_out = ROOT / "CITED_PAPERS_METRICS.html"
    html_out.write_text(
        render_full_html(rows, len(keys), verified, with_any, no_empirical, family_counts),
        encoding="utf-8",
    )

    md_out = ROOT / "CITED_PAPERS_METRICS.md"
    md_out.write_text(
        "\n".join([
            "# Cited Papers and Metrics Reporting",
            "",
            f"Open **[CITED_PAPERS_METRICS.html](CITED_PAPERS_METRICS.html)** "
            f"for the full wide-format citation matrix ({len(keys)} papers).",
            "",
            "Regenerate both files:",
            "",
            "```bash",
            "python3 scripts/build_cited_papers_metrics.py",
            "```",
            "",
        ])
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {html_out} ({len(rows)} rows)")
    print(f"Wrote {md_out} (pointer)")


if __name__ == "__main__":
    main()
