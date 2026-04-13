"""
normalise.py
Converts descriptive string fields in tools.json into clean values
the scoring engine can compare.
"""


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
