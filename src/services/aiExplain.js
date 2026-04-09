/**
 * Calls the local /api/explain proxy which forwards to AWS Bedrock Mistral.
 * Returns a string brief, or null on failure (silent degrade).
 */
export async function getCaseAnalysisBrief(caseInput, top5Tools) {
  try {
    const res = await fetch("/api/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ caseInput, top5Tools }),
    });

    if (!res.ok) return null;

    const data = await res.json();
    return data.brief || null;
  } catch {
    return null; // silent degrade — results still show without the brief
  }
}
