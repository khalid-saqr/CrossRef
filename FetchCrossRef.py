import requests
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.optimize import curve_fit
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

# ==== CONFIG ====
MAILTO = "research@knowdyn.co.uk"
START_YEAR, END_YEAR = 2004, 2024
years = np.arange(START_YEAR, END_YEAR + 1)

# ==== SESSION with RETRY ====
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=["GET"])
session.mount("https://", HTTPAdapter(max_retries=retries))

def fetch_counts(filter_args, start, end, mailto, query_title=None):
    """Generic fetcher for CrossRef counts (with optional title search)."""
    results = {}
    for year in range(start, end + 1):
        base_filter = f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31"
        full_filter = f"{base_filter},{filter_args}" if filter_args else base_filter
        params = {'filter': full_filter, 'rows': 0, 'mailto': mailto}
        if query_title is not None:
            params['query.title'] = query_title
        try:
            resp = session.get('https://api.crossref.org/works', params=params, timeout=30)
            resp.raise_for_status()
            count = resp.json()['message']['total-results']
        except Exception as e:
            print(f"ERROR fetching {year}: {e}")
            count = None
        results[year] = count
        time.sleep(0.2)
    return results

# ==== DATA FETCH ====
pubs = fetch_counts("", START_YEAR, END_YEAR, MAILTO)
rets = fetch_counts("", START_YEAR, END_YEAR, MAILTO,
    query_title='Retraction OR Retracted OR "Retraction Notice" OR "Retraction Note" OR "Retracted article"')
covid = fetch_counts("update-type:retraction", 2019, END_YEAR, MAILTO,
    query_title="COVID-19 OR SARS-CoV-2 OR Coronavirus")
preprints = fetch_counts("type:posted-content", START_YEAR, END_YEAR, MAILTO)

df = pd.DataFrame({
    'Publications': [pubs.get(y) for y in years],
    'Retractions': [rets.get(y) for y in years],
    'COVID_Retraction': [covid.get(y, 0) for y in years],
    'Preprints': [preprints.get(y) for y in years]
}, index=years)

# ==== REGRESSION FUNCTIONS ====
def exp_fit(x, a, b):
    return a * np.exp(b * (x - x[0]))
def quad_fit(x, a, b, c):
    return a * (x - x[0])**2 + b * (x - x[0]) + c
def logistic_fit(x, L, k, x0):
    return L / (1 + np.exp(-k*(x - x0)))

def model_compare(x, y):
    mask = (np.array(y) > 0) & ~np.isnan(y)
    x, y = np.array(x)[mask], np.array(y)[mask]
    # Exponential (log-linear)
    slope, intercept, r2, _, _ = linregress(x, np.log(y))
    y_exp = np.exp(intercept + slope * x)
    exp_r2 = 1 - np.sum((y - y_exp) ** 2) / np.sum((y - y.mean()) ** 2)
    # Quadratic
    qparams = np.polyfit(x-x[0], y, 2)
    y_quad = np.polyval(qparams, x-x[0])
    quad_r2 = 1 - np.sum((y - y_quad) ** 2) / np.sum((y - y.mean()) ** 2)
    # Logistic
    try:
        L0, k0, x0_0 = max(y), 0.2, x[y.argmax()] if len(y) > 1 else x[0]
        lparams, _ = curve_fit(logistic_fit, x, y, p0=[L0, k0, x0_0], maxfev=10000)
        y_logi = logistic_fit(x, *lparams)
        logi_r2 = 1 - np.sum((y - y_logi) ** 2) / np.sum((y - y.mean()) ** 2)
    except Exception:
        y_logi, logi_r2, lparams = y, np.nan, [np.nan]*3
    # Doubling time (exp only)
    dt = np.log(2) / slope if slope > 0 else np.nan
    return {
        'exp': (y_exp, exp_r2, slope, dt),
        'quad': (y_quad, quad_r2, qparams),
        'logi': (y_logi, logi_r2, lparams)
    }

results = {}
summary = {}
for col in ['Publications', 'Retractions', 'Preprints']:
    res = model_compare(df.index.values, df[col].values)
    results[col] = res
    summary[col] = {
        'exp_r2': res['exp'][1],
        'quad_r2': res['quad'][1],
        'logi_r2': res['logi'][1],
        'exp_doubling': res['exp'][3]
    }
    # add fits to df
    df[f'{col}_ExpFit'] = np.nan
    df[f'{col}_QuadFit'] = np.nan
    df[f'{col}_LogiFit'] = np.nan
    mask = (df[col].values > 0) & ~np.isnan(df[col].values)
    x = df.index.values[mask]
    df.loc[x, f'{col}_ExpFit'] = res['exp'][0]
    df.loc[x, f'{col}_QuadFit'] = res['quad'][0]
    df.loc[x, f'{col}_LogiFit'] = res['logi'][0]

# ==== PLOTS ====
def plot_compare(col, scale=1, ylabel='', fname='plot.png'):
    x = df.index.values
    plt.figure(figsize=(10, 6))
    plt.scatter(x, df[col]/scale, c='k', label='Data')
    plt.plot(x, df[f'{col}_ExpFit']/scale, 'r-', label=f'Exp fit ($R^2$={summary[col]["exp_r2"]:.3f})')
    plt.plot(x, df[f'{col}_QuadFit']/scale, 'g--', label=f'Quad fit ($R^2$={summary[col]["quad_r2"]:.3f})')
    plt.plot(x, df[f'{col}_LogiFit']/scale, 'b:', label=f'Logistic fit ($R^2$={summary[col]["logi_r2"]:.3f})')
    plt.title(f'{col} Trend and Fits')
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.grid(True, linestyle=':')
    plt.legend()
    plt.tight_layout()
    plt.savefig(fname, dpi=150)
    plt.close()

plot_compare('Publications', scale=1e6, ylabel='Publications (Millions)', fname='publications_compare.png')
plot_compare('Retractions', scale=1e3, ylabel='Retractions (Thousands)', fname='retractions_compare.png')
plot_compare('Preprints', scale=1e3, ylabel='Preprints (Thousands)', fname='preprints_compare.png')

# ==== SAVE ====
df.to_csv('analysis_time_series.csv', float_format='%.4f')
pd.DataFrame(summary).to_csv('regression_summary.csv')

print("Plots and CSVs saved (analysis_time_series.csv, regression_summary.csv, and 3 PNGs).")
