import {
  Card, CardContent, CardActions, Chip, Typography,
  Button, Box, Tooltip, Stack
} from "@mui/material";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import LockIcon from "@mui/icons-material/Lock";
import PublicIcon from "@mui/icons-material/Public";
import TerminalIcon from "@mui/icons-material/Terminal";
import ExtensionIcon from "@mui/icons-material/Extension";
import ApiIcon from "@mui/icons-material/Api";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

const PRICING_COLOR = { free: "success", freemium: "warning", paid: "error" };
const CATEGORY_COLOR = {
  OSINT: "#1565c0",
  Forensics: "#6a1b9a",
  Crypto: "#e65100",
  "Dark Web": "#212121",
  "Threat Intel": "#b71c1c",
  CSAM: "#880e4f",
};

const PLATFORM_ICON = {
  cli: <TerminalIcon fontSize="small" />,
  web: <PublicIcon fontSize="small" />,
  api: <ApiIcon fontSize="small" />,
  "browser-extension": <ExtensionIcon fontSize="small" />,
};

export default function ToolCard({ tool, showScore = false, matchLabel, onClick }) {
  const {
    name, url, description, category, pricing,
    platform, skillLevel, investigationTypes,
    requiresRegistration, matchReasons, reliabilityNote,
  } = tool;

  return (
    <Card
      elevation={2}
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        cursor: onClick ? "pointer" : "default",
        transition: "box-shadow 0.2s",
        "&:hover": onClick ? { boxShadow: 6 } : {},
        borderLeft: `4px solid ${CATEGORY_COLOR[category] || "#555"}`,
      }}
      onClick={onClick}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
          <Typography variant="subtitle1" fontWeight={700} sx={{ lineHeight: 1.3 }}>
            {name}
          </Typography>
          {showScore && matchLabel && (
            <Chip
              label={matchLabel.label}
              size="small"
              color={matchLabel.color}
              sx={{ ml: 1, flexShrink: 0, fontSize: "0.65rem" }}
            />
          )}
        </Box>

        {/* Description */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 1.5,
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {description || "No description available."}
        </Typography>

        {/* Chips row */}
        <Stack direction="row" flexWrap="wrap" gap={0.5} mb={1}>
          <Chip label={category} size="small" sx={{ bgcolor: CATEGORY_COLOR[category] || "#555", color: "#fff" }} />
          <Chip label={pricing} size="small" color={PRICING_COLOR[pricing] || "default"} variant="outlined" />
          <Chip label={skillLevel} size="small" variant="outlined" />
          {platform && (
            <Tooltip title={platform}>
              <Chip icon={PLATFORM_ICON[platform]} label={platform} size="small" variant="outlined" />
            </Tooltip>
          )}
          {requiresRegistration && (
            <Tooltip title="Registration required">
              <Chip icon={<LockIcon />} label="Sign-up" size="small" variant="outlined" color="warning" />
            </Tooltip>
          )}
        </Stack>

        {/* Investigation types */}
        {investigationTypes?.length > 0 && (
          <Stack direction="row" flexWrap="wrap" gap={0.5}>
            {investigationTypes.slice(0, 3).map((t) => (
              <Chip key={t} label={t} size="small" sx={{ fontSize: "0.65rem", bgcolor: "#f3f4f6" }} />
            ))}
            {investigationTypes.length > 3 && (
              <Chip label={`+${investigationTypes.length - 3}`} size="small" sx={{ fontSize: "0.65rem" }} />
            )}
          </Stack>
        )}

        {/* Match reasons (shown on recommendation results) */}
        {showScore && matchReasons?.length > 0 && (
          <Box mt={1} p={1} bgcolor="#f0f7ff" borderRadius={1}>
            <Typography variant="caption" color="primary" fontWeight={600}>Why this tool:</Typography>
            {matchReasons.map((r, i) => (
              <Typography key={i} variant="caption" display="block" color="text.secondary">
                • {r}
              </Typography>
            ))}
          </Box>
        )}

        {/* Reliability warning */}
        {reliabilityNote && (
          <Box mt={1} p={1} bgcolor="#fff8e1" borderRadius={1} display="flex" gap={0.5} alignItems="flex-start">
            <WarningAmberIcon sx={{ fontSize: 14, color: "#f57c00", mt: "1px", flexShrink: 0 }} />
            <Typography variant="caption" color="#e65100">
              {reliabilityNote}
            </Typography>
          </Box>
        )}
      </CardContent>

      <CardActions sx={{ pt: 0 }}>
        <Button
          size="small"
          endIcon={<OpenInNewIcon />}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
        >
          Open Tool
        </Button>
      </CardActions>
    </Card>
  );
}
