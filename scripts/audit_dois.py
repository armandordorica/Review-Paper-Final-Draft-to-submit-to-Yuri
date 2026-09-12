#!/usr/bin/env python3
"""Audit every DOI in bibliography.bib against Crossref metadata.

Flags entries where the bib title does not reasonably match the title
Crossref has registered for that DOI (a strong signal of a fabricated or
mismatched DOI, as flagged by the ACM TORS Associate Editor).
"""
import re
import sys
import time
import json
import urllib.request
import urllib.error
import difflib

BIB_PATH = "bibliography.bib"

entry_re = re.compile(r"@(\w+)\{([^,]+),(.*?)\n\}", re.DOTALL)
field_re = re.compile(r"(\w+)\s*=\s*[\{\"](.*?)[\}\"]\s*,?\s*$", re.MULTILINE)


def extract_field(body, name):
    # handle nested braces roughly by matching balanced braces for the field
    pattern = re.compile(rf"{name}\s*=\s*\{{", re.IGNORECASE)
    m = pattern.search(body)
    if not m:
        return None
    start = m.end()
    depth = 1
    i = start
    while i < len(body) and depth > 0:
        if body[i] == "{":
            depth += 1
        elif body[i] == "}":
            depth -= 1
        i += 1
    return body[start:i-1].strip()


def clean_title(t):
    if not t:
        return ""
    t = re.sub(r"[\{\}]", "", t)
    t = re.sub(r"\\'\w?", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def normalize(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def similarity(a, b):
    return difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def main():
    with open(BIB_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    for m in entry_re.finditer(content):
        etype, key, body = m.group(1), m.group(2), m.group(3)
        doi = extract_field(body, "doi")
        title = extract_field(body, "title")
        if doi:
            entries.append((key, clean_title(title), doi.strip()))

    print(f"Found {len(entries)} entries with a doi field.\n")

    results = []
    for i, (key, title, doi) in enumerate(entries):
        doi_clean = doi.strip().rstrip(".")
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi_clean)}" if False else f"https://api.crossref.org/works/{doi_clean}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "doi-audit/1.0 (mailto:test@example.com)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.load(resp)
            cr_title = data["message"].get("title", [""])
            cr_title = cr_title[0] if cr_title else ""
            sim = similarity(title, cr_title)
            flag = "MISMATCH" if sim < 0.5 else ("CHECK" if sim < 0.75 else "OK")
            results.append((key, doi_clean, title, cr_title, round(sim, 2), flag))
        except urllib.error.HTTPError as e:
            results.append((key, doi_clean, title, f"<HTTP {e.code}>", 0.0, "ERROR"))
        except Exception as e:
            results.append((key, doi_clean, title, f"<ERROR {e}>", 0.0, "ERROR"))
        time.sleep(0.15)
        if (i + 1) % 25 == 0:
            print(f"...checked {i+1}/{len(entries)}", file=sys.stderr)

    results.sort(key=lambda r: r[4])
    for key, doi, title, cr_title, sim, flag in results:
        print(f"[{flag:8s}] sim={sim:.2f} key={key} doi={doi}")
        print(f"    bib title : {title}")
        print(f"    crossref  : {cr_title}")

    n_mismatch = sum(1 for r in results if r[5] == "MISMATCH")
    n_check = sum(1 for r in results if r[5] == "CHECK")
    n_error = sum(1 for r in results if r[5] == "ERROR")
    print(f"\nTotal: {len(results)} | MISMATCH: {n_mismatch} | CHECK: {n_check} | ERROR: {n_error}")


if __name__ == "__main__":
    import urllib.parse
    main()
