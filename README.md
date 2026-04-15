# Investiqo

**Build the right stack without the guesswork.**

Investiqo is a decision-support tool that helps child protection investigators find the right digital investigation tools for their case fast, without technical expertise required.

Built for the **ICMEC Ishango Hackathon 2026** (April 9–16, 2026).

Live app: [investiqo.streamlit.app](https://investiqo.streamlit.app)

---

## The Problem

When an investigator needs a tool for a case, they Google it, ask a colleague, or scroll through a long list manually. This takes time they don't have. Investiqo fixes that — describe your case, get ranked recommendations with reasons in under 10 seconds.

---

## How It Works

The investigator fills out a plain-language form:

- **Investigation type** — CSAM detection, online grooming, crypto tracing, trafficking, etc.
- **Available evidence** — image, mobile device, chat logs, crypto wallet, username, etc.
- **Budget** — free only, free + freemium, or any
- **Technical skill level** — beginner, intermediate, advanced
- **Urgency** — immediate, days, or weeks
- **Law enforcement status** — checkbox

A 5-signal scoring engine runs against a curated database of 84 tools and returns the top results ranked by relevance.

### Scoring Signals

| Signal | Points |
|---|---|
| Investigation type match | +3 per tag hit, cap +9 |
| Budget fit | +2 / −2 penalty |
| Technical skill match | +2 |
| Evidence type match | +1 per hit, cap +3 |
| Urgency bonus (free + public tools) | +1 |
| Access gate (LE-only for non-LE users) | −5 |

**Score range:** −7 to 17 points. Every recommendation includes a plain-language explanation of why it was matched.

---

## Features

- Ranked tool recommendations with match reasons
- Show More — extend results beyond top 5
- Tool detail page — cost, skill level, platform, legal admissibility, coding requirements, languages
- Contact & licensing information per tool
- Community star ratings
- Tool deprecation and change warnings
- Suggest a Tool — submit tools not in the database
- Scoring transparency — expandable explanation on results page
- No AI at runtime — fully deterministic, auditable
- No investigator data stored or transmitted

---

## Stack

- Python 3.13
- Streamlit 1.38+
- JSON tool database (84 tools, no backend required)
- pytest (35 tests)

---

## Running Locally

```bash
git clone https://github.com/dkumi12/icmec-tool-finder.git
cd icmec-tool-finder
pip install -r requirements.txt
streamlit run app.py
```

Or open in GitHub Codespaces — click **Code → Codespaces → Create codespace on main**.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
├── app.py                  # Router — registers all pages
├── requirements.txt
├── data/
│   ├── tools.json          # 84 curated tools
│   └── ratings.json        # Community ratings store
├── pages/
│   ├── search.py           # Main form + results
│   ├── detail.py           # Tool detail page
│   └── suggest.py          # Suggest a tool form
├── scoring/
│   ├── recommend.py        # Scoring engine
│   ├── tag_maps.py         # Investigation type → capability tag mapping
│   └── normalise.py        # Field parsing utilities
└── tests/
    └── test_scoring.py     # 35 unit tests
```

---

## Team

- **David Osei Kumi**
- **George Mwangi**
- **Thierry Donambi**

---
