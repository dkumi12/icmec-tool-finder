"""
File-based community ratings helpers.
Stores individual rating submissions without login or database.
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

_ROOT = pathlib.Path(__file__).parent.parent
_RATINGS_LOG_PATH = _ROOT / "data" / "ratings_log.jsonl"
_LEGACY_RATINGS_PATH = _ROOT / "data" / "ratings.json"


def _normalise_tool_name(tool_name: str) -> str:
    value = tool_name.strip()
    if not value:
        raise ValueError("tool_name is required.")
    return value


def _normalise_investigator(investigator: str) -> str:
    value = investigator.strip()
    if not value:
        raise ValueError("investigator name or alias is required.")
    return value


def _identity_key(investigator: str) -> str:
    return _normalise_investigator(investigator).lower()


def _validate_stars(stars: int) -> int:
    if stars < 1 or stars > 5:
        raise ValueError("stars must be between 1 and 5.")
    return stars


def submit_rating(tool_name: str, investigator: str, stars: int, source: str) -> bool:
    normalised_tool = _normalise_tool_name(tool_name)
    normalised_investigator = _normalise_investigator(investigator)
    investigator_key = _identity_key(normalised_investigator)
    normalised_stars = _validate_stars(stars)
    normalised_source = source.strip() or "unknown"

    existing = get_investigator_tool_rating(normalised_tool, normalised_investigator)
    if existing == normalised_stars:
        return False

    entries = _load_log_entries()
    filtered_entries: list[dict] = []
    for entry in entries:
        if entry.get("tool_name") != normalised_tool:
            filtered_entries.append(entry)
            continue
        if _identity_key(str(entry.get("investigator", ""))) == investigator_key:
            continue
        filtered_entries.append(entry)

    filtered_entries.append(
        {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "tool_name": normalised_tool,
            "investigator": normalised_investigator,
            "stars": normalised_stars,
            "source": normalised_source,
        }
    )
    _write_log_entries(filtered_entries)
    return True


def _load_log_entries() -> list[dict]:
    if not _RATINGS_LOG_PATH.exists():
        return []

    entries: list[dict] = []
    with open(_RATINGS_LOG_PATH, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid rating record at line {line_number}.") from exc
            entries.append(item)
    return entries


def _write_log_entries(entries: list[dict]) -> None:
    _RATINGS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_RATINGS_LOG_PATH, "w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _legacy_totals_for_tool(tool_name: str) -> tuple[int, int]:
    if not _LEGACY_RATINGS_PATH.exists():
        return 0, 0

    with open(_LEGACY_RATINGS_PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    ratings = data.get(tool_name, [])
    total = sum(int(value) for value in ratings)
    count = len(ratings)
    return total, count


def get_tool_rating_summary(tool_name: str) -> tuple[float | None, int]:
    normalised_tool = _normalise_tool_name(tool_name)
    total, count = _legacy_totals_for_tool(normalised_tool)
    latest_by_investigator: dict[str, int] = {}
    for entry in _load_log_entries():
        if entry.get("tool_name") != normalised_tool:
            continue
        key = _identity_key(str(entry.get("investigator", "")))
        latest_by_investigator[key] = int(entry.get("stars", 0))

    total += sum(latest_by_investigator.values())
    count += len(latest_by_investigator)

    if count == 0:
        return None, 0
    return round(total / count, 1), count


def get_investigator_tool_rating(tool_name: str, investigator: str) -> int | None:
    normalised_tool = _normalise_tool_name(tool_name)
    normalised_investigator = _identity_key(investigator)

    latest: int | None = None
    for entry in _load_log_entries():
        if entry.get("tool_name") != normalised_tool:
            continue
        if _identity_key(str(entry.get("investigator", ""))) != normalised_investigator:
            continue
        latest = int(entry.get("stars", 0))
    return latest
