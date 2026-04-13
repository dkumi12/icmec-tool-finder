"""
recommend.py
Core scoring engine for InvestiTools.

Scores all tools against the investigator's case input using 5 additive
signals + 1 access gate. Returns the top N tools with scores and
human-readable match reasons. No AI, fully deterministic.
"""

from dataclasses import dataclass, field

from .tag_maps import get_relevant_tags, INVESTIGATION_TAG_MAP
from .normalise import (
    parse_pricing,
    parse_skill,
    user_skill_to_int,
    budget_allows,
    parse_access,
)


@dataclass
class UserQuery:
    investigation_types: list[str]
    budget: str  # "free" | "freemium" | "paid"
    skill_level: str  # "beginner" | "intermediate" | "advanced"
    input_types: list[str]
    urgency: str  # "immediate" | "days" | "weeks"
    is_law_enforcement: bool = False


@dataclass
class ScoredTool:
    tool: dict
    score: int = 0
    match_reasons: list[str] = field(default_factory=list)


def recommend_tools(
    tools: list[dict],
    query: UserQuery,
    top_n: int = 5,
) -> list[ScoredTool]:
    """
    Score all tools and return the top_n results sorted by score descending.

    Scoring signals (additive points):
        Signal 1: Investigation type match   +3 per tag hit, cap +9
        Signal 2: Budget match               +2 or -2
        Signal 3: Skill level match          +2 or +0
        Signal 4: Evidence/input type match  +1 per hit, cap +3
        Signal 5: Urgency bonus              +1
        Access gate:                         -5 if restricted + non-LE

    Score range: -7 to +17.
    """
    # Pre-compute expanded tag sets from user selections
    inv_tags, inp_tags = get_relevant_tags(
        query.investigation_types, query.input_types
    )

    user_skill = user_skill_to_int(query.skill_level)

    scored: list[ScoredTool] = []

    for tool in tools:
        score = 0
        reasons: list[str] = []

        tool_tags = set(t.lower() for t in (tool.get("capability_tags") or []))
        tool_access = parse_access(tool.get("access_restrictions", ""))
        tool_pricing = parse_pricing(tool.get("cost_and_licensing", ""))

        # ── ACCESS GATE ──────────────────────────────────────────
        if tool_access in ("le_only", "restricted") and not query.is_law_enforcement:
            score -= 5
            reasons.append("⚠️ Access may be restricted to law enforcement")

        # ── SIGNAL 1: Investigation type match (+3 per hit, cap +9) ──
        hits = tool_tags & inv_tags
        if hits:
            inv_score = min(len(hits) * 3, 9)
            score += inv_score
            # Map hit tags back to which investigation types they fired
            fired_types = [
                t for t in query.investigation_types
                if any(tag in hits for tag in INVESTIGATION_TAG_MAP.get(t, []))
            ]
            if fired_types:
                reasons.append(f"Matches investigation: {', '.join(fired_types)}")
            else:
                reasons.append(f"Matches {len(hits)} relevant capabilities")

        # ── SIGNAL 2: Budget match (+2 / -2) ─────────────────────
        if query.budget:
            if budget_allows(tool_pricing, query.budget):
                score += 2
                reasons.append(f"Fits your {query.budget} budget ({tool_pricing} tool)")
            else:
                score -= 2
                reasons.append(f"⚠️ Outside budget (tool is {tool_pricing})")

        # ── SIGNAL 3: Skill level match (+2) ─────────────────────
        if query.skill_level:
            tool_skill = parse_skill(tool.get("skill_level", ""))
            if tool_skill <= user_skill:
                score += 2
                # Clean up the skill display: take text before first parenthesis
                skill_display = tool.get("skill_level", "").split("(")[0].strip()
                reasons.append(f"Matches your skill level ({skill_display})")
            else:
                skill_display = tool.get("skill_level", "").split("(")[0].strip()
                reasons.append(f"May require higher skill ({skill_display})")

        # ── SIGNAL 4: Evidence/input type match (+1 per hit, cap +3) ──
        if inp_tags:
            input_hits = tool_tags & inp_tags
            input_score = min(len(input_hits), 3)
            if input_score > 0:
                score += input_score
                reasons.append(f"Handles {input_score} of your evidence types")

        # ── SIGNAL 5: Urgency bonus (+1) ─────────────────────────
        if query.urgency == "immediate":
            if tool_pricing == "free" and tool_access == "public":
                score += 1
                reasons.append("Free and publicly available — good for urgent cases")

        scored.append(ScoredTool(tool=tool, score=score, match_reasons=reasons))

    # Sort: score descending, ties broken alphabetically by tool name
    scored.sort(
        key=lambda s: (-s.score, (s.tool.get("tool_name") or "").strip().lower())
    )

    return scored[:top_n]
