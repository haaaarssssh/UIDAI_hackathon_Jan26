# import pandas as pd
# import numpy as np
# import duckdb
# import os
# from statsmodels.tsa.api import Holt
# from sklearn.linear_model import LinearRegression
# from scipy.stats import zscore

# # -----------------------------------------------------------------------------
# # 1. DATA INGESTION
# # -----------------------------------------------------------------------------
# print("🔹 Starting ETL Pipeline...")

# def load_data():
#     try:
#         print("   Attempting to load CSVs from 'data/level3_processing/'...")
        
#         bio_path = 'data/level3_processing/processed_biometric_data.csv'
#         enrol_path = 'data/level3_processing/processed_enrolment_data.csv'
#         demo_path = 'data/level3_processing/processed_demographic_data.csv'
        
#         # FIX 1: Add dayfirst=True to handle your date format (DD/MM/YYYY)
#         bio = pd.read_csv(bio_path, parse_dates=['date'], dayfirst=True)
#         enrol = pd.read_csv(enrol_path, parse_dates=['date'], dayfirst=True)
#         demo = pd.read_csv(demo_path, parse_dates=['date'], dayfirst=True)
        
#         print("   ✅ CSVs loaded successfully.")
#         return bio, enrol, demo
#     except FileNotFoundError as e:
#         print(f"   ❌ Error: {e}")
#         return None, None, None

# df_bio, df_enrol, df_demo = load_data()

# if df_bio is None:
#     exit()

# # -----------------------------------------------------------------------------
# # 2. MERGING & MAPPING
# # -----------------------------------------------------------------------------
# print("🔹 Merging & mapping columns...")

# # Merge
# df_merged = df_enrol.merge(df_bio, on=['date', 'state', 'district', 'pincode'], how='outer')\
#                     .merge(df_demo, on=['date', 'state', 'district', 'pincode'], how='outer')

# df_merged = df_merged.fillna(0)

# # FIX 2: FORCE Date Conversion (Crucial step to fix TypeError)
# df_merged['date'] = pd.to_datetime(df_merged['date'], dayfirst=True, errors='coerce')
# # Remove any rows where date couldn't be parsed
# df_merged = df_merged.dropna(subset=['date'])

# # Map Columns
# df_merged['total_enrol'] = df_merged['age_0_5'] + df_merged['age_5_17'] + df_merged['age_18_greater']
# df_merged['total_bio'] = df_merged['bio_age_5_17'] + df_merged['bio_age_17_']
# df_merged['total_demo'] = df_merged['demo_age_5_17'] + df_merged['demo_age_17_']
# df_merged['total_transactions'] = df_merged['total_enrol'] + df_merged['total_bio'] + df_merged['total_demo']
# df_merged['total_adult_enrolments'] = df_merged['age_18_greater']
# df_merged['total_child_enrolments'] = df_merged['age_0_5'] + df_merged['age_5_17']

# # -----------------------------------------------------------------------------
# # 3. NAME STANDARDIZATION
# # -----------------------------------------------------------------------------
# print("🔹 Standardizing State Names...")
# state_mapper = {
#     "Andaman and Nicobar Islands": "Andaman and Nicobar",
#     "Dadra and Nagar Haveli and Daman and Diu": "Dādra and Nagar Haveli and Damān and Diu",
#     "Odisha": "Orissa",
#     "Uttarakhand": "Uttaranchal",
#     "Jammu and Kashmir": "Jammu and Kashmir",
#     "Ladakh": "Ladakh"
# }
# df_merged['state'] = df_merged['state'].apply(lambda x: state_mapper.get(x, x))

# # -----------------------------------------------------------------------------
# # 4. AGGREGATION
# # -----------------------------------------------------------------------------
# print("🔹 Aggregating Data...")

# # A. District Daily
# df_daily = df_merged.groupby(['date', 'state', 'district'])[[
#     'total_transactions', 'total_enrol', 'total_bio', 'total_demo'
# ]].sum().reset_index()

