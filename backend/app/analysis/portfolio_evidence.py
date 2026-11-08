"""Portfolio evidence for roles where GitHub does not apply (design, business, marketing,
finance). The user lists links and answers a short checklist. Links are checked for format
and platform only: they are never opened, so the score is self-reported evidence."""
from urllib.parse import urlparse

MAX_LINKS = 5
MAX_LINK_LENGTH = 300
MAX_CASE_STUDIES = 20

KNOWN_PLATFORMS = {
    "behance.net": "Behance",
    "dribbble.com": "Dribbble",
    "figma.com": "Figma",
    "myportfolio.com": "Adobe Portfolio",
    "notion.so": "Notion",
    "notion.site": "Notion",
    "medium.com": "Medium",
    "substack.com": "Substack",
    "linkedin.com": "LinkedIn",
    "github.com": "GitHub",
    "github.io": "GitHub Pages",
    "canva.com": "Canva",
    "wixsite.com": "Wix",
    "squarespace.com": "Squarespace",
    "carrd.co": "Carrd",
    "drive.google.com": "Google Drive",
    "docs.google.com": "Google Docs",
    "slides.google.com": "Google Slides",
}


class EvidenceError(ValueError):
    """Raised when the submitted evidence is invalid."""


def _clean_link(raw: str) -> dict:
    text = raw.strip()
    if len(text) > MAX_LINK_LENGTH:
        raise EvidenceError("A link is too long. Links must be under 300 characters.")
    candidate = text if "://" in text else f"https://{text}"
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in ("http", "https") or "." not in host or " " in text:
        raise EvidenceError(f"'{text}' does not look like a web link.")
    host = host[4:] if host.startswith("www.") else host
    platform = next(
        (name for domain, name in KNOWN_PLATFORMS.items() if host == domain or host.endswith("." + domain)),
        None,
    )
    return {
        "url": f"{parsed.scheme}://{host}{parsed.path.rstrip('/')}",
        "platform": platform or "Personal site",
        "recognized": platform is not None,
    }


def score_portfolio_evidence(
    links: list,
    case_studies: int,
    has_results: bool,
    has_process: bool,
    recent_work: bool,
) -> dict:
    raw_links = [l for l in (links or []) if l and l.strip()]
    if len(raw_links) > MAX_LINKS:
        raise EvidenceError(f"Add at most {MAX_LINKS} links.")
    if not 0 <= case_studies <= MAX_CASE_STUDIES:
        raise EvidenceError(f"Case studies must be between 0 and {MAX_CASE_STUDIES}.")

    cleaned, seen = [], set()
    for raw in raw_links:
        link = _clean_link(raw)
        if link["url"].lower() not in seen:
            seen.add(link["url"].lower())
            cleaned.append(link)

    score = round(
        min(len(cleaned), 3) / 3 * 25
        + min(case_studies, 4) / 4 * 40
        + (15 if has_results else 0)
        + (10 if has_process else 0)
        + (10 if recent_work else 0)
    )

    notes = []
    if len(cleaned) < 3:
        notes.append("Add at least 3 portfolio links (case studies, a portfolio site or published work)")
    if case_studies < 3:
        notes.append("Aim for 3 to 4 case studies that show your process and results")
    if not has_results:
        notes.append("Show measurable results in your work")
    if not has_process:
        notes.append("Explain your process: the problem, your approach and the outcome")
    if not recent_work:
        notes.append("Add something from the last 6 months")
    if not notes:
        notes.append("Portfolio evidence looks strong")

    return {
        "score": score,
        "notes": notes,
        "links": cleaned,
        "case_studies": case_studies,
        "has_results": has_results,
        "has_process": has_process,
        "recent_work": recent_work,
    }