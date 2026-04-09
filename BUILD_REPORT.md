# InvestiTools — Build Report
**Project:** ICMEC Investigative Tool Finder
**Hackathon:** Ishango Hackathon — April 9-16, 2026
**Challenge:** Idea #2 — Central system for OSINT tools matching investigation needs
**Build Date:** April 4, 2026
**Status:** Prototype Complete

---

## 1. Problem Statement

Child protection investigators — police officers, digital forensic specialists, prosecutors, and frontline workers — operate in a fragmented ecosystem of tools. When investigating a case involving online grooming, CSAM distribution, crypto-financed trafficking, or dark web exploitation, there is no central place that tells them:

- Which tools exist for their specific case type
- Which ones fit their budget (free vs paid)
- Which ones match their technical skill level
- Which ones are legally admissible in their jurisdiction
- Which ones are available in their region (including Africa)

This forces investigators to rely on colleagues, Google searches, or outdated PDF guides — wasting time that could be spent on active cases.

**InvestiTools solves this by combining a comprehensive tool database with an intelligent recommendation engine that matches investigators to the right tools based on their specific case context.**

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LAYER 1 — DATA SOURCES                                     │
│  ──────────────────────                                     │
│  OSINT Framework (arf.json)     — 1,167 tools               │
│  OSINT-Map (database.json)      — 198 tools                 │
│  awesome-osint (markdown)       — 1,398 tools               │
│  awesome-forensics (markdown)   — 178 tools                 │
│  awesome-incident (markdown)    — 218 tools                 │
│  ICMEC curated (manual)         — 12 tools                  │
│  Additional curated (manual)    — 14 tools                  │
│                                                             │
│  LAYER 2 — DATA PIPELINE (Python)                           │
│  ────────────────────────────────                           │
│  fetch_sources.py    → downloads JSON sources               │
│  parse_markdown.py   → converts markdown to JSON            │
│  merge.py            → deduplicates + normalises schema     │
│  tag_with_bedrock.py → AI-tags investigation types          │
│  cleanup_tags.py     → fixes false positives                │
│                                                             │
│  LAYER 3 — DATABASE                                         │
│  ──────────────────                                         │
│  tools.json          → 2,946 unique tools                   │
│                         unified schema                      │
│                         AI-tagged investigation types       │
│                                                             │
│  LAYER 4 — FRONTEND APPLICATION (React)                     │
│  ──────────────────────────────────────                     │
│  Tool Browser        → search + filter all 2,946 tools      │
│  Case Input Form     → investigator describes their case    │
│  Recommendation Engine → scores + ranks matching tools      │
│  Tool Cards          → displays results with match labels   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. The Data Pipeline — Detailed

The pipeline is the backbone of the system. It runs once to build the database and does not run during live app usage.

### Step 1 — Fetch (`fetch_sources.py`)
Downloads raw data from GitHub repositories. Some sources are already in JSON format (OSINT Framework, OSINT-Map) and require no conversion. Others are markdown files (awesome-lists) that need parsing.

**Why GitHub repos?** These are the most maintained, community-verified collections of investigative tools available publicly. They are updated regularly by security researchers globally.

### Step 2 — Parse (`parse_markdown.py`)
Awesome-lists are written for human readers in markdown format:
```
- [Sherlock](https://github.com/sherlock-project/sherlock) - Find usernames across 400+ networks
```
The parser extracts the `[name](url) - description` pattern from each line and converts it into a structured JSON object matching the unified schema.

**Key challenge:** Not all markdown lists follow the same format. Tables, nested lists, and inconsistent spacing required regex pattern matching to handle edge cases.

### Step 3 — Merge (`merge.py`)
Combines all sources into a single unified database. Two critical operations happen here:

**Deduplication:**
The same tool appears across multiple sources. Without deduplication, Sherlock would appear 4 times in the database. The merge script uses the tool's URL as the unique identifier — because while names vary across sources ("Sherlock", "Sherlock Tool", "sherlock-project"), the URL is always the same. First occurrence wins, all duplicates are dropped.

```
Before merge:  ~4,200 raw entries
After dedup:    2,946 unique tools
Duplicates removed: ~1,254 (30% of raw data)
```

