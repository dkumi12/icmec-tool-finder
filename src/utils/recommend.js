/**
 * Recommendation engine — scores tools against a case input
 * Returns tools sorted by relevance score (highest first)
 */

const SKILL_ORDER = { beginner: 0, intermediate: 1, advanced: 2 };

/**
 * @param {Object} caseInput - { investigationTypes, budget, skillLevel, inputs, urgency }
 * @param {Array}  tools     - full tools array from tools.json
 * @returns {Array}          - tools with .score and .matchReasons, sorted desc
 */
export function recommendTools(caseInput, tools) {
  const { investigationTypes = [], budget, skillLevel, inputs = [], urgency } = caseInput;

  const scored = tools.map((tool) => {
    let score = 0;
    const matchReasons = [];

    // +3 per matching investigation type (most important signal)
    const invMatches = investigationTypes.filter((t) =>
      tool.investigationTypes?.includes(t)
    );
    if (invMatches.length > 0) {
      score += invMatches.length * 3;
      matchReasons.push(`Matches investigation: ${invMatches.join(", ")}`);
    }

    // +2 if pricing fits budget
    const budgetOk =
      budget === "paid" || // paid users can use anything
      (budget === "freemium" && ["free", "freemium"].includes(tool.pricing)) ||
      (budget === "free" && tool.pricing === "free");
    if (budgetOk) {
      score += 2;
      matchReasons.push(`Fits budget (${tool.pricing})`);
    } else {
      score -= 2; // penalise tools outside budget
    }

    // +2 if skill level is within user capability
    const userSkillNum = SKILL_ORDER[skillLevel] ?? 1;
    const toolSkillNum = SKILL_ORDER[tool.skillLevel] ?? 1;
    if (toolSkillNum <= userSkillNum) {
      score += 2;
      matchReasons.push(`Within skill level (${tool.skillLevel})`);
    }

    // +1 per matching input type
    if (inputs.length > 0 && tool.input) {
      const toolInput = tool.input.toLowerCase();
      const inputMatches = inputs.filter((i) => toolInput.includes(i.toLowerCase()));
      if (inputMatches.length > 0) {
        score += inputMatches.length;
        matchReasons.push(`Works with: ${inputMatches.join(", ")}`);
      }
    }

    // +1 for free tools when urgency is high (no signup delays)
    if (urgency === "immediate" && tool.pricing === "free" && !tool.requiresRegistration) {
      score += 1;
      matchReasons.push("Ready to use immediately (free, no registration)");
    }

    // +1 per matching tag
    if (tool.tags?.length > 0 && investigationTypes.length > 0) {
      const tagMatches = tool.tags.filter((tag) =>
        investigationTypes.some((t) => t.toLowerCase().includes(tag.toLowerCase()))
      );
      score += tagMatches.length;
    }

    return { ...tool, score, matchReasons };
  });

  // Filter out zero-score tools, sort by score desc
  // Minimum score of 3 ensures at least one meaningful match
  return scored
    .filter((t) => t.score >= 3)
    .sort((a, b) => b.score - a.score)
    .slice(0, 30); // Cap at top 30 most relevant
}

/**
 * Get all unique values for a given field across all tools
 * Used to populate filter dropdowns
 */
export function getFilterOptions(tools, field) {
  const values = new Set();
  tools.forEach((tool) => {
    const val = tool[field];
    if (Array.isArray(val)) val.forEach((v) => values.add(v));
    else if (val) values.add(val);
  });
  return Array.from(values).sort();
}
