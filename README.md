# Investiqo 🔍

**Build the right investigative stack without the guesswork.**

Investiqo is a deterministic tool recommendation engine designed to help child protection investigators, law enforcement, and researchers find the most relevant forensic and OSINT tools for their specific case — fast, without technical expertise required.

Developed for the **ICMEC Ishango Hackathon 2026** (April 9–16, 2026).

🌐 Live app: [investiqo.streamlit.app](https://investiqo.streamlit.app)

---

## 🚀 The Problem

When an investigator needs a tool for a case, they Google it, ask a colleague, or scroll through a long list manually. This takes time they don't have. Investiqo fixes that — describe your case, get ranked recommendations with explanations in under 10 seconds.

---

## 👥 The Team

- **David Osei Kumi**
- **George Mwangi**
- **Thierry Donambi**

Built for the ICMEC Ishango Hackathon 2026.

---

## 📐 Scoring Logic (0–100%)

Investiqo uses a **transparent, additive scoring engine** — no black-box AI. Each tool is scored against your case inputs across five signals, then normalised to a 0–100% match score. Every recommendation includes a plain-language explanation of why it was matched.

| Signal | How It Works |
|---|---|
| **Investigation type match** | +3 per matching capability tag, capped at +9 |
| **Budget fit** | +2 if within budget, −2 if outside |
| **Technical skill match** | +2 if tool is appropriate for your level |
| **Evidence type match** | +1 per matching evidence type, capped at +3 |
| **Urgency bonus** | +1 for free, publicly available tools when urgency is immediate |
| **Access gate** | −5 if tool is LE-restricted and user is not law enforcement |

Raw score range: −7 to +17 points → normalised to **0–100%**.

- 🟢 **≥ 70%** — strong match
- 🟡 **40–69%** — partial match
- 🔴 **< 40%** — weak match

---

## 🛠️ Key Features

- Ranked recommendations with plain-language match reasons
- Score displayed as a match percentage (0–100%)
- Show More — extend results beyond top 5
- Tool detail page — cost, skill level, platform, legal admissibility, coding requirements, languages
- Community star ratings — no database or login required
- Thumbs up/down recommendation feedback
- Tool deprecation and change warnings
- Suggest a Tool — submit tools not in the database
- Optional filters — coding requirement, interface language
- Scoring transparency — expandable explanation on results page
- No AI at runtime — fully deterministic and auditable
- No investigator data stored or transmitted

---

## 📁 Project Structure

```text
├── app.py                      # Streamlit router — registers all pages
├── requirements.txt
├── data/
│   ├── tools.json              # 84 curated forensic and OSINT tools
│   ├── tool_enrichment.json    # Extended language and coding metadata (George Mwangi)
│   ├── ratings.json            # Seed ratings for demo
│   └── ratings_log.jsonl       # Investigator rating submissions log
├── pages/
│   ├── search.py               # Main form + ranked results
│   ├── detail.py               # Full tool breakdown + community ratings + feedback
│   └── suggest.py              # Suggest a tool form
├── scoring/
│   ├── recommend.py            # Core scoring engine + score_pct() normaliser
│   ├── tag_maps.py             # Investigation type → capability tag mapping
│   ├── normalise.py            # Field parsing utilities (pricing, skill, languages)
│   └── ratings.py              # Community ratings helpers (George Mwangi)
└── tests/
    └── test_scoring.py         # 43 unit tests
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/dkumi12/icmec-tool-finder.git
cd icmec-tool-finder
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

Or open in GitHub Codespaces — click **Code → Codespaces → Create codespace on main**.

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

*Built for the ICMEC Ishango Hackathon 2026.*
