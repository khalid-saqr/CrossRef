#!/usr/bin/env python3
import requests
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# --- Configuration ---
MAILTO = "your_email@domain.com"   # Per CrossRef etiquette
START_YEAR = 2004
END_YEAR = 2024

# --- Fetching functions ---
def fetch_total_publications(start, end, mailto):
    """Yearly total DOI registrations from CrossRef."""
    counts = {}
    for y in range(start, end + 1):
        params = {
            'filter': f'from-pub-date:{y}-01-01,until-pub-date:{y}-12-31',
            'rows': 0,
            'mailto': mailto
        }
        resp = requests.get('https://api.crossref.org/works', params=params)
        resp.raise_for_status()
        counts[y] = resp.json()['message']['total-results']
        time.sleep(1)
    return counts

def fetch_retraction_counts(start, end, mailto):
    """Yearly CrossRef works whose titles contain retraction keywords."""
    query = 'Retraction OR Retracted OR "Retraction Notice" OR "Retraction Note" OR "Retracted article"'
    counts = {}
    for y in range(start, end + 1):
        params = {
            'filter': f'from-pub-date:{y}-01-01,until-pub-date:{y}-12-31',
            'query.title': query,
            'rows': 0,
            'mailto': mailto
        }
        resp = requests.get('https://api.crossref.org/works', params=params)
        resp.raise_for_status()
        counts[y] = resp.json()['message']['total-results']
        time.sleep(1)
    return counts

def fetch_covid_retraction_counts(start, end, mailto):
    """Yearly CrossRef retraction notices mentioning COVID-19."""
    covid_terms = "COVID-19 SARS-CoV-2 Coronavirus"
    counts = {}
    for y in range(start, end + 1):
        params = {
            'filter': f'from-pub-date:{y}-01-01,until-pub-date:{y}-12-31,update-type:retraction',
            'query.title': covid_terms,
            'rows': 0,
            'mailto': mailto
        }
        resp = requests.get('https://api.crossref.org/works', params=params)
        resp.raise_for_status()
        counts[y] = resp.json()['message']['total-results']
        time.sleep(1)
    return counts

# --- Main report assembly ---
if __name__ == "__main__":
    # 1. Fetch data
    print("\nFetching total publication counts...")
    pubs = fetch_total_publications(START_YEAR, END_YEAR, MAILTO)

    print("\nFetching retraction counts...")
    retractions = fetch_retraction_counts(START_YEAR, END_YEAR, MAILTO)

    print("\nFetching COVID-19 retraction counts...")
    covid_retracts = fetch_covid_retraction_counts(2019, END_YEAR, MAILTO)

    # 2. Build DataFrame
    df = pd.DataFrame({
        'Year': list(range(START_YEAR, END_YEAR+1)),
        'Total_Publications': [pubs[y] for y in range(START_YEAR, END_YEAR+1)],
        'Retractions': [retractions[y] for y in range(START_YEAR, END_YEAR+1)],
        'COVID_Retractions': [covid_retracts.get(y, 0) for y in range(START_YEAR, END_YEAR+1)]
    })
    df.set_index('Year', inplace=True)

    # 3. Print tables
    pd.set_option('display.max_rows', None)
    print("\n=== Yearly Totals ===")
    print(df)

    # 4. Plot 1: Publications with exponential fit & doubling markers
    years = df.index.values
    vals = df['Total_Publications'].values
    slope, intercept, r_val, _, _ = linregress(years, np.log(vals))
    fit = np.exp(intercept + slope * years)

    # Doubling thresholds
    base = vals[0]
    doubles = [2*base, 4*base]
    dbl_years = [years[np.argmax(vals >= d)] for d in doubles]

    plt.figure(figsize=(10,6))
    plt.scatter(years, vals/1e6, color='navy', s=50, label='Data')
    plt.plot(years, fit/1e6, 'r-', label=f'Fit ($R^2$={r_val**2:.3f})')
    for i, dy in enumerate(dbl_years, start=1):
        plt.plot(dy, vals[dy-START_YEAR]/1e6, 'k*', markersize=15, label=f'{i*2}× @ {dy}')
    plt.title('CrossRef Publications (2004–2024)')
    plt.xlabel('Year')
    plt.ylabel('Publications (millions)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('publications.png')
    print("\nSaved plot: publications.png")

    # 5. Plot 2: Retractions vs COVID retractions (log scale)
    plt.figure(figsize=(10,6))
    w = 0.4
    plt.bar(years - w/2, df['Retractions'], width=w, color='skyblue', label='Retractions')
    plt.bar(years + w/2, df['COVID_Retractions'], width=w, color='salmon', label='COVID-19 Retractions')
    plt.yscale('log')
    plt.title('Retractions vs COVID-19 Retractions (2004–2024)')
    plt.xlabel('Year')
    plt.ylabel('Count (log scale)')
    plt.legend()
    plt.grid(which='both', axis='y', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig('retractions.png')
    print("Saved plot: retractions.png\n")
