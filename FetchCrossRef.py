{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyP18V9Kr5e/IsFKZDPEkJtJ"
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "code",
      "execution_count": 12,
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "j6fum89GhoPh",
        "outputId": "5bf9a7c8-514b-4f6a-9dbb-e3e30663e27e"
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "2004: 2,283,655\n",
            "2005: 2,351,732\n",
            "2006: 2,599,465\n",
            "2007: 2,965,931\n",
            "2008: 2,997,132\n",
            "2009: 3,296,418\n",
            "2010: 3,463,320\n",
            "2011: 3,888,074\n",
            "2012: 4,067,012\n",
            "2013: 4,387,303\n",
            "2014: 4,541,854\n",
            "2015: 4,667,703\n",
            "2016: 5,083,275\n",
            "2017: 5,528,479\n",
            "2018: 5,888,064\n",
            "2019: 6,493,524\n",
            "2020: 7,369,329\n",
            "2021: 7,550,033\n",
            "2022: 8,218,023\n",
            "2023: 10,124,471\n",
            "2024: 8,695,324\n"
          ]
        }
      ],
      "source": [
        "import requests\n",
        "import time\n",
        "\n",
        "years = range(2004, 2025)\n",
        "counts = {}\n",
        "\n",
        "for y in years:\n",
        "    params = {\n",
        "        'filter': f'from-pub-date:{y}-01-01,until-pub-date:{y}-12-31',\n",
        "        'rows': 0\n",
        "    }\n",
        "    resp = requests.get('https://api.crossref.org/works', params=params)\n",
        "    resp.raise_for_status()\n",
        "    counts[y] = resp.json()['message']['total-results']\n",
        "    print(f\"{y}: {counts[y]:,}\")\n",
        "    time.sleep(1)   # be gentle on the API\n"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import requests\n",
        "import time\n",
        "\n",
        "def fetch_retraction_counts(start_year=2004, end_year=2024, mailto=\"your_email@domain.com\"):\n",
        "    \"\"\"\n",
        "    Queries the Crossref API year-by-year for works whose title\n",
        "    contains any of the specified retraction-related terms.\n",
        "\n",
        "    Returns a dict mapping year -> total count.\n",
        "    \"\"\"\n",
        "    base_url = \"https://api.crossref.org/works\"\n",
        "    query = 'Retraction OR Retracted OR \"Retraction Notice\" OR \"Retraction Note\" OR \"Retracted article\"'\n",
        "    counts = {}\n",
        "\n",
        "    for year in range(start_year, end_year + 1):\n",
        "        params = {\n",
        "            'filter': f'from-pub-date:{year}-01-01,until-pub-date:{year}-12-31',\n",
        "            'query.title': query,\n",
        "            'rows': 0,\n",
        "            'mailto': mailto\n",
        "        }\n",
        "        resp = requests.get(base_url, params=params)\n",
        "        resp.raise_for_status()\n",
        "        total = resp.json()['message']['total-results']\n",
        "        counts[year] = total\n",
        "        print(f\"{year}: {total:,}\")\n",
        "        # Be considerate of rate limits\n",
        "        time.sleep(1.0)\n",
        "\n",
        "    return counts\n",
        "\n",
        "if __name__ == \"__main__\":\n",
        "    # Replace mailto with your contact email per Crossref etiquette\n",
        "    retraction_counts = fetch_retraction_counts()\n",
        "    # `retraction_counts` now holds a mapping of year -> number of title-based retractions\n",
        "\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "QZ9oBpVSjEAH",
        "outputId": "caa94551-0d00-4103-ee6e-a4be23320619"
      },
      "execution_count": 18,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "2004: 6,099\n",
            "2005: 6,469\n",
            "2006: 6,135\n",
            "2007: 6,792\n",
            "2008: 7,570\n",
            "2009: 9,253\n",
            "2010: 13,407\n",
            "2011: 13,902\n",
            "2012: 10,597\n",
            "2013: 11,666\n",
            "2014: 10,959\n",
            "2015: 11,371\n",
            "2016: 11,992\n",
            "2017: 14,383\n",
            "2018: 15,369\n",
            "2019: 17,897\n",
            "2020: 19,443\n",
            "2021: 23,280\n",
            "2022: 27,166\n",
            "2023: 30,690\n",
            "2024: 24,474\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import requests\n",
        "import time\n",
        "\n",
        "def fetch_covid_retraction_counts(start_year=2019, end_year=2024, mailto=\"your_email@domain.com\"):\n",
        "    \"\"\"\n",
        "    Queries Crossref’s REST API year-by-year for publisher-recorded retractions\n",
        "    whose titles mention COVID-19 (or SARS-CoV-2, Coronavirus).\n",
        "    Returns a dict mapping year -> total count.\n",
        "    \"\"\"\n",
        "    base = \"https://api.crossref.org/works\"\n",
        "    covid_terms = \"COVID-19 SARS-CoV-2 Coronavirus\"\n",
        "    results = {}\n",
        "\n",
        "    for year in range(start_year, end_year + 1):\n",
        "        # Build the filter: only retraction updates in that calendar year\n",
        "        date_filter = f\"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31\"\n",
        "        retraction_filter = \"update-type:retraction\"\n",
        "        params = {\n",
        "            \"filter\": f\"{date_filter},{retraction_filter}\",\n",
        "            \"query.title\": covid_terms,\n",
        "            \"rows\": 0,\n",
        "            \"mailto\": mailto\n",
        "        }\n",
        "\n",
        "        resp = requests.get(base, params=params)\n",
        "        resp.raise_for_status()               # should now succeed\n",
        "        total = resp.json()[\"message\"][\"total-results\"]\n",
        "        results[year] = total\n",
        "        print(f\"{year}: {total}\")\n",
        "        time.sleep(1.0)                       # polite pause\n",
        "\n",
        "    return results\n",
        "\n",
        "if __name__ == \"__main__\":\n",
        "    data = fetch_covid_retraction_counts(mailto=\"your_actual_email@domain.com\")\n",
        "    print(\"\\nFinal COVID Retraction Counts:\", data)\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "jdzFFr2Bj3nR",
        "outputId": "21d88e39-137f-49c0-ee0d-309b872b4f09"
      },
      "execution_count": 17,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "2019: 8\n",
            "2020: 137\n",
            "2021: 165\n",
            "2022: 93\n",
            "2023: 149\n",
            "2024: 141\n",
            "\n",
            "Final COVID Retraction Counts: {2019: 8, 2020: 137, 2021: 165, 2022: 93, 2023: 149, 2024: 141}\n"
          ]
        }
      ]
    }
  ]
}