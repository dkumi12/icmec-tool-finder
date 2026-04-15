"""
normalise.py
Converts descriptive string fields in tools.json into clean values
the scoring engine can compare.
"""

from __future__ import annotations

from functools import lru_cache
import json
import pathlib
import re


LANGUAGE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "English": ("english",),
    "Spanish": ("spanish", "espanol", "español"),
    "French": ("french", "francais", "français"),
    "Arabic": ("arabic",),
    "Portuguese": ("portuguese",),
    "Chinese": ("chinese", "mandarin"),
}


def _normalise_tool_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip()).lower()


@lru_cache(maxsize=1)
def _load_enrichment() -> dict[str, dict]:
    data_path = pathlib.Path(__file__).parent.parent / "data" / "tool_enrichment.json"
    if not data_path.exists():
        return {}
    with open(data_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return raw.get("tools", {}) if isinstance(raw, dict) else {}


def parse_pricing(cost_and_licensing: str) -> str:
    """Parse cost_and_licensing string -> 'free' | 'freemium' | 'paid'."""
    s = cost_and_licensing.lower()
    if "open-source" in s or "open source" in s:
        return "free"
    if s.startswith("free") and "freemium" not in s:
        return "free"
    if "free" in s and "trial" not in s and "freemium" not in s:
        return "free"
    if "freemium" in s:
        return "freemium"
    return "paid"


def parse_skill(skill_level: str) -> int:
    """Parse tool's skill_level string -> 1 (beginner) | 2 (intermediate) | 3 (expert)."""
    s = skill_level.lower()
    if "beginner" in s:
        return 1
    if "expert" in s or "advanced" in s or "developer" in s:
        return 3
    return 2  # intermediate default


def user_skill_to_int(skill: str) -> int:
    """Convert user-facing skill label -> int."""
    return {"beginner": 1, "intermediate": 2, "advanced": 3}.get(skill, 2)


def budget_allows(tool_pricing: str, user_budget: str) -> bool:
    """Check if a tool's pricing fits the user's budget preference."""
    if user_budget == "paid":
        return True
    if user_budget == "freemium":
        return tool_pricing in ("free", "freemium")
    if user_budget == "free":
        return tool_pricing == "free"
    return True


def parse_access(access_restrictions: str) -> str:
    """Parse access_restrictions string -> 'public' | 'le_only' | 'restricted'."""
    s = access_restrictions.lower()
    if "public" in s:
        return "public"
    if "strictly" in s:
        return "le_only"
    if "law enforcement" in s or "law-enforcement" in s:
        return "restricted"
    return "restricted"


def parse_coding_requirement(tool: dict) -> str:
    """
    Infer coding requirement from skill/platform/capabilities/docs.
    Returns:
        'no_coding' | 'optional_coding' | 'requires_coding'
    """
    enrichment = _load_enrichment()
    tool_key = _normalise_tool_name(tool.get("tool_name", ""))
    enriched = enrichment.get(tool_key) if tool_key else None
    if isinstance(enriched, dict):
        value = str(enriched.get("coding_requirement", "")).strip().lower()
        if value in {"no_coding", "optional_coding", "requires_coding"}:
            return value

    skill = (tool.get("skill_level") or "").lower()
    platform = (tool.get("platform_and_integration") or "").lower()
    docs = (tool.get("documentation_and_support") or "").lower()
    tags = [str(t).lower() for t in (tool.get("capability_tags") or [])]

    coding_markers = (
        "api", "cli", "command line", "command-line", "developer", "sdk",
        "script", "python", "terminal", "integration",
    )
    no_coding_markers = ("web-based", "web based", "gui", "browser", "extension")

    has_coding_marker = (
        any(marker in skill for marker in coding_markers)
        or any(marker in platform for marker in coding_markers)
        or any(marker in docs for marker in coding_markers)
        or any(any(marker in tag for marker in coding_markers) for tag in tags)
    )
    has_no_coding_marker = (
        any(marker in skill for marker in no_coding_markers)
        or any(marker in platform for marker in no_coding_markers)
    )

    if has_coding_marker and has_no_coding_marker:
        return "optional_coding"
    if has_coding_marker:
        return "requires_coding"
    return "no_coding"


def parse_languages(tool: dict) -> set[str]:
    """
    Extract language availability from explicit metadata or text hints.
    Returns at least one value; defaults to {'Not specified'}.
    """
    enrichment = _load_enrichment()
    tool_key = _normalise_tool_name(tool.get("tool_name", ""))
    enriched = enrichment.get(tool_key) if tool_key else None
    if isinstance(enriched, dict):
        values = enriched.get("languages")
        if isinstance(values, list):
            langs = {str(v).strip() for v in values if str(v).strip()}
            if langs:
                return langs

    langs: set[str] = set()

    meta = tool.get("additional_metadata") or {}
    explicit_candidates: list[str] = []
    if isinstance(meta, dict):
        for key in ("languages", "language", "interface_language"):
            value = meta.get(key)
            if isinstance(value, str):
                explicit_candidates.append(value)
            elif isinstance(value, list):
                explicit_candidates.extend(str(v) for v in value)

    for candidate in explicit_candidates:
        low = candidate.lower()
        for canonical, variants in LANGUAGE_KEYWORDS.items():
            if any(v in low for v in variants):
                langs.add(canonical)
        if "multilingual" in low:
            langs.add("Multilingual")

    searchable = " ".join(
        [
            str(tool.get("platform_and_integration", "")),
            str(tool.get("documentation_and_support", "")),
            str(meta),
        ]
    ).lower()
    for canonical, variants in LANGUAGE_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(v)}\b", searchable) for v in variants):
            langs.add(canonical)
    if "multilingual" in searchable:
        langs.add("Multilingual")

    if not langs:
        langs.add("Not specified")
    return langs