**Schema normalisation:**
Every tool from every source gets mapped to the same unified schema regardless of its origin. This ensures the recommendation engine can query any field on any tool consistently.

**Unified Schema:**
```json
{
  "id": "unique-slug-xxxx",
  "name": "Tool Name",
  "url": "https://...",
  "description": "What it does",
  "category": "OSINT | Forensics | Crypto | Dark Web | CSAM | Threat Intel",
  "subcategory": "More specific grouping",
  "pricing": "free | freemium | paid",
  "platform": "web | cli | api | desktop | browser-extension",
  "skillLevel": "beginner | intermediate | advanced",
  "investigationTypes": ["CSAM detection", "online grooming", ...],
  "input": "What the investigator provides",
  "output": "What the tool returns",
  "opsec": "passive | active",
  "requiresRegistration": false,
  "hasAPI": true,
  "localInstall": false,
  "legalNotes": "Jurisdiction and admissibility notes",
  "tags": ["keyword", "tags"],
  "source": "where this entry came from"
}
```

### Step 4 — AI Tagging (`tag_with_bedrock.py`)
The most critical step for the recommendation engine. Each tool needs `investigationTypes` — the field that tells the engine which case types this tool is relevant for.

**The problem:** 2,946 tools need classifying across 10 investigation types. Doing this manually would take weeks.

**The solution:** AWS Bedrock with Mistral Small. For each tool, the script sends a prompt:
```
"Given this tool: [name] - [description]
Which investigation types apply?
[list of 10 types]
Reply with a JSON array only."
```

Mistral reads the tool's context and returns a classification like:
```json
["CSAM detection", "online grooming", "digital forensics"]
```

This tag is then written to the tool's `investigationTypes` field in tools.json.

**Important:** Mistral runs only once during the build. It does not run during live app usage. The intelligence is baked into tools.json at build time.

**Cost:** ~$1 total for 2,054 tools at Mistral Small pricing.
**Time:** ~1 hour.

### Step 5 — Cleanup (`cleanup_tags.py`)
Mistral occasionally produces false positives — e.g., tagging a certificate transparency tool as "crypto tracing" because it sees the word "certificate." The cleanup script applies rule-based corrections:
- Removes crypto tracing tags from tools that don't actually trace cryptocurrency
- Adds dark web tags to tools containing Tor/onion keywords
- Adds CSAM tags to tools containing known child protection keywords
- Never modifies the 26 manually curated ICMEC tools

---

## 4. The Database — What's Inside

### Coverage by Category
| Category | Tools |
|---|---|
| OSINT | 2,314 |
| Forensics | 195 |
| Dark Web | 145 |
| Threat Intel | 90 |
| Crypto | 15 |
| CSAM | 13 |
| **Total** | **2,946** |

### Coverage by Investigation Type
| Investigation Type | Tools Tagged |
|---|---|
| Social media investigation | 1,695 |
| Digital forensics | 865 |
| Cross-border | 766 |
| Dark web | 527 |
| Threat intelligence | 394 |
| Online grooming | 175 |
| Crypto tracing | 91 |
| CSAM detection | 57 |
| Trafficking | 30 |
| Sextortion | 7 |

### Pricing Distribution
| Pricing | Tools | % |
|---|---|---|
| Free | 2,669 | 90% |
| Freemium | 229 | 8% |
| Paid | 48 | 2% |

### The ICMEC Curated Layer
12 manually researched tools specific to child protection investigations — none of which exist in any public tool database:

| Tool | Category | Cost | Provider |
|---|---|---|---|
| PhotoDNA | CSAM | Free (LE) | Microsoft |
| F1 Video Hash Tool | CSAM | Free (LE) | Friend MTS / ICMEC |
| Griffeye Analyze DI | CSAM | Free (LE) | Safer Society / ICMEC |
| INTERPOL ICSE Database | CSAM | Free (LE) | INTERPOL |
| Project VIC | CSAM | Free (LE) | Project VIC Intl |
| NCMEC CyberTipline | CSAM | Free | NCMEC |
| CAID | CSAM | Free (UK LE) | UK NCA |
| Cellebrite UFED | Forensics | Paid | Cellebrite |
| Magnet AXIOM | Forensics | Paid | Magnet Forensics |
| Thorn Spotlight | CSAM | Free (LE) | Thorn |
| Europol IOCTA Platform | CSAM | Free | Europol |
| IWF Reporting Portal | CSAM | Free | Internet Watch Foundation |

