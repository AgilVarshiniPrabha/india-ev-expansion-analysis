import duckdb, os

con = duckdb.connect("ev.duckdb")
os.makedirs("outputs", exist_ok=True)

queries = {

# 1. How is the fuel mix changing each month? (for a stacked area chart)
"1_national_monthly_fuel": """
SELECT date AS month, fuel_group, SUM(registrations) AS registrations
FROM clean
GROUP BY date, fuel_group
ORDER BY month, fuel_group
""",

# 2. EV share of new vehicles, year by year (2024 = Jan-May only)
"2_national_yearly": """
SELECT
    YEAR(date)                                                      AS year,
    COUNT(DISTINCT date)                                            AS months_of_data,
    SUM(registrations)                                              AS total_vehicles,
    SUM(CASE WHEN fuel_group = 'EV' THEN registrations ELSE 0 END)  AS ev_vehicles,
    ROUND(100.0 * ev_vehicles / total_vehicles, 2)                  AS ev_share_pct
FROM clean
GROUP BY 1
ORDER BY 1
""",

# 3. Every state, every year (for the India map and state trends)
"3_state_year": """
SELECT
    state_name                                                      AS state,
    YEAR(date)                                                      AS year,
    SUM(registrations)                                              AS total_vehicles,
    SUM(CASE WHEN fuel_group = 'EV' THEN registrations ELSE 0 END)  AS ev_vehicles,
    ROUND(100.0 * ev_vehicles / total_vehicles, 2)                  AS ev_share_pct
FROM clean
GROUP BY 1, 2
ORDER BY 1, 2
""",

# 4. The opportunity matrix: EV share (2023) vs EV growth (2022 -> 2023)
#    States compared against the national average on both measures.
#    Only states with 100,000+ vehicles a year (meaningful markets).
"4_state_opportunity": """
WITH s AS (
    SELECT
        state_name AS state,
        SUM(CASE WHEN YEAR(date) = 2023 THEN registrations ELSE 0 END)                      AS market_2023,
        SUM(CASE WHEN YEAR(date) = 2022 AND fuel_group = 'EV' THEN registrations ELSE 0 END) AS ev_2022,
        SUM(CASE WHEN YEAR(date) = 2023 AND fuel_group = 'EV' THEN registrations ELSE 0 END) AS ev_2023
    FROM clean
    GROUP BY state_name
),
nat AS (
    SELECT 100.0 * SUM(ev_2023) / SUM(market_2023)  AS nat_share,
           100.0 * (SUM(ev_2023) / SUM(ev_2022) - 1) AS nat_growth
    FROM s
)
SELECT
    state,
    market_2023,
    ev_2022,
    ev_2023,
    ROUND(100.0 * ev_2023 / market_2023, 1)    AS ev_share_2023,
    ROUND(100.0 * (ev_2023 / ev_2022 - 1), 1)  AS ev_growth_pct,
    CASE
        WHEN 100.0 * ev_2023 / market_2023 >= nat_share
         AND 100.0 * (ev_2023 / ev_2022 - 1) >= nat_growth THEN 'Leaders'
        WHEN 100.0 * ev_2023 / market_2023 >= nat_share     THEN 'Maturing'
        WHEN 100.0 * (ev_2023 / ev_2022 - 1) >= nat_growth  THEN 'Rising stars'
        ELSE 'Laggards'
    END                                        AS segment,
    ROUND(nat_share, 2)                        AS national_share,
    ROUND(nat_growth, 1)                       AS national_growth
FROM s, nat
WHERE market_2023 >= 100000
ORDER BY market_2023 DESC
""",
}

for name, q in queries.items():
    print("\n=== " + name + " ===")
    con.sql(q).show(max_rows=25)
    con.execute(f"COPY ({q}) TO 'outputs/{name}.csv' (HEADER)")

con.close()
print("\nAll 4 files saved in the outputs folder")
