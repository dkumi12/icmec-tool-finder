import { Box, Typography, Grid, Button, Divider, Alert, Chip } from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ToolCard from "./ToolCard";
import CaseAnalysisBrief from "./CaseAnalysisBrief";

export default function RecommendationResults({ results, caseInput, onReset, brief, briefLoading }) {
  if (!results.length) {
    return (
      <Box>
        <Alert severity="info" sx={{ mb: 2 }}>
          No tools matched your case criteria. Try broadening your filters.
        </Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={onReset}>
          Try Again
        </Button>
      </Box>
    );
  }

  // Only show top 30, group by category
  const top = results.slice(0, 30);
  const grouped = top.reduce((acc, tool) => {
    const cat = tool.category || "Other";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(tool);
    return acc;
  }, {});

  // Score → label
  const getMatchLabel = (score) => {
    if (score >= 9) return { label: "Excellent match", color: "success" };
    if (score >= 6) return { label: "Strong match",    color: "primary" };
    if (score >= 3) return { label: "Good match",      color: "default" };
    return           { label: "Partial match",         color: "default" };
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h6" fontWeight={700}>
            Top {top.length} recommended tools
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sorted by relevance · Investigation: {caseInput?.investigationTypes?.join(", ")}
          </Typography>
        </Box>
        <Button startIcon={<ArrowBackIcon />} onClick={onReset} variant="outlined" size="small">
          New Search
        </Button>
      </Box>

      {/* AI Case Analysis Brief */}
      <CaseAnalysisBrief brief={brief} loading={briefLoading} />

      {Object.entries(grouped).map(([category, tools]) => (
        <Box key={category} mb={4}>
          <Typography variant="subtitle1" fontWeight={700} color="primary" mb={1}>
            {category} ({tools.length})
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            {tools.map((tool) => (
              <Grid item xs={12} sm={6} md={4} key={tool.id}>
                <ToolCard
                  tool={tool}
                  showScore
                  matchLabel={getMatchLabel(tool.score)}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      ))}
    </Box>
  );
}
