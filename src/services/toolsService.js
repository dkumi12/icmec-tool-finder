/**
 * Tools data service
 * Loads tools.json and provides search/filter helpers
 */

let _tools = null;

export async function loadTools() {
  if (_tools) return _tools;
  const res = await fetch("/data/tools.json");
  _tools = await res.json();
  return _tools;
}

export function filterTools(tools, filters = {}) {
  const { search, category, pricing, skillLevel, platform, investigationType } = filters;

  return tools.filter((tool) => {
    if (search) {
      const q = search.toLowerCase();
      const match =
        tool.name?.toLowerCase().includes(q) ||
        tool.description?.toLowerCase().includes(q) ||
        tool.tags?.some((t) => t.toLowerCase().includes(q));
      if (!match) return false;
    }
    if (category && tool.category !== category) return false;
    if (pricing && tool.pricing !== pricing) return false;
    if (skillLevel && tool.skillLevel !== skillLevel) return false;
    if (platform && tool.platform !== platform) return false;
    if (investigationType && !tool.investigationTypes?.includes(investigationType)) return false;
    return true;
  });
}