# # B. District Summary
# df_summary = df_merged.groupby(['state', 'district']).agg({
#     'total_transactions': 'sum',
#     'total_adult_enrolments': 'sum',
#     'total_child_enrolments': 'sum',
#     'total_bio': 'sum',
#     'total_demo': 'sum',
#     'pincode': 'count'
# }).reset_index()

# # Consistency & Archetypes
# stats = df_daily.groupby(['state', 'district'])['total_transactions'].agg(['mean', 'std'])
# df_summary = df_summary.merge(stats, on=['state', 'district'])
# df_summary['consistency'] = (1 - (df_summary['std'] / df_summary['mean'])).clip(0, 1) * 100
# df_summary.rename(columns={'mean': 'intensity'}, inplace=True)
# df_summary['intensity'] = df_summary['intensity'].fillna(0)
# df_summary['consistency'] = df_summary['consistency'].fillna(0)

# c_thresh = df_summary['consistency'].quantile(0.75)
# i_thresh = df_summary['intensity'].quantile(0.75)

# def get_archetype(row):
#     if row['consistency'] >= c_thresh and row['intensity'] >= i_thresh: return 'High-Consistency / High-Intensity'
#     elif row['consistency'] >= c_thresh: return 'High-Consistency / Stable'
#     elif row['intensity'] >= i_thresh: return 'High-Intensity / Sporadic'
#     return 'Standard Operations'

# df_summary['archetype_label'] = df_summary.apply(get_archetype, axis=1)

# # Risk Scores
# df_summary['z_score'] = df_summary.groupby('state')['total_adult_enrolments'].transform(
#     lambda x: zscore(x, nan_policy='omit')
# ).fillna(0)
# df_summary['risk_color'] = np.where(df_summary['z_score'] >= 2, 'Anomaly', 'Normal')
# df_summary['migration_index'] = (df_summary['total_demo'] / df_summary['total_transactions']).fillna(0)

# # Strategy Quadrants
# med_enrol = df_summary['total_child_enrolments'].median()
# med_update = (df_summary['total_bio'] + df_summary['total_demo']).median()

# def get_quadrant(row):
#     e = row['total_child_enrolments']
#     u = row['total_bio'] + row['total_demo']
#     if e >= med_enrol and u >= med_update: return "Scale Everything"
#     elif u >= med_update: return "Focus on Updates"
#     elif e >= med_enrol: return "Focus on Enrolment"
#     return "Maintain / Monitor"

# df_summary['Quadrant'] = df_summary.apply(get_quadrant, axis=1)

# # Enrolment Gap
# X = df_summary['total_transactions'].values.reshape(-1, 1)
# y = df_summary['total_child_enrolments'].values
# if len(y) > 0:
#     reg = LinearRegression().fit(X, y)
#     df_summary['enrolment_gap'] = reg.predict(X) - y
# else:
#     df_summary['enrolment_gap'] = 0

# # -----------------------------------------------------------------------------
# # 5. FORECASTING & SIMULATION
# # -----------------------------------------------------------------------------
# print("🔹 Running Models...")

# # Forecasts
# forecast_records = []

# # FIX 3: Use 'ME' instead of 'M' for future compatibility
# full_dates = pd.date_range(start=df_daily['date'].min(), end=df_daily['date'].max(), freq='ME')

# for state in df_daily['state'].unique():
#     # FIX 4: Explicit set_index and Sort to prevent Resample TypeError
#     state_data = df_daily[df_daily['state'] == state].copy()
#     state_data = state_data.sort_values('date').set_index('date')
    
#     # FIX 3 applied here as well ('ME')
#     monthly = state_data['total_transactions'].resample('ME').sum()
#     monthly = monthly.reindex(full_dates).fillna(0)
    
#     for d, v in monthly.items():
#         forecast_records.append({'state': state, 'month': d, 'value': v, 'type': 'Historical'})
        
#     try:
#         if len(monthly) > 2: # Check if enough data
#             model = Holt(monthly, initialization_method="estimated").fit()
#             future = model.forecast(3)
#             for d, v in future.items():
#                 forecast_records.append({'state': state, 'month': d, 'value': max(0, v), 'type': 'Forecast'})
#     except Exception as e:
#         # print(f"Forecast error for {state}: {e}")
#         pass

