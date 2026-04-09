import { useState } from "react";
import {
  Box, Typography, Button, Chip, Stack, FormControl,
  InputLabel, Select, MenuItem, Paper, Divider
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

const INVESTIGATION_TYPES = [
  "CSAM detection",
  "AI-Generated CSAM",
  "Self-Generated CSAM",
  "online grooming",
  "crypto tracing",
  "dark web",
  "trafficking",
  "sextortion",
  "cross-border",
  "social media investigation",
  "digital forensics",
  "media authentication",
  "forensic linguistics",
  "undercover operations",
  "threat intelligence",
];

const INPUT_TYPES = [
  "Username",
  "Email address",
  "Phone number",
  "Image / photo",
  "Video",
  "Crypto wallet address",
  "Domain / IP",
  "Social media profile",
  "Hash / fingerprint",
  "Encrypted file",
  "Mobile device",
  "Cloud storage",
  "Document",
  "Chat logs",
];

const DEFAULTS = {
  investigationTypes: [],
  budget: "",
  skillLevel: "",
  inputs: [],
  urgency: "",
};

export default function CaseInputForm({ onSubmit, loading }) {
  const [form, setForm] = useState(DEFAULTS);
  const [errors, setErrors] = useState({});

  const toggleChip = (field, value) => {
    setForm((prev) => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter((v) => v !== value)
        : [...prev[field], value],
    }));
  };

  const validate = () => {
    const e = {};
    if (form.investigationTypes.length === 0) e.investigationTypes = "Select at least one type";
    if (!form.budget) e.budget = "Required";
    if (!form.skillLevel) e.skillLevel = "Required";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = () => {
    if (validate()) onSubmit(form);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h6" fontWeight={700} mb={0.5}>
        Describe Your Investigation
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        Tell us about your case and we'll recommend the best tools for you.
      </Typography>

      <Divider sx={{ mb: 2 }} />

      {/* Investigation Type */}
      <Box mb={2.5}>
        <Typography variant="subtitle2" fontWeight={600} mb={1}>
          What are you investigating? *
        </Typography>
        <Stack direction="row" flexWrap="wrap" gap={1}>
          {INVESTIGATION_TYPES.map((t) => (
            <Chip
              key={t}
              label={t}
              clickable
              color={form.investigationTypes.includes(t) ? "primary" : "default"}
              variant={form.investigationTypes.includes(t) ? "filled" : "outlined"}
              onClick={() => toggleChip("investigationTypes", t)}
            />
          ))}
        </Stack>
        {errors.investigationTypes && (
          <Typography variant="caption" color="error">{errors.investigationTypes}</Typography>
        )}
      </Box>

      {/* Budget + Skill Level */}
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} mb={2.5}>
        <FormControl fullWidth error={!!errors.budget}>
          <InputLabel>Budget</InputLabel>
          <Select
            value={form.budget}
            label="Budget"
            onChange={(e) => setForm({ ...form, budget: e.target.value })}
          >
            <MenuItem value="free">Free tools only</MenuItem>
            <MenuItem value="freemium">Free + Freemium</MenuItem>
            <MenuItem value="paid">Any (including paid)</MenuItem>
          </Select>
          {errors.budget && <Typography variant="caption" color="error">{errors.budget}</Typography>}
        </FormControl>

        <FormControl fullWidth error={!!errors.skillLevel}>
          <InputLabel>Your Technical Skill Level</InputLabel>
          <Select
            value={form.skillLevel}
            label="Your Technical Skill Level"
            onChange={(e) => setForm({ ...form, skillLevel: e.target.value })}
          >
            <MenuItem value="beginner">Beginner (web-based tools only)</MenuItem>
            <MenuItem value="intermediate">Intermediate (can install software)</MenuItem>
            <MenuItem value="advanced">Advanced (command line, scripting)</MenuItem>
          </Select>
          {errors.skillLevel && <Typography variant="caption" color="error">{errors.skillLevel}</Typography>}
        </FormControl>
      </Stack>

      {/* What do you have */}
      <Box mb={2.5}>
        <Typography variant="subtitle2" fontWeight={600} mb={1}>
          What evidence / inputs do you have? (optional)
        </Typography>
        <Stack direction="row" flexWrap="wrap" gap={1}>
          {INPUT_TYPES.map((t) => (
            <Chip
              key={t}
              label={t}
              clickable
              color={form.inputs.includes(t) ? "secondary" : "default"}
              variant={form.inputs.includes(t) ? "filled" : "outlined"}
              onClick={() => toggleChip("inputs", t)}
            />
          ))}
        </Stack>
      </Box>

      {/* Urgency */}
      <Box mb={3}>
        <FormControl fullWidth>
          <InputLabel>Urgency</InputLabel>
          <Select
            value={form.urgency}
            label="Urgency"
            onChange={(e) => setForm({ ...form, urgency: e.target.value })}
          >
            <MenuItem value="immediate">Immediate (need tools now)</MenuItem>
            <MenuItem value="days">Days (can set up tools)</MenuItem>
            <MenuItem value="weeks">Weeks (full investigation setup)</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Button
        variant="contained"
        size="large"
        fullWidth
        startIcon={<SearchIcon />}
        onClick={handleSubmit}
        disabled={loading}
        sx={{ py: 1.5, fontWeight: 700 }}
      >
        {loading ? "Finding tools..." : "Find Recommended Tools"}
      </Button>
    </Paper>
  );
}
