import { useState, useCallback } from "react";
import { recommendTools } from "../utils/recommend";
import { getCaseAnalysisBrief } from "../services/aiExplain";

export function useRecommendations(tools) {
  const [results, setResults] = useState([]);
  const [caseInput, setCaseInput] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [brief, setBrief] = useState(null);
  const [briefLoading, setBriefLoading] = useState(false);

  const runRecommendation = useCallback(
    async (input) => {
      setCaseInput(input);
      const ranked = recommendTools(input, tools);
      setResults(ranked);
      setHasSearched(true);

      // Fire AI brief asynchronously — results show immediately, brief fills in after
      const top5 = ranked.slice(0, 5);
      if (top5.length > 0) {
        setBriefLoading(true);
        setBrief(null);
        const result = await getCaseAnalysisBrief(input, top5);
        setBrief(result);
        setBriefLoading(false);
      }
    },
    [tools]
  );

  const reset = useCallback(() => {
    setResults([]);
    setCaseInput(null);
    setHasSearched(false);
    setBrief(null);
    setBriefLoading(false);
  }, []);

  return { results, caseInput, hasSearched, runRecommendation, reset, brief, briefLoading };
}