# df_forecasts = pd.DataFrame(forecast_records)

# # Simulations
# sim_stats = []
# sim_raw = []

# for district, group in df_daily.groupby('district'):
#     data = group['total_transactions'].values
#     if len(data) > 5:
#         sims = np.random.choice(data, size=(1000, 30))
#         monthly_sums = sims.sum(axis=1)
        
#         sim_stats.append({
#             'district': district,
#             'p10': np.percentile(monthly_sums, 10),
#             'p50': np.percentile(monthly_sums, 50),
#             'p90': np.percentile(monthly_sums, 90)
#         })
        
#         for x in monthly_sums[:200]:
#             sim_raw.append({'district': district, 'sim_value': x})

# df_sim_stats = pd.DataFrame(sim_stats)
# df_sim_raw = pd.DataFrame(sim_raw)

# # -----------------------------------------------------------------------------
# # 6. SAVE TO DATABASE
# # -----------------------------------------------------------------------------
# print("🔹 Saving to DuckDB...")
# if not os.path.exists('database'):
#     os.makedirs('database')

# con = duckdb.connect('database/analytics.db')
# con.execute("CREATE OR REPLACE TABLE district_summary AS SELECT * FROM df_summary")
# con.execute("CREATE OR REPLACE TABLE district_daily AS SELECT * FROM df_daily")
# con.execute("CREATE OR REPLACE TABLE state_forecasts AS SELECT * FROM df_forecasts")
# con.execute("CREATE OR REPLACE TABLE sim_stats AS SELECT * FROM df_sim_stats")
# con.execute("CREATE OR REPLACE TABLE sim_raw AS SELECT * FROM df_sim_raw")
# con.close()

# print("✅ ETL Complete. Database updated.")

import pandas as pd
import numpy as np
import duckdb
import os
import pgeocode
from sklearn.linear_model import LinearRegression
from scipy.stats import zscore

print("🔹 Starting Master ETL Pipeline (With Calendar Aggregates)...")

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------
def load_data():
    try:
        base_dir = 'data/level4_processing'
        if not os.path.exists(base_dir):
            print(f"❌ Error: {base_dir} not found. Run create_level4_data.py first.")
            exit()
            
        bio = pd.read_csv(os.path.join(base_dir, 'processed_biometric_data.csv'), parse_dates=['date'], dayfirst=True)
        enrol = pd.read_csv(os.path.join(base_dir, 'processed_enrolment_data.csv'), parse_dates=['date'], dayfirst=True)
        demo = pd.read_csv(os.path.join(base_dir, 'processed_demographic_data.csv'), parse_dates=['date'], dayfirst=True)
        return bio, enrol, demo
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        exit()

df_bio, df_enrol, df_demo = load_data()

# ---------------------------------------------------------
# 2. MERGE
# ---------------------------------------------------------
print("🔹 Merging Data...")
df_merged = df_enrol.merge(df_bio, on=['date', 'state', 'district', 'pincode'], how='outer')\
                    .merge(df_demo, on=['date', 'state', 'district', 'pincode'], how='outer').fillna(0)

df_merged['total_child_enrolments'] = df_merged['age_0_5'] + df_merged['age_5_17']
df_merged['total_adult_enrolments'] = df_merged['age_18_greater']
df_merged['total_enrol'] = df_merged['total_child_enrolments'] + df_merged['total_adult_enrolments']
df_merged['total_bio'] = df_merged['bio_age_5_17'] + df_merged['bio_age_17_']
df_merged['total_demo'] = df_merged['demo_age_5_17'] + df_merged['demo_age_17_']
df_merged['total_transactions'] = df_merged['total_enrol'] + df_merged['total_bio'] + df_merged['total_demo']
df_merged['month_num'] = df_merged['date'].dt.month

# ---------------------------------------------------------
# 3. PAGE 1 TABLES
# ---------------------------------------------------------
print("🔹 Generating Page 1 Data...")

