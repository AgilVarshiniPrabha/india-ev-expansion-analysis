import duckdb, glob

con = duckdb.connect("ev.duckdb")
csv_path = glob.glob("data/vahan-vehicle-registrations-by-fuel-type*.csv")[0]

# ---------------------------------------------------------------
# STEP 1: Load the raw file exactly as downloaded
# ---------------------------------------------------------------
con.execute(f"CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv_auto('{csv_path}')")

# ---------------------------------------------------------------
# STEP 2: Clean it
# Problem found: ~20 RTO offices carry ALL-INDIA (or state) totals
# instead of their own numbers, e.g. "Lower Siang, Arunachal Pradesh"
# shows 2.3 million petrol vehicles in one month.
# Rule: a single RTO never registers more than ~35,000 vehicles a
# month (the biggest real ones, like Pune, peak around 32,000).
# So we drop any office-month above 35,000, plus one fitness centre
# (RJ204) that reports state-level totals.
# ---------------------------------------------------------------
con.execute("""
CREATE OR REPLACE TABLE clean AS
WITH office_month AS (
    SELECT office_code, date, SUM(registrations) AS office_month_total
    FROM raw
    GROUP BY office_code, date
)
SELECT
    r.date,
    r.state_name,
    r.office_code,
    r.office_name,
    r.fuel_type,
    CASE
        WHEN r.fuel_type IN ('Electric(Bov)', 'Pure Ev') THEN 'EV'
        WHEN r.fuel_type IN ('Petrol/Hybrid', 'Diesel/Hybrid', 'Strong Hybrid Ev',
                             'Plug-In Hybrid Ev') THEN 'Hybrid'
        WHEN r.fuel_type IN ('Cng Only', 'Petrol/Cng', 'Lpg Only', 'Petrol/Lpg', 'Lng',
                             'Dual Diesel/Cng', 'Dual Diesel/Lng', 'Dual Diesel/Bio Cng')
             THEN 'CNG/LPG'
        WHEN r.fuel_type IN ('Petrol', 'Petrol/Ethanol', 'Ethanol') THEN 'Petrol'
        WHEN r.fuel_type = 'Diesel' THEN 'Diesel'
        ELSE 'Other'
    END AS fuel_group,
    r.registrations
FROM raw r
JOIN office_month om
  ON r.office_code = om.office_code AND r.date = om.date
WHERE om.office_month_total <= 35000
  AND r.office_code <> 'RJ204'
""")

# ---------------------------------------------------------------
# STEP 3: Check the effect of cleaning
# ---------------------------------------------------------------
print("\n=== Rows before vs after cleaning ===")
con.sql("""
SELECT raw_rows, clean_rows, raw_rows - clean_rows AS rows_removed
FROM (SELECT (SELECT COUNT(*) FROM raw)   AS raw_rows,
             (SELECT COUNT(*) FROM clean) AS clean_rows)
""").show()

print("=== Total registrations per year: before vs after (in millions) ===")
con.sql("""
SELECT r.yr AS year, r.raw_millions, c.clean_millions
FROM (SELECT YEAR(date) AS yr, ROUND(SUM(registrations)/1e6, 1) AS raw_millions
      FROM raw GROUP BY yr) r
JOIN (SELECT YEAR(date) AS yr, ROUND(SUM(registrations)/1e6, 1) AS clean_millions
      FROM clean GROUP BY yr) c ON r.yr = c.yr
ORDER BY year
""").show()

print("=== EV share of new registrations, by year ===")
con.sql("""
SELECT
    YEAR(date)                                                        AS year,
    SUM(registrations)                                                AS total_vehicles,
    SUM(CASE WHEN fuel_group = 'EV' THEN registrations ELSE 0 END)    AS ev_vehicles,
    ROUND(100.0 * ev_vehicles / total_vehicles, 2)                    AS ev_share_pct
FROM clean
GROUP BY 1
ORDER BY 1
""").show()

con.close()
print("Done. Clean data saved in ev.duckdb (table: clean)")
