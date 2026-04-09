import { useState, useMemo } from "react";
import {
  Box, Grid, TextField, FormControl, InputLabel, Select,
  MenuItem, Typography, Stack, InputAdornment, Chip, Button
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import ClearIcon from "@mui/icons-material/Clear";
import ToolCard from "./ToolCard";
import { filterTools, } from "../services/toolsService";
import { getFilterOptions } from "../utils/recommend";

const EMPTY_FILTERS = {
  search: "", category: "", pricing: "", skillLevel: "", platform: "", investigationType: "",
};

export default function ToolBrowser({ tools }) {
  const [filters, setFilters] = useState(EMPTY_FILTERS);

  const categories = useMemo(() => getFilterOptions(tools, "category"), [tools]);
  const platforms = useMemo(() => getFilterOptions(tools, "platform"), [tools]);
  const invTypes = useMemo(() => getFilterOptions(tools, "investigationTypes"), [tools]);

  const filtered = useMemo(() => filterTools(tools, filters), [tools, filters]);

  const setFilter = (key, val) => setFilters((prev) => ({ ...prev, [key]: val }));
  const clearFilters = () => setFilters(EMPTY_FILTERS);
  const activeFilterCount = Object.values(filters).filter(Boolean).length;

  return (
    <Box>
      {/* Search bar */}
      <TextField
        fullWidth
        placeholder="Search tools by name, description or keyword..."
        value={filters.search}
        onChange={(e) => setFilter("search", e.target.value)}
        InputProps={{
          startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>,
        }}
        sx={{ mb: 2 }}
      />

      {/* Filter row */}
      <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} mb={2} flexWrap="wrap">
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Category</InputLabel>
          <Select value={filters.category} label="Category" onChange={(e) => setFilter("category", e.target.value)}>
            <MenuItem value="">All</MenuItem>
            {categories.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 130 }}>
          <InputLabel>Pricing</InputLabel>
          <Select value={filters.pricing} label="Pricing" onChange={(e) => setFilter("pricing", e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="free">Free</MenuItem>
            <MenuItem value="freemium">Freemium</MenuItem>
            <MenuItem value="paid">Paid</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Skill Level</InputLabel>
          <Select value={filters.skillLevel} label="Skill Level" onChange={(e) => setFilter("skillLevel", e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="beginner">Beginner</MenuItem>
            <MenuItem value="intermediate">Intermediate</MenuItem>
            <MenuItem value="advanced">Advanced</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 130 }}>
          <InputLabel>Platform</InputLabel>
          <Select value={filters.platform} label="Platform" onChange={(e) => setFilter("platform", e.target.value)}>
            <MenuItem value="">All</MenuItem>
            {platforms.map((p) => <MenuItem key={p} value={p}>{p}</MenuItem>)}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Investigation Type</InputLabel>
          <Select value={filters.investigationType} label="Investigation Type" onChange={(e) => setFilter("investigationType", e.target.value)}>
            <MenuItem value="">All</MenuItem>
            {invTypes.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
          </Select>
        </FormControl>

        {activeFilterCount > 0 && (
          <Button startIcon={<ClearIcon />} onClick={clearFilters} size="small" color="error" variant="outlined">
            Clear ({activeFilterCount})
          </Button>
        )}
      </Stack>

      {/* Results count */}
      <Typography variant="body2" color="text.secondary" mb={2}>
        Showing <strong>{filtered.length}</strong> of {tools.length} tools
      </Typography>

      {/* Grid */}
      {filtered.length === 0 ? (
        <Typography color="text.secondary" textAlign="center" py={6}>
          No tools match your filters. Try clearing some.
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {filtered.slice(0, 60).map((tool) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={tool.id}>
              <ToolCard tool={tool} />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
