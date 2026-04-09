import { Box, Paper, Typography, Chip, LinearProgress } from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";

export default function CaseAnalysisBrief({ brief, loading }) {
  if (!loading && !brief) return null;

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2.5,
        mb: 3,
        bgcolor: "#eef4ff",
        borderLeft: "4px solid #1a3a6b",
        borderRadius: 2,
      }}
    >
      <Box display="flex" alignItems="center" gap={1} mb={1}>
        <AutoAwesomeIcon sx={{ color: "#1a3a6b", fontSize: 18 }} />
        <Typography variant="subtitle2" fontWeight={700} color="primary">
          Case Analysis Brief
        </Typography>
        <Chip label="AI" size="small" sx={{ fontSize: "0.6rem", height: 18, bgcolor: "#1a3a6b", color: "#fff" }} />
      </Box>

      {loading ? (
        <LinearProgress sx={{ borderRadius: 1, mt: 1 }} />
      ) : (
        <Typography variant="body2" color="text.secondary" lineHeight={1.7} sx={{ textAlign: "left" }}>
          {brief}
        </Typography>
      )}
    </Paper>
  );
}
