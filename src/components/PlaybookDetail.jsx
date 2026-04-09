import { useState } from "react";
import {
  Box, Typography, Button, Chip, Stack, Paper, Alert,
  Checkbox, FormControlLabel, Divider
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import BuildIcon from "@mui/icons-material/Build";

const DIFFICULTY_COLOR = { beginner: "success", intermediate: "warning", advanced: "error" };

export default function PlaybookDetail({ playbook, onBack }) {
  const [checked, setChecked] = useState({});

  const toggle = (stepNumber) =>
    setChecked((prev) => ({ ...prev, [stepNumber]: !prev[stepNumber] }));

  const completedCount = Object.values(checked).filter(Boolean).length;

  return (
    <Box>
      {/* Back button */}
      <Button startIcon={<ArrowBackIcon />} onClick={onBack} sx={{ mb: 2 }}>
        Back to Playbooks
      </Button>

      {/* Header */}
      <Paper elevation={0} sx={{ p: 3, mb: 3, bgcolor: "#f8f9ff", borderRadius: 2, borderLeft: "4px solid #1a3a6b" }}>
        <Typography variant="h5" fontWeight={700} mb={1}>
          {playbook.title}
        </Typography>
        <Typography variant="body2" color="text.secondary" mb={2}>
          {playbook.description}
        </Typography>
        <Stack direction="row" flexWrap="wrap" gap={1} alignItems="center">
          <Chip label={playbook.difficulty} size="small" color={DIFFICULTY_COLOR[playbook.difficulty]} />
          <Chip label={playbook.estimatedTime} size="small" variant="outlined" />
          {playbook.investigationTypes.map((t) => (
            <Chip key={t} label={t} size="small" sx={{ bgcolor: "#eef4ff", color: "#1a3a6b", fontSize: "0.7rem" }} />
          ))}
        </Stack>
        {playbook.tools?.length > 0 && (
          <Box mt={1.5} display="flex" alignItems="center" gap={0.5} flexWrap="wrap">
            <BuildIcon sx={{ fontSize: 14, color: "text.secondary" }} />
            <Typography variant="caption" color="text.secondary">
              Tools used:
            </Typography>
            {playbook.tools.map((t) => (
              <Chip key={t} label={t} size="small" variant="outlined" sx={{ fontSize: "0.65rem", height: 20 }} />
            ))}
          </Box>
        )}
      </Paper>

      {/* Progress indicator */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="subtitle2" color="text.secondary">
          {completedCount} of {playbook.steps.length} steps completed
        </Typography>
        {completedCount === playbook.steps.length && (
          <Chip
            icon={<CheckCircleOutlineIcon />}
            label="Playbook Complete"
            color="success"
            size="small"
          />
        )}
      </Box>

      {/* Steps */}
      <Stack spacing={2}>
        {playbook.steps.map((step) => {
          const done = !!checked[step.stepNumber];
          return (
            <Paper
              key={step.stepNumber}
              elevation={done ? 0 : 2}
              sx={{
                p: 2.5,
                borderRadius: 2,
                bgcolor: done ? "#f0f9f0" : "#fff",
                borderLeft: `4px solid ${done ? "#2e7d32" : "#1a3a6b"}`,
                opacity: done ? 0.85 : 1,
                transition: "all 0.2s",
              }}
            >
              <Box display="flex" alignItems="flex-start" gap={1.5}>
                <Box
                  sx={{
                    minWidth: 28,
                    height: 28,
                    borderRadius: "50%",
                    bgcolor: done ? "#2e7d32" : "#1a3a6b",
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
                  <Typography variant="subtitle2" fontWeight={700} mb={0.5}>
                    {step.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={1.5} lineHeight={1.7}>
                    {step.description}
                  </Typography>

                  {step.toolName && (
                    <Chip
                      icon={<BuildIcon />}
                      label={step.toolName}
                      size="small"
                      variant="outlined"
                      color="primary"
                      sx={{ mb: 1.5, fontSize: "0.7rem" }}
                    />
                  )}

                  {/* Checkpoint */}
                  <Alert severity="warning" icon={false} sx={{ py: 0.5, mb: 1.5 }}>
                    <Typography variant="caption" fontWeight={600}>
                      Checkpoint:
                    </Typography>
                    <Typography variant="caption" display="block">
                      {step.checkpoint}
                    </Typography>
                  </Alert>

                  <Divider sx={{ mb: 1 }} />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={done}
                        onChange={() => toggle(step.stepNumber)}
                        size="small"
                        color="success"
                      />
                    }
                    label={
                      <Typography variant="caption" fontWeight={600} color={done ? "success.main" : "text.secondary"}>
                        {done ? "Step completed" : "Mark as complete"}
                      </Typography>
                    }
                  />
                </Box>
              </Box>
            </Paper>
          );
        })}
      </Stack>
    </Box>
  );
}
