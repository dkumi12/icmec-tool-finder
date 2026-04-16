"""
Tests for the Investiqo scoring engine, normalisation, and tag maps.
Run with: python -m pytest tests/ -v
"""

import json
import pathlib
import pytest

from scoring.recommend import recommend_tools, UserQuery, score_pct
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

    def test_non_le_user_restricted_tools_excluded(self, tools):
        """LE-only / restricted tools must not appear at all for non-LE users."""
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="paid",
            skill_level="advanced",
            input_types=["Image / photo"],
            urgency="immediate",
            is_law_enforcement=False,
        )
        results = recommend_tools(tools, query, top_n=len(tools))
        from scoring.normalise import parse_access
        restricted_in_results = [
            r for r in results
            if parse_access(r.tool.get("access_restrictions") or "") in ("le_only", "restricted")
        ]
        assert len(restricted_in_results) == 0

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


# ── Error Handling / Robustness Tests ──────────────────────────────────────
# Ensures no raw Python errors appear during the demo.

class TestScorePct:
    """score_pct must never crash or return values outside 0–100."""

    def test_max_score(self):
        assert score_pct(17) == 100

    def test_min_score(self):
        assert score_pct(-7) == 0

    def test_zero_score(self):
        assert score_pct(0) == 29

    def test_above_max_clamped(self):
        assert score_pct(50) == 100

    def test_below_min_clamped(self):
        assert score_pct(-20) == 0

    def test_returns_int(self):
        assert isinstance(score_pct(10), int)


class TestNormaliseMissingFields:
    """Functions must handle missing / None / empty fields without crashing."""

    def test_parse_pricing_empty(self):
        assert parse_pricing("") == "paid"

    def test_parse_skill_empty(self):
        assert parse_skill("") == 2

    def test_parse_access_empty(self):
        assert parse_access("") == "restricted"

    def test_user_skill_unknown(self):
        assert user_skill_to_int("expert") == 2

    def test_parse_coding_empty_tool(self):
        result = parse_coding_requirement({})
        assert result in ("no_coding", "optional_coding", "requires_coding")

    def test_parse_coding_none_fields(self):
        tool = {"skill_level": None, "platform_and_integration": None,
                "capability_tags": None, "documentation_and_support": None}
        result = parse_coding_requirement(tool)
        assert result in ("no_coding", "optional_coding", "requires_coding")

    def test_parse_languages_empty_tool(self):
        result = parse_languages({})
        assert isinstance(result, set)
        assert len(result) >= 1

    def test_parse_languages_none_metadata(self):
        result = parse_languages({"additional_metadata": None})
        assert isinstance(result, set)
        assert len(result) >= 1

    def test_parse_languages_string_metadata(self):
        """additional_metadata should be a dict but might be a string in bad data."""
        result = parse_languages({"additional_metadata": "some text"})
        assert isinstance(result, set)
        assert len(result) >= 1


