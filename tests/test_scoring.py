"""
Tests for the Investiqo scoring engine, normalisation, and tag maps.
Run with: python -m pytest tests/ -v
"""

import json
import pathlib
import pytest

from scoring.recommend import recommend_tools, UserQuery
from scoring.normalise import (
    parse_pricing,
    parse_skill,
    user_skill_to_int,
    budget_allows,
    parse_access,
    parse_coding_requirement,
    parse_languages,
)
from scoring.tag_maps import INVESTIGATION_TAG_MAP, INPUT_TAG_MAP, get_relevant_tags


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def tools():
    data_path = pathlib.Path(__file__).parent.parent / "data" / "tools.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Normalise Tests ─────────────────────────────────────────────────────────

class TestParsePricing:
    def test_free_open_source(self):
        assert parse_pricing("Free / Open-source") == "free"

    def test_free_for_orgs(self):
        assert parse_pricing("Free for qualifying organizations") == "free"

    def test_paid_enterprise(self):
        assert parse_pricing("Enterprise / Subscription (approx. $4,000+)") == "paid"

    def test_freemium(self):
        assert parse_pricing("Freemium (limited free tier)") == "freemium"


class TestParseSkill:
    def test_beginner(self):
        assert parse_skill("Beginner") == 1

    def test_intermediate(self):
        assert parse_skill("Intermediate") == 2

    def test_expert(self):
        assert parse_skill("Expert") == 3

    def test_beginner_to_intermediate(self):
        assert parse_skill("Beginner to Intermediate") == 1

    def test_enterprise_api_defaults_intermediate(self):
        assert parse_skill("Enterprise API") == 2


class TestUserSkillToInt:
    def test_beginner(self):
        assert user_skill_to_int("beginner") == 1

    def test_intermediate(self):
        assert user_skill_to_int("intermediate") == 2

    def test_advanced(self):
        assert user_skill_to_int("advanced") == 3


class TestBudgetAllows:
    def test_free_allows_free(self):
        assert budget_allows("free", "free") is True

    def test_paid_blocked_by_free(self):
        assert budget_allows("paid", "free") is False

    def test_paid_allows_paid(self):
        assert budget_allows("paid", "paid") is True

    def test_freemium_allows_freemium(self):
        assert budget_allows("freemium", "freemium") is True

    def test_free_allows_freemium(self):
        assert budget_allows("free", "freemium") is True

    def test_freemium_blocked_by_free(self):
        assert budget_allows("freemium", "free") is False


class TestParseAccess:
    def test_public(self):
        assert parse_access("Public") == "public"

    def test_strictly_le(self):
        assert parse_access("Strictly INTERPOL member law enforcement agencies.") == "le_only"

    def test_law_enforcement(self):
        assert parse_access("Law-enforcement and vetted corporate organizations.") == "restricted"


class TestParseCodingRequirement:
    def test_requires_coding_from_api(self):
        tool = {
            "skill_level": "Developer",
            "platform_and_integration": "API",
            "capability_tags": ["api_integration"],
            "documentation_and_support": "API docs",
        }
        assert parse_coding_requirement(tool) == "requires_coding"

    def test_optional_coding_when_web_and_api(self):
        tool = {
            "skill_level": "Intermediate",
            "platform_and_integration": "Web-based, API",
            "capability_tags": [],
            "documentation_and_support": "",
        }
        assert parse_coding_requirement(tool) == "optional_coding"

    def test_no_coding_defaults(self):
        tool = {
            "skill_level": "Beginner",
            "platform_and_integration": "Web-based",
            "capability_tags": [],
            "documentation_and_support": "User guides",
        }
        assert parse_coding_requirement(tool) == "no_coding"


class TestParseLanguages:
    def test_explicit_language_metadata(self):
        tool = {"additional_metadata": {"language": "English and Spanish"}}
        assert parse_languages(tool) == {"English", "Spanish"}

    def test_multilingual_hint(self):
        tool = {"additional_metadata": {"languages": "Multilingual"}}
        assert parse_languages(tool) == {"Multilingual"}

    def test_not_specified_fallback(self):
        tool = {"additional_metadata": {"focus": "OSINT"}}
        assert parse_languages(tool) == {"Not specified"}