# A. District Daily (Granular)
df_daily = df_merged.groupby(['date', 'state', 'district'])[[
    'total_transactions', 'total_enrol', 'total_bio', 'total_demo'
]].sum().reset_index()

# B. State Daily (NEW: For Home Page Calendar)
df_state_daily = df_daily.groupby(['date', 'state'])['total_transactions'].sum().reset_index()

# C. National Daily (NEW: For Home Page Calendar)
df_national_daily = df_daily.groupby(['date'])['total_transactions'].sum().reset_index()

# D. Pincode Daily (For Pulse Drill-down)
df_pin_daily = df_merged.groupby(['date', 'state', 'district', 'pincode'])[[
    'total_demo', 'total_transactions'
]].sum().reset_index()

# E. Monthly Aggregates
df_state_monthly = df_merged.groupby(['state', 'month_num'])['total_demo'].sum().reset_index()
df_dist_monthly = df_merged.groupby(['state', 'district', 'month_num'])['total_demo'].sum().reset_index()
df_pin_monthly = df_merged.groupby(['state', 'district', 'pincode', 'month_num'])['total_demo'].sum().reset_index()

# Map Coords
df_pincode_agg = df_merged.groupby(['state', 'district', 'pincode']).agg({'total_transactions': 'sum'}).reset_index()
nomi = pgeocode.Nominatim('in')
unique_pins = df_pincode_agg['pincode'].astype(str).unique()
geo_results = nomi.query_postal_code(unique_pins)
df_geo_map = pd.DataFrame({'pincode': unique_pins, 'lat': geo_results.latitude, 'lon': geo_results.longitude})
df_pincode_agg['pincode'] = df_pincode_agg['pincode'].astype(str)
df_geo_map['pincode'] = df_geo_map['pincode'].astype(str)
df_final_pin = df_pincode_agg.merge(df_geo_map, on='pincode', how='left').dropna(subset=['lat', 'lon'])

q75, q25 = df_final_pin['total_transactions'].quantile(0.75), df_final_pin['total_transactions'].quantile(0.25)
df_final_pin['archetype'] = df_final_pin['total_transactions'].apply(lambda x: "High Volume" if x > q75 else ("Remote Node" if x < q25 else "Standard"))

df_dist_geo = df_final_pin.groupby(['state', 'district']).agg({'lat': 'mean', 'lon': 'mean', 'total_transactions': 'sum', 'pincode': 'count'}).reset_index().rename(columns={'pincode': 'active_pincodes'})
df_state_geo = df_final_pin.groupby(['state']).agg({'lat': 'mean', 'lon': 'mean', 'total_transactions': 'sum', 'district': 'nunique'}).reset_index()

# ---------------------------------------------------------
# 4. PAGE 2 RISK ENGINE
# ---------------------------------------------------------
print("🔹 Generating Page 2 Risk Data...")
def calculate_risk(df):
    if len(df) < 5: 
        df['predicted_enrol'] = df['total_enrol']; df['residual'] = 0; df['z_score'] = 0; df['Status'] = 'Normal'; df['migration_index'] = 0
        return df
    X = df['total_transactions'].values.reshape(-1, 1); y = df['total_enrol'].values
    model = LinearRegression().fit(X, y)
    df['predicted_enrol'] = model.predict(X)
    df['residual'] = df['total_enrol'] - df['predicted_enrol']
    res_std = df['residual'].std()
    df['z_score'] = zscore(df['residual']) if res_std != 0 else 0
    df['Status'] = df['z_score'].apply(lambda z: "Ghost Risk" if z < -1.5 else ("High Growth" if z > 1.5 else "Normal"))
    df['migration_index'] = (df['total_demo'] / df['total_transactions'].replace(0, 1) * 100).round(1)
    return df