### Africa-Specific Tools
3 tools specifically relevant to West African investigators — unique to this platform:
- Ghana Police Cyber Crime Unit (Child Protection Digital Forensics Lab)
- AFRIPOL Cybercrime Reporting
- AFJOC (INTERPOL African Joint Operation Against Cybercrime)

---

## 5. The Recommendation Engine

The engine lives entirely in `src/utils/recommend.js` and runs in the browser with no API calls.

### How It Works
When an investigator submits their case, the engine scores every tool in the database against their inputs using a weighted scoring system:

```
Score = 0

+3 per matching investigation type    (most important signal)
+2 if pricing fits budget
+2 if tool skill level ≤ user skill
+1 per matching evidence input type
+1 if free + no registration + urgency is immediate
+1 per matching keyword tag

Minimum score to appear: 3
Maximum results shown: 30
```

### Score → Match Label
| Score | Label |
|---|---|
| 9+ | Excellent match |
| 6-8 | Strong match |
| 3-5 | Good match |

### Why This Approach
A rule-based scoring system was chosen over a trained ML classifier for the prototype because:
1. Fast to build and explain
2. Fully transparent — every reason a tool was recommended is shown to the user
3. No inference cost — runs instantly in the browser
4. Can be improved post-hackathon by training a proper classifier using the tags as labelled data

---

## 6. The Frontend Application

### Tech Stack
| Layer | Technology | Why |
|---|---|---|
| Framework | React 18 + Vite | Fast builds, hot reload, consistent with existing Limbraapp work |
| UI Library | Material UI (MUI) | Professional components, consistent with Limbraapp |
| Styling | Emotion (CSS-in-JS) | Comes with MUI |
| State | React hooks (useState, useEffect) | Simple enough for prototype, no Redux needed |
| Data | Static JSON fetch | No backend needed, instant load |

### Application Views

**View 1 — Case Input Form**
Investigator fills in:
- Investigation type (multi-select chips)
- Budget (free / freemium / paid)
- Technical skill level (beginner / intermediate / advanced)
- Evidence available (username, image, wallet address, etc.)
- Urgency (immediate / days / weeks)

**View 2 — Recommendation Results**
- Top 30 tools ranked by relevance score
- Grouped by category
- Each card shows: match label, why this tool, pricing, skill level, platform, investigation types
- Direct link to open each tool
- "New Search" to start over

**View 3 — Tool Browser**
- Search all 2,946 tools by name or keyword
- Filter by: category, pricing, skill level, platform, investigation type
- Shows result count in real time

---

## 7. What Makes This System Unique

### 1. Context-Aware Recommendations
No existing tool directory asks investigators for their case context before showing results. OSINT Framework, awesome-osint, and similar resources are static lists. InvestiTools is the first to match tools to investigator context.

### 2. Child-Protection-Specific Intelligence
The ICMEC curated layer contains tools — PhotoDNA, INTERPOL ICSE, Project VIC, Thorn Spotlight — that don't appear in any public tool database. This layer was built entirely from primary research.

### 3. Africa Coverage
Ghana Police Cyber Crime Unit, AFRIPOL, and AFJOC are not in any existing tool directory globally. For investigators in West Africa, this platform is the only place these resources are catalogued alongside international tools.

### 4. Pre-Computed AI Intelligence
Mistral classified 2,054 tools at build time — so the live app requires zero AI API calls. This means the system is fast, cheap to run, and works offline once loaded.

### 5. Reproducible Pipeline
The entire database can be rebuilt from scratch by running one command:
```
python pipeline/run_pipeline.py
```
This means the database can be kept current as new tools emerge.

---

## 8. Gaps and Future Work

### Minor Gaps (Easy Fixes)
- **AI-generated CSAM investigation type** — add to the investigation types list with relevant tools (deepfake detectors, metadata analysers)
- **Livestreamed abuse tools** — NetClean, NCMEC livestream reporting
- **Privacy notice** — visible statement that the app stores no investigation data

