import { useState } from "react";
import {
  Box, Typography, Grid, Card, CardContent, CardActions,
  Chip, Stack, Button, Paper, Alert, Divider
} from "@mui/material";
import SchoolIcon from "@mui/icons-material/School";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import TipsAndUpdatesIcon from "@mui/icons-material/TipsAndUpdates";

const LEVEL_COLOR = { beginner: "success", intermediate: "warning", advanced: "error" };
const LEVEL_BORDER = { beginner: "#2e7d32", intermediate: "#e65100", advanced: "#b71c1c" };

function TutorialDetail({ tutorial, onBack }) {
  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={onBack} sx={{ mb: 2 }}>
        Back to Tutorials
      </Button>

      <Paper elevation={0} sx={{ p: 3, mb: 3, bgcolor: "#f8f9ff", borderRadius: 2, borderLeft: "4px solid #1a3a6b" }}>
        <Typography variant="h5" fontWeight={700} mb={1}>
          {tutorial.title}
        </Typography>
        <Typography variant="body2" color="text.secondary" mb={2}>
          {tutorial.summary}
        </Typography>
        <Stack direction="row" flexWrap="wrap" gap={1} alignItems="center">
          <Chip label={tutorial.level} size="small" color={LEVEL_COLOR[tutorial.level]} />
          <Chip icon={<AccessTimeIcon />} label={tutorial.duration} size="small" variant="outlined" />
          <Chip label={tutorial.category} size="small" sx={{ bgcolor: "#eef4ff", color: "#1a3a6b" }} />
        </Stack>

        <Box mt={2}>
          <Typography variant="subtitle2" fontWeight={700} mb={0.5}>
            Learning outcomes
          </Typography>
          {tutorial.learningOutcomes.map((o, i) => (
            <Typography key={i} variant="body2" color="text.secondary">
              {i + 1}. {o}
            </Typography>
          ))}
        </Box>
      </Paper>

      <Stack spacing={2}>
        {tutorial.steps.map((step) => (
          <Paper key={step.stepNumber} elevation={2} sx={{ p: 2.5, borderRadius: 2, borderLeft: "4px solid #1a3a6b" }}>
            <Box display="flex" gap={1.5} alignItems="flex-start">
              <Box
                sx={{
                  minWidth: 28,
                  height: 28,
                  borderRadius: "50%",
                  bgcolor: "#1a3a6b",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  flexShrink: 0,
                }}
              >
                {step.stepNumber}
              </Box>
              <Box flexGrow={1}>
                <Typography variant="subtitle2" fontWeight={700} mb={0.75}>
                  {step.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" lineHeight={1.7} mb={step.tip ? 1.5 : 0}>
                  {step.content}
                </Typography>
                {step.tip && (
                  <>
                    <Divider sx={{ mb: 1.5 }} />
                    <Alert
                      severity="success"
                      icon={<TipsAndUpdatesIcon fontSize="small" />}
                      sx={{ py: 0.5 }}
                    >
                      <Typography variant="caption" fontWeight={600} display="block">
                        Pro tip
                      </Typography>
                      <Typography variant="caption">{step.tip}</Typography>
                    </Alert>
                  </>
                )}
              </Box>
            </Box>
          </Paper>
        ))}
      </Stack>
    </Box>
  );
}

export default function TutorialList({ tutorials }) {
  const [selected, setSelected] = useState(null);

  if (selected) {
    return <TutorialDetail tutorial={selected} onBack={() => setSelected(null)} />;
  }

  return (
    <Box>
      <Box mb={3}>
        <Typography variant="h6" fontWeight={700}>
          Investigation Tutorials
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Skill-building guides for investigators at every level, from hash matching fundamentals to dark web investigation.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {tutorials.map((t) => (
          <Grid item xs={12} sm={6} md={4} key={t.id}>
            <Card
              elevation={2}
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                cursor: "pointer",
                transition: "box-shadow 0.2s",
                "&:hover": { boxShadow: 6 },
                borderLeft: `4px solid ${LEVEL_BORDER[t.level] || "#555"}`,
              }}
              onClick={() => setSelected(t)}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" alignItems="flex-start" gap={1} mb={1}>
                  <SchoolIcon sx={{ color: "#1a3a6b", mt: "2px", flexShrink: 0 }} />
                  <Typography variant="subtitle1" fontWeight={700} lineHeight={1.3}>
                    {t.title}
                  </Typography>
                </Box>

                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    mb: 2,
                    display: "-webkit-box",
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                  }}
                >
                  {t.summary}
                </Typography>

                <Stack direction="row" flexWrap="wrap" gap={0.5} mb={1}>
                  <Chip label={t.level} size="small" color={LEVEL_COLOR[t.level]} />
                  <Chip icon={<AccessTimeIcon />} label={t.duration} size="small" variant="outlined" />
                </Stack>

                <Chip
                  label={t.category}
                  size="small"
                  sx={{ bgcolor: "#eef4ff", color: "#1a3a6b", fontSize: "0.65rem" }}
                />

                <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                  {t.steps.length} steps · {t.learningOutcomes.length} learning outcomes
                </Typography>
              </CardContent>

              <CardActions sx={{ pt: 0 }}>
                <Button
                  size="small"
                  endIcon={<ArrowForwardIcon />}
                  onClick={(e) => { e.stopPropagation(); setSelected(t); }}
                >
                  Start Tutorial
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
