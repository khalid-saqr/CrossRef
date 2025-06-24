# CrossRef Publication & Retraction Fetcher

A reproducible Python toolkit for meta-research on scholarly publishing trends.  
Fetches and analyzes year-by-year:

1. Total CrossRef DOI registrations (2004–2024)  
2. Retraction-related documents (2004–2024)  
3. COVID-19 retractions (2019–2024)

Generates summary tables and two publication-quality plots:
- `publications.png` (exponential fit, doubling‐time markers)  
- `retractions.png` (total vs. COVID-19 retractions on log scale)  

---

## Features

- Three CrossRef queries via the REST API with polite rate-limiting (1 s delay).
- Automated data framing into pandas DataFrames.
- Matplotlib visualizations with fit statistics (using SciPy’s `linregress`).
- Calculation of:
  - Exponential growth rates,  
  - $R^2$ of log-linear fits,  
  - Doubling times.
- Self-contained script with no external config files.
- MIT-licensed, production-ready for GitHub Actions or local use.

---

## 📦 Installation

```bash
# Clone this repo
git clone https://github.com/yourorg/retract-tracker.git
cd retract-tracker

# Create a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
