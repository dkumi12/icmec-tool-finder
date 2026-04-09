import { useState, useEffect } from "react";
import {
  Box, Container, Typography, Tabs, Tab, AppBar,
  Toolbar, CircularProgress, Alert, CssBaseline
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import PolicyIcon from "@mui/icons-material/Policy";
import SearchIcon from "@mui/icons-material/Search";
import StorageIcon from "@mui/icons-material/Storage";
import ListAltIcon from "@mui/icons-material/ListAlt";
import SchoolIcon from "@mui/icons-material/School";

import { loadTools } from "./services/toolsService";
import { useRecommendations } from "./hooks/useRecommendations";
import CaseInputForm from "./components/CaseInputForm";
import RecommendationResults from "./components/RecommendationResults";
import ToolBrowser from "./components/ToolBrowser";
import PlaybookList from "./components/PlaybookList";
import TutorialList from "./components/TutorialList";
import playbooksData from "./data/playbooks.json";
import tutorialsData from "./data/tutorials.json";

const theme = createTheme({
  palette: {
    primary: { main: "#1a3a6b" },
    secondary: { main: "#c0392b" },
    background: { default: "#f5f6fa" },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", sans-serif',
  },
});

export default function App() {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState(0);

  const { results, caseInput, hasSearched, runRecommendation, reset, brief, briefLoading } = useRecommendations(tools);

  useEffect(() => {
    loadTools()
      .then(setTools)
      .catch(() => setError("Could not load tools database. Run the data pipeline first."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" elevation={1} sx={{ bgcolor: "primary.main" }}>
        <Toolbar>
          <PolicyIcon sx={{ mr: 1.5, fontSize: 28 }} />
          <Box>
            <Typography variant="h6" fontWeight={700} lineHeight={1.2}>
              InvestiTools
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              ICMEC · Decision-Support System for Investigators
            </Typography>
          </Box>
          <Box flexGrow={1} />
          <Typography variant="caption" sx={{ opacity: 0.6 }}>
            {tools.length > 0 && `${tools.length} tools indexed`}
          </Typography>
        </Toolbar>
        <Tabs
          value={tab}
          onChange={(_, v) => { setTab(v); reset(); }}
          textColor="inherit"
          TabIndicatorProps={{ style: { backgroundColor: "#fff" } }}
          sx={{ px: 2, borderTop: "1px solid rgba(255,255,255,0.1)" }}
        >
          <Tab icon={<SearchIcon />} iconPosition="start" label="Find Tools for My Case" />
          <Tab icon={<StorageIcon />} iconPosition="start" label="Browse All Tools" />
          <Tab icon={<ListAltIcon />} iconPosition="start" label="Playbooks" />
          <Tab icon={<SchoolIcon />} iconPosition="start" label="Tutorials" />
        </Tabs>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        {loading && (
          <Box display="flex" justifyContent="center" py={10}>
            <CircularProgress />
          </Box>
        )}
        {error && <Alert severity="error">{error}</Alert>}

        {!loading && !error && (
          <>
            {tab === 0 && (
              <>
                {!hasSearched ? (
                  <Box maxWidth={700} mx="auto">
                    <CaseInputForm onSubmit={runRecommendation} />
                  </Box>
                ) : (
                  <RecommendationResults
                    results={results}
                    caseInput={caseInput}
                    onReset={reset}
                    brief={brief}
                    briefLoading={briefLoading}
                  />
                )}
              </>
            )}
            {tab === 1 && <ToolBrowser tools={tools} />}
            {tab === 2 && <PlaybookList playbooks={playbooksData} />}
            {tab === 3 && <TutorialList tutorials={tutorialsData} />}
          </>
        )}
      </Container>
    </ThemeProvider>
  );
}