# ── Tag Map Tests ───────────────────────────────────────────────────────────

class TestTagMaps:
    def test_investigation_types_exist(self):
        assert len(INVESTIGATION_TAG_MAP) == 14  # Self-Generated CSAM merged into CSAM detection

    def test_input_types_exist(self):
        assert len(INPUT_TAG_MAP) == 14

    def test_key_investigation_types(self):
        for key in ["CSAM detection", "online grooming", "crypto tracing"]:
            assert key in INVESTIGATION_TAG_MAP

    def test_key_input_types(self):
        for key in ["Image / photo", "Mobile device", "Chat logs"]:
            assert key in INPUT_TAG_MAP

    def test_get_relevant_tags_returns_sets(self):
        inv, inp = get_relevant_tags(["CSAM detection"], ["Image / photo"])
        assert isinstance(inv, set)
        assert isinstance(inp, set)
        assert len(inv) > 0
        assert len(inp) > 0

    def test_get_relevant_tags_empty_input(self):
        inv, inp = get_relevant_tags([], [])
        assert len(inv) == 0
        assert len(inp) == 0


# ── Scoring Engine Tests ────────────────────────────────────────────────────

class TestRecommendTools:
    def test_returns_top_n(self, tools):
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="free",
            skill_level="intermediate",
            input_types=["Image / photo"],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools(tools, query, top_n=5)
        assert len(results) == 5

    def test_top_20_returns_more_than_5(self, tools):
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="free",
            skill_level="intermediate",
            input_types=["Image / photo", "Mobile device"],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools(tools, query, top_n=20)
        assert len(results) > 5

    def test_scores_descending(self, tools):
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="free",
            skill_level="intermediate",
            input_types=["Image / photo"],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools(tools, query, top_n=10)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_match_reasons_populated(self, tools):
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="free",
            skill_level="intermediate",
            input_types=["Image / photo"],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools(tools, query, top_n=5)
        for r in results:
            assert len(r.match_reasons) > 0

    def test_le_user_no_access_penalty(self, tools):
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="paid",
            skill_level="advanced",
            input_types=["Image / photo"],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools(tools, query, top_n=5)
        for r in results:
            for reason in r.match_reasons:
                assert "restricted to law enforcement" not in reason

    def test_non_le_user_gets_access_penalty(self, tools):
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="paid",
            skill_level="advanced",
            input_types=["Image / photo"],
            urgency="immediate",
            is_law_enforcement=False,
        )
        results = recommend_tools(tools, query, top_n=20)
        penalised = [r for r in results if any("restricted" in reason for reason in r.match_reasons)]
        assert len(penalised) > 0

    def test_empty_investigation_types(self, tools):
        query = UserQuery(
            investigation_types=[],
            budget="free",
            skill_level="beginner",
            input_types=["Image / photo"],
            urgency="days",
            is_law_enforcement=False,
        )
        results = recommend_tools(tools, query, top_n=5)
        assert len(results) == 5

    def test_crypto_tracing_scenario(self, tools):
        query = UserQuery(
            investigation_types=["crypto tracing"],
            budget="free",
            skill_level="beginner",
            input_types=["Crypto wallet address"],
            urgency="immediate",
            is_law_enforcement=False,
        )
        results = recommend_tools(tools, query, top_n=5)
        assert len(results) == 5
        # Top result should have a positive score
        assert results[0].score > 0

    def test_filter_no_coding_removes_developer_only_tools(self, tools):
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="paid",
            skill_level="advanced",
            input_types=["Image / photo"],
            urgency="days",
            is_law_enforcement=True,
            coding_requirement="no_coding",
        )
        results = recommend_tools(tools, query, top_n=20)
        assert len(results) > 0
        assert all(parse_coding_requirement(r.tool) == "no_coding" for r in results)

    def test_filter_language_not_specified_with_specific_language(self, tools):
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="paid",
            skill_level="advanced",
            input_types=["Image / photo"],
            urgency="days",
            is_law_enforcement=True,
            languages=["Spanish"],
        )
        results = recommend_tools(tools, query, top_n=20)
        assert len(results) == 0
