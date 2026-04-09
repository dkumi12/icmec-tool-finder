import { useState } from "react";
import {
  Box, Typography, Grid, Card, CardContent, CardActions,
  Chip, Stack, Button
} from "@mui/material";
import ListAltIcon from "@mui/icons-material/ListAlt";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import PlaybookDetail from "./PlaybookDetail";

const DIFFICULTY_COLOR = { beginner: "success", intermediate: "warning", advanced: "error" };
const DIFFICULTY_BORDER = { beginner: "#2e7d32", intermediate: "#e65100", advanced: "#b71c1c" };

export default function PlaybookList({ playbooks }) {
  const [selected, setSelected] = useState(null);

  if (selected) {
    return <PlaybookDetail playbook={selected} onBack={() => setSelected(null)} />;
  }

  return (
    <Box>
      <Box mb={3}>
        <Typography variant="h6" fontWeight={700}>
          Investigation Playbooks
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Step-by-step workflows for common child exploitation investigation scenarios, with evaluation checkpoints at each stage.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {playbooks.map((pb) => (
          <Grid item xs={12} sm={6} md={4} key={pb.id}>
            <Card
              elevation={2}
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                cursor: "pointer",
                transition: "box-shadow 0.2s",
                "&:hover": { boxShadow: 6 },
                borderLeft: `4px solid ${DIFFICULTY_BORDER[pb.difficulty] || "#555"}`,
              }}
              onClick={() => setSelected(pb)}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" alignItems="flex-start" gap={1} mb={1}>
                  <ListAltIcon sx={{ color: "#1a3a6b", mt: "2px", flexShrink: 0 }} />
                  <Typography variant="subtitle1" fontWeight={700} lineHeight={1.3}>
                    {pb.title}
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
                  {pb.description}
                </Typography>

                <Stack direction="row" flexWrap="wrap" gap={0.5} mb={1}>
                  <Chip label={pb.difficulty} size="small" color={DIFFICULTY_COLOR[pb.difficulty]} />
                  <Chip label={pb.estimatedTime} size="small" variant="outlined" />
                </Stack>

                <Stack direction="row" flexWrap="wrap" gap={0.5}>
                  {pb.investigationTypes.slice(0, 2).map((t) => (
                    <Chip
                      key={t}
                      label={t}
                      size="small"
                      sx={{ bgcolor: "#eef4ff", color: "#1a3a6b", fontSize: "0.65rem" }}
                    />
                  ))}
                </Stack>

                <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                  {pb.steps.length} steps
                </Typography>
              </CardContent>

              <CardActions sx={{ pt: 0 }}>
                <Button
                  size="small"
                  endIcon={<ArrowForwardIcon />}
                  onClick={(e) => { e.stopPropagation(); setSelected(pb); }}
                >
                  View Playbook
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
