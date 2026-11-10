# India's EV Shift: Where Should an EV Maker Expand Next?

**Interactive dashboard:** [View on Tableau Public](https://public.tableau.com/app/profile/agil.prabhakaran/viz/IndiaEVExpansionAnalysis)

## Business question
An electric two-wheeler company wants to expand its dealership and charging network.
**Which Indian states should it target next, and why?**

## Data
- **Source:** Government of India VAHAN vehicle registration database (via Transport Data Commons / India Data Portal)
- **Coverage:** Jan 2019 – May 2024, monthly, by state, RTO office and fuel type
- **Size:** 418,372 rows, ~1,300 RTO offices, 34 states/UTs

## Data cleaning: the key challenge
The raw file was badly inflated: it showed **388 million** vehicles registered in 2020 (India's real figure is ~18-19 million).

**Root cause:** about 20 RTO offices were carrying **all-India or state totals** instead of their own numbers.
For example, *Lower Siang (Arunachal Pradesh)*, a small district, showed 2.3 million petrol vehicles in a single month.

**Fix:** no real RTO registers more than ~35,000 vehicles a month (the largest, e.g. Pune, peak near 32,000).
Office-months above this limit were removed, along with one fitness centre (RJ204) reporting state totals.
- Rows removed: 4,712 of 418,372 (~1%)
- **Validation:** the cleaned data gives **1.55 million EVs in 2023 (6.4% share)**, in line with widely reported national EV sales for that year.

Fuel types (22 raw values) were grouped into 6: EV, Hybrid, CNG/LPG, Petrol, Diesel, Other.

## Approach
1. Load raw CSV into DuckDB; clean with SQL (`load_clean.py`)
2. Analysis in SQL (`analysis.py`): national trend, state-by-year EV share, state opportunity matrix
3. Dashboard in Tableau Public

**Opportunity matrix:** each state (100,000+ vehicles/year) is placed by
- EV share of new vehicles in 2023 (national average 6.4%), and
- EV growth 2022 to 2023 (national average 49%),

giving four segments: **Leaders, Maturing, Rising stars, Laggards**.

## Key findings
- EV share of new vehicles rose from **0.7% (2019) to 6.4% (2023)**, and 7.1% in Jan-May 2024.
- **1.55 million EVs** were registered in 2023, up 49% from 1.04 million in 2022; monthly EV registrations grew ~9x from 2019 to 2023.
- **Leaders:** Uttar Pradesh (largest market, 8.1% share, +71%), Karnataka (8.7%), Kerala (10.0%), Bihar, Chhattisgarh.
- **Rising stars (low share, fast growth):**

| State | Vehicles/yr (2023) | EV share | EV growth |
|---|---|---|---|
| Madhya Pradesh | 1.50M | 4.5% | +85% |
| West Bengal | 1.00M | 2.1% | +92% |
| Punjab | 0.64M | 4.0% | +83% |
| Jharkhand | 0.54M | 3.9% | +54% |
| Jammu & Kashmir | 0.17M | 5.7% | +108% |

## Recommendation
**Prioritise Madhya Pradesh, West Bengal and Punjab.** Together they register ~3.1 million vehicles a year,
EV share is still below 5%, and EV registrations are growing 80%+ a year: demand is taking off before the market is crowded.
Leaders such as Kerala and Karnataka already have high EV share and stronger competition.

## Limitations
- **Telangana is not in the VAHAN data** for this period, so it is excluded.
- This dataset has **fuel type but not vehicle type** (2-wheeler, 3-wheeler, car), so EV share covers all vehicle types.
- 2024 covers January-May only.
- Growth is measured over one year (2022 to 2023); a longer window would smooth out one-off effects.

## Tools
Python, DuckDB (SQL), Tableau Public

## Files
| File | Purpose |
|---|---|
| `load_clean.py` | Loads the raw VAHAN CSV and removes the inflated rows |
| `analysis.py` | Runs the analysis and exports 4 CSVs for Tableau |
| `outputs/` | Analysis tables used in the dashboard |
