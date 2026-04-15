"""
rule_based.py
Advanced scoring engine for InvestiTools using weighted normalization.
Calculates a final score from 0 to 100 based on weighted signals.
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

# 1. DEFINE GLOBAL WEIGHTS (Must sum to 1.0)
# These prioritize which factors are most important for a recommendation.
WEIGHTS = {
    "capability": 0.40,  # Match for the core investigation type
    "input": 0.15,  # Match for the evidence/input types
    "budget": 0.20,  # Financial suitability
    "skill": 0.15,  # Technical expertise alignment
    "access": 0.10,  # Law Enforcement vs Public restriction
}


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


def generate_explanation(
    match_ratio: float,
    input_ratio: float,
    budget_score: float,
    skill_score: float,
    access_score: float,
    query: UserQuery,
) -> list[str]:
    """Generates human-readable strings explaining the score components."""
    reasons = []

    if match_ratio > 0.8:
        reasons.append("Matches nearly all required investigation capabilities.")
    elif match_ratio > 0.4:
        reasons.append(
            f"Supports {int(match_ratio * 100)}% of requested investigation features."
        )

    if input_ratio > 0.5:
        reasons.append(
            f"Strong evidence handling ({int(input_ratio * 100)}% coverage)."
        )

    if budget_score == 1.0:
        reasons.append(f"Fits your {query.budget} budget perfectly.")
    elif budget_score == 0.5:
        reasons.append("Available as a freemium version (partial budget match).")

    if skill_score == 1.0:
        reasons.append(f"Optimized for {query.skill_level} skill level.")
    elif skill_score < 1.0:
        reasons.append("⚠️ Requires higher technical expertise than specified.")

    if access_score == 0.0:
        reasons.append("⚠️ Access is likely restricted to Law Enforcement.")

    return reasons if reasons else ["General match for your criteria."]


def recommend_tools(
    tools: list[dict],
    query: UserQuery,
    top_n: int = 5,
) -> list[ScoredTool]:
    """
    Core weighted engine. Scores tools 0-100 by calculating normalized
    ratios for each category and applying weights.
    """
    # Pre-compute expanded tag sets from user selections
    inv_tags, inp_tags = get_relevant_tags(query.investigation_types, query.input_types)
    user_skill_val = user_skill_to_int(query.skill_level)

    scored_results: list[ScoredTool] = []

    for tool in tools:
        total_normalized = 0.0

        tool_tags = set(t.lower() for t in (tool.get("capability_tags") or []))
        tool_access = parse_access(tool.get("access_restrictions", ""))
        tool_pricing = parse_pricing(tool.get("cost_and_licensing", ""))
        tool_skill_val = parse_skill(tool.get("skill_level", ""))

        # --- 1. CAPABILITY RATIO ---
        # How much of the investigation's needs does this tool cover?
        match_ratio = 1.0
        if inv_tags:
            match_ratio = len(tool_tags & inv_tags) / len(inv_tags)
        total_normalized += match_ratio * WEIGHTS["capability"]

        # --- 2. INPUT RATIO ---
        # Does the tool support the specific evidence types provided?
        input_ratio = 1.0
        if inp_tags:
            input_ratio = len(tool_tags & inp_tags) / len(inp_tags)
        total_normalized += input_ratio * WEIGHTS["input"]

        # --- 3. BUDGET SCORE ---
        # 1.0 for match, 0.5 for freemium compromise, 0.0 for mismatch
        budget_score = 0.0
        if budget_allows(tool_pricing, query.budget):
            budget_score = 1.0
        elif query.budget == "free" and tool_pricing == "freemium":
            budget_score = 0.5
        total_normalized += budget_score * WEIGHTS["budget"]

        # --- 4. SKILL SCORE ---
        # Uses a gradient penalty: -0.4 for every level higher than user's skill
        if tool_skill_val <= user_skill_val:
            skill_score = 1.0
        else:
            skill_score = max(0.0, 1.0 - (tool_skill_val - user_skill_val) * 0.4)
        total_normalized += skill_score * WEIGHTS["skill"]

        # --- 5. ACCESS SCORE ---
        # 1.0 if accessible, 0.0 if user doesn't meet the restriction level
        user_access_rank = 2 if query.is_law_enforcement else 0
        tool_access_rank = 2 if tool_access in ("le_only", "restricted") else 0

        access_score = 1.0 if tool_access_rank <= user_access_rank else 0.0
        total_normalized += access_score * WEIGHTS["access"]

        # FINAL CALCULATION
        final_score = int(total_normalized * 100)

        reasons = generate_explanation(
            match_ratio, input_ratio, budget_score, skill_score, access_score, query
        )

        scored_results.append(
            ScoredTool(tool=tool, score=final_score, match_reasons=reasons)
        )

    # Sort by score descending, then by name for ties
    scored_results.sort(
        key=lambda s: (-s.score, (s.tool.get("tool_name") or "").lower())
    )

    return scored_results[:top_n]