### Post-Hackathon Improvements
- **Supabase integration** — allow investigators to save sessions and build tool shortlists
- **Admin panel** — let ICMEC staff add/update tools without touching code
- **Feedback loop** — investigators rate recommendations, improving the scoring over time
- **Trained classifier** — use the Mistral tags as training labels to train a lightweight model replacing the rule-based scorer
- **Live pipeline** — scheduled weekly rebuild to pick up new tools from source repos
- **Multi-language** — French and Spanish for Francophone Africa and Latin America (ICMEC's key regions)

---

## 9. Standards and Architecture Decisions

### Standards Followed
| Standard | Implementation |
|---|---|
| Separation of concerns | Pipeline (`/pipeline`) separate from app (`/src`) |
| Single source of truth | One `tools.json` feeds everything |
| DRY (Don't Repeat Yourself) | Shared hooks, services, utility functions |
| Data provenance | Every tool has a `source` field |
| Schema consistency | All 2,946 tools follow identical schema |
| Deduplication | URL-based dedup removes ~1,254 duplicates |
| Modular components | Each React component has one responsibility |

### Standards to Add
| Standard | What It Covers |
|---|---|
| Privacy by design | No investigation data stored or transmitted |
| WCAG accessibility | Screen reader support for LE users with disabilities |
| API versioning | If a backend is added later |
| Database versioning | Track schema changes to tools.json over time |

---

## 10. Research Directions

Areas worth deeper research before or during the hackathon:

**On the data side:**
- Entity resolution — how to match tools that have the same function but different names/URLs across sources
- Data quality metrics — how to measure and score the completeness of tool entries
- Ontology design — formal taxonomy of investigation types used by INTERPOL/UNODC

**On the recommendation side:**
- Collaborative filtering — recommend tools based on what similar investigators used
- Hybrid recommendation systems — combining rule-based and ML approaches
- Explainable AI — making recommendation reasoning more transparent

**On the child protection domain:**
- ICMEC's Technology Tools page — primary source for what tools LE agencies actually use
- INTERPOL's ICSE Next Generation — upcoming AI-powered upgrade to the global CSAM database
- WeProtect Global Alliance — framework for national responses to online child exploitation
- UNODC cybercrime tools — additional toolsets used in trafficking investigations
- Project VIC International — hash sharing infrastructure details

**On the Africa context:**
- AFRIPOL Cybercrime Strategy — official AU cybercrime framework
- INTERPOL Africa Cyberthreat Assessment Report 2025 — current threat landscape
- Ghana Police Cyber Crime Unit — capabilities and toolset in West Africa
- AFJOC programme outcomes — what tools have been deployed across African LE agencies

---

## 11. Key Files Reference

```
icmec-tool-finder/
├── pipeline/
│   ├── run_pipeline.py          Master script — runs all steps
│   ├── fetch_sources.py         Downloads JSON sources
│   ├── parse_markdown.py        Converts markdown to JSON
│   ├── merge.py                 Deduplicates + merges all sources
│   ├── tag_with_bedrock.py      AI-tags tools via AWS Bedrock (Mistral)
│   ├── cleanup_tags.py          Fixes false positive tags
│   ├── icmec_tools.json         12 manually curated ICMEC tools
│   └── add_missing_tools.json   14 additional curated tools
├── src/
│   ├── data/
│   │   └── tools.json           Master database (2,946 tools)
│   ├── components/
│   │   ├── App.jsx              Main layout and routing
│   │   ├── CaseInputForm.jsx    Investigator case input
│   │   ├── RecommendationResults.jsx  Ranked results display
│   │   ├── ToolBrowser.jsx      Search and filter all tools
│   │   └── ToolCard.jsx         Individual tool display
│   ├── hooks/
│   │   └── useRecommendations.js  Recommendation state management
│   ├── services/
│   │   └── toolsService.js      Load and filter tools
│   └── utils/
│       └── recommend.js         Weighted scoring algorithm
├── public/
│   └── data/
│       └── tools.json           Served to browser (copy of src/data/)
└── .env                         AWS credentials for pipeline
```

---

*Built for the Ishango Hackathon, April 2026*
*Challenge partner: International Centre for Missing & Exploited Children (ICMEC)*