class TestScoringEdgeCases:
    """Scoring engine must never crash regardless of tool data quality."""

    def test_tool_with_no_fields(self):
        """Completely empty tool dict should score without errors."""
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="free",
            skill_level="beginner",
            input_types=[],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools([{}], query, top_n=5)
        assert len(results) == 1
        assert isinstance(results[0].score, int)

    def test_tool_with_none_values(self):
        """Tool with all None values should not crash."""
        tool = {
            "tool_name": None, "vendor": None, "url": None,
            "cost_and_licensing": None, "skill_level": None,
            "platform_and_integration": None, "access_restrictions": None,
            "capability_tags": None, "status": None,
            "additional_metadata": None,
        }
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="free",
            skill_level="beginner",
            input_types=["Image / photo"],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools([tool], query, top_n=5)
        assert len(results) == 1

    def test_tool_with_empty_strings(self):
        """Tool with all empty strings should not crash."""
        tool = {
            "tool_name": "", "vendor": "", "url": "",
            "cost_and_licensing": "", "skill_level": "",
            "platform_and_integration": "", "access_restrictions": "",
            "capability_tags": [], "status": "",
        }
        query = UserQuery(
            investigation_types=["crypto tracing"],
            budget="paid",
            skill_level="advanced",
            input_types=["Crypto wallet address"],
            urgency="days",
            is_law_enforcement=True,
        )
        results = recommend_tools([tool], query, top_n=5)
        assert len(results) == 1

    def test_unknown_investigation_type(self):
        """Bogus investigation type should not crash, just return no tag matches."""
        query = UserQuery(
            investigation_types=["nonexistent_type"],
            budget="free",
            skill_level="beginner",
            input_types=[],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools([{"capability_tags": ["csam_detection"]}], query, top_n=5)
        assert len(results) == 1

    def test_unknown_input_type(self):
        """Bogus input type should not crash."""
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="free",
            skill_level="beginner",
            input_types=["Alien spaceship"],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools([{"capability_tags": ["csam_detection"]}], query, top_n=5)
        assert len(results) == 1


class TestTagMapRobustness:
    """Tag maps must handle unexpected inputs gracefully."""

    def test_get_relevant_tags_unknown_types(self):
        inv, inp = get_relevant_tags(["fake_type"], ["fake_evidence"])
        assert isinstance(inv, set)
        assert isinstance(inv, set)
        assert len(inv) == 0
        assert len(inp) == 0

    def test_all_investigation_tags_are_strings(self):
        for key, tags in INVESTIGATION_TAG_MAP.items():
            assert isinstance(key, str), f"Key {key} is not a string"
            for tag in tags:
                assert isinstance(tag, str), f"Tag {tag} in {key} is not a string"

    def test_all_input_tags_are_strings(self):
        for key, tags in INPUT_TAG_MAP.items():
            assert isinstance(key, str), f"Key {key} is not a string"
            for tag in tags:
                assert isinstance(tag, str), f"Tag {tag} in {key} is not a string"

    def test_no_duplicate_investigation_keys(self):
        keys = list(INVESTIGATION_TAG_MAP.keys())
        assert len(keys) == len(set(keys))

    def test_no_duplicate_input_keys(self):
        keys = list(INPUT_TAG_MAP.keys())
        assert len(keys) == len(set(keys))


class TestToolsJsonIntegrity:
    """The tools.json file must be well-formed and every tool scoreable."""

    def test_all_tools_have_name(self, tools):
        for i, tool in enumerate(tools):
            name = (tool.get("tool_name") or "").strip()
            assert name, f"Tool at index {i} has no tool_name"

    def test_all_tools_have_capability_tags_list(self, tools):
        for tool in tools:
            tags = tool.get("capability_tags")
            assert tags is None or isinstance(tags, list), (
                f"{tool.get('tool_name')}: capability_tags must be a list or absent"
            )

    def test_all_tools_scoreable(self, tools):
        """Every single tool must be scoreable without crashing."""
        query = UserQuery(
            investigation_types=["CSAM detection", "crypto tracing", "digital forensics"],
            budget="paid",
            skill_level="advanced",
            input_types=["Image / photo", "Mobile device"],
            urgency="immediate",
            is_law_enforcement=True,
        )
        results = recommend_tools(tools, query, top_n=len(tools))
        assert len(results) > 0
        for r in results:
            assert isinstance(r.score, int)
            assert isinstance(r.match_reasons, list)

    def test_all_tools_status_valid(self, tools):
        valid_statuses = {"active", "deprecated", "unverified"}
        for tool in tools:
            status = (tool.get("status") or "active").lower()
            assert status in valid_statuses, (
                f"{tool.get('tool_name')}: status '{status}' not in {valid_statuses}"
            )

    def test_score_pct_on_all_real_scores(self, tools):
        """score_pct must return 0–100 for every real tool score."""
        query = UserQuery(
            investigation_types=["CSAM detection"],
            budget="free",
            skill_level="beginner",
            input_types=[],
            urgency="immediate",
            is_law_enforcement=False,
        )
        results = recommend_tools(tools, query, top_n=len(tools))
        for r in results:
            pct = score_pct(r.score)
            assert 0 <= pct <= 100, f"score_pct({r.score}) = {pct} out of range"
