# Investiqo 🔍

**Build the right investigative stack without the guesswork.**

Investiqo is a deterministic tool recommendation engine designed to help digital investigators, law enforcement, and researchers find the most relevant forensic and OSINT tools for their specific case requirements. Developed for the **ICMEC Ishango Hackathon 2026**.

## 🚀 Overview

Investiqo removes the ambiguity of "black-box" AI recommendations by using a **transparent, rule-based scoring engine**. It evaluates tools across five weighted dimensions to ensure investigators use tools that are legally admissible, budget-friendly, and skill-appropriate.

## 👥 The Team

### Developers

* **George**
* **David**
* **Thierry Donambi**

### Mentors

* **Mahamat**
* **Luel**

## 📐 Scoring Logic (Weighted 0–100)

The engine in `scoring/rule_based.py` calculates a tool's relevance using the following weights:

* **Investigation Match (40%)**: Ratio of required vs. available technical capability tags.
* **Budget Alignment (20%)**: Compatibility with user financial constraints (Free, Freemium, Paid).
* **Technical Skill Fit (15%)**: Gradient penalty if a tool's required skill exceeds the user's level.
* **Evidence Handling (15%)**: Ability to process specific inputs (Images, Crypto, Mobile, etc.).
* **Access Verification (10%)**: Hierarchy check for Law Enforcement vs. Public status.

## 🛠️ Key Features

- **Deterministic & Explainable**: Every recommendation includes specific "Match Reasons."
- **Comprehensive Database**: Includes industry standards like Autopsy, Magnet AXIOM, and specialized OSINT frameworks.
- **Access Gating**: Intelligently handles Law Enforcement-restricted tools.
- **Technical Requirement Indicators**: Automatically detects if a tool requires CLI, API, or coding knowledge.

## 📁 Project Structure

```text
├── data/
│   └── tools.json         # The master database of forensic and OSINT tools
├── pages/
│   ├── search.py          # Main search interface and results display
│   ├── detail.py          # Full breakdown of individual tool metadata and scores
│   └── suggest.py         # User submission form for new tool suggestions
├── scoring/
│   ├── normalise.py       # Fuzzy string matching and data cleaning
│   ├── rule_based.py      # Core 0–100 weighted scoring engine
│   ├── tag_maps.py        # Maps case types to technical capability tags
│   └── recommend.py       # Legacy additive scoring system
├── tests/
│   └── test_scoring.py    # Unit tests for scoring logic
├── README.md              # Documentation
├── app.py                 # Streamlit application entry point
└── requirements.txt       # Project dependencies
```

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

---
*Built for the ICMEC Ishango Hackathon 2026 — Kigali, Rwanda.*