state_risk = calculate_risk(df_daily.groupby('state')[['total_transactions', 'total_enrol', 'total_demo']].sum().reset_index())
dist_risk = df_daily.groupby(['state', 'district'])[['total_transactions', 'total_enrol', 'total_demo']].sum().reset_index()
dist_risk = dist_risk.groupby('state', group_keys=False).apply(calculate_risk)
pin_risk = df_merged.groupby(['state', 'district', 'pincode'])[['total_transactions', 'total_enrol', 'total_demo']].sum().reset_index()
pin_risk = pin_risk.groupby(['state', 'district'], group_keys=False).apply(calculate_risk)

# ---------------------------------------------------------
# 5. PAGE 3 STRATEGIC PLANNER
# ---------------------------------------------------------
print("🔹 Generating Page 3 Strategies...")

def calculate_gap(df):
    if len(df) < 3: 
        df['enrolment_gap'] = 0
        return df
    X = df['total_transactions'].values.reshape(-1, 1)
    y = df['total_child_enrolments'].values
    model = LinearRegression().fit(X, y)
    expected = model.predict(X)
    df['enrolment_gap'] = (expected - y).round(0)
    return df

df_state_summary = calculate_gap(df_merged.groupby(['state']).agg({
    'total_transactions': 'sum', 'total_child_enrolments': 'sum', 'total_adult_enrolments': 'sum', 'total_bio': 'sum', 'total_demo': 'sum'
}).reset_index())

df_dist_summary = calculate_gap(df_merged.groupby(['state', 'district']).agg({
    'total_transactions': 'sum', 'total_child_enrolments': 'sum', 'total_adult_enrolments': 'sum', 'total_bio': 'sum', 'total_demo': 'sum'
}).reset_index())

df_pin_summary = df_merged.groupby(['state', 'district', 'pincode']).agg({
    'total_transactions': 'sum', 'total_child_enrolments': 'sum', 'total_adult_enrolments': 'sum', 'total_bio': 'sum', 'total_demo': 'sum'
}).reset_index()
df_pin_summary = df_pin_summary.groupby(['state', 'district'], group_keys=False).apply(calculate_gap)

# ---------------------------------------------------------
# 6. SAVE
# ---------------------------------------------------------
print("🔹 Saving to DuckDB...")
if not os.path.exists('database'): os.makedirs('database')
con = duckdb.connect('database/analytics.db')

# Page 1
con.execute("CREATE OR REPLACE TABLE pin_geo AS SELECT * FROM df_final_pin")
con.execute("CREATE OR REPLACE TABLE dist_geo AS SELECT * FROM df_dist_geo")
con.execute("CREATE OR REPLACE TABLE state_geo AS SELECT * FROM df_state_geo")
con.execute("CREATE OR REPLACE TABLE district_daily AS SELECT * FROM df_daily")
con.execute("CREATE OR REPLACE TABLE pincode_daily AS SELECT * FROM df_pin_daily")
con.execute("CREATE OR REPLACE TABLE state_monthly AS SELECT * FROM df_state_monthly")
con.execute("CREATE OR REPLACE TABLE district_monthly AS SELECT * FROM df_dist_monthly")
con.execute("CREATE OR REPLACE TABLE pincode_monthly AS SELECT * FROM df_pin_monthly")

# Home Page (New Calendar Tables)
con.execute("CREATE OR REPLACE TABLE national_daily AS SELECT * FROM df_national_daily")
con.execute("CREATE OR REPLACE TABLE state_daily AS SELECT * FROM df_state_daily")

# Page 2
con.execute("CREATE OR REPLACE TABLE risk_state AS SELECT * FROM state_risk")
con.execute("CREATE OR REPLACE TABLE risk_district AS SELECT * FROM dist_risk")
con.execute("CREATE OR REPLACE TABLE risk_pincode AS SELECT * FROM pin_risk")

# Page 3
con.execute("CREATE OR REPLACE TABLE state_summary AS SELECT * FROM df_state_summary")
con.execute("CREATE OR REPLACE TABLE district_summary AS SELECT * FROM df_dist_summary")
con.execute("CREATE OR REPLACE TABLE pincode_summary AS SELECT * FROM df_pin_summary")

con.close()
print("✅ ETL Complete. Calendar Tables Added.")