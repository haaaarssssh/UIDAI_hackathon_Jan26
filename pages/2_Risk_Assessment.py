# # pages/2_Risk_Assessment.py

# import streamlit as st
# import pandas as pd
# import duckdb
# import plotly.express as px

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Risk Assessment", page_icon="🎯", layout="wide")

# SOLID_COLORS = {'red': '#D32F2F', 'blue': '#1976D2', 'green': '#388E3C', 'yellow': '#FBC02D'}
# COLOR_MAP = {'--void-purple': '#0F001A', '--toxic-cyan': '#00FFFF', '--chrome-grey': '#B0B0B0'}
# css = f"""
# <style>
#     .stApp {{ background-color: {COLOR_MAP['--void-purple']}; }}
#     h1, h2, h3, h4 {{ color: {COLOR_MAP['--toxic-cyan']}; }}
#     p, label, .stMarkdown {{ color: {COLOR_MAP['--chrome-grey']}; }}
# </style>
# """
# st.markdown(css, unsafe_allow_html=True)

# # --- DATA LOADING (OPTIMIZED) ---
# @st.cache_data
# def load_risk_data():
#     con = duckdb.connect(database='database/analytics.db', read_only=True)
#     # Fetch pre-calculated Z-Scores and Colors
#     df_pincode = con.execute("SELECT state, district, total_adult_enrolments, migration_index, z_score, risk_color FROM district_summary").fetchdf()
#     # Fetch pre-calculated Forecasts
#     df_forecasts = con.execute("SELECT * FROM state_forecasts").fetchdf()
#     con.close()
    
#     if not df_forecasts.empty:
#         df_forecasts['month'] = pd.to_datetime(df_forecasts['month'])
        
#     return df_pincode, df_forecasts

# df_pincode, df_forecasts = load_risk_data()

# # --- PAGE LAYOUT ---
# st.title("🎯 Risk Assessment")
# st.markdown("Proactively identifying integrity risks and future operational bottlenecks.")

# # --- Q4: THE ROGUE PROTOCOL ---
# st.header("1. The Rogue Center Identifier")
# st.markdown("_Question: Which districts are exhibiting statistically improbable levels of new adult enrolments?_")

# if not df_pincode.empty:
#     states_with_anomalies = sorted(df_pincode[df_pincode['risk_color'] == 'Anomaly']['state'].unique())
    
#     if not states_with_anomalies:
#         st.success("No significant anomalies (Z-Score > 2) found in the dataset.")
#         selected_state = df_pincode['state'].unique()[0] # Fallback
#     else:
#         selected_state = st.selectbox("Select a State to Investigate:", states_with_anomalies, index=0)

#     state_df = df_pincode[df_pincode['state'] == selected_state]

#     st.subheader(f"Distribution of Adult Enrolments in {selected_state}")
#     fig = px.strip(
#         state_df, x='total_adult_enrolments', y='district', orientation='h', color='risk_color',
#         stripmode='overlay', title=f"Identifying Outliers in {selected_state}",
#         color_discrete_map={'Normal': SOLID_COLORS['blue'], 'Anomaly': SOLID_COLORS['red']}
#     )
#     fig.update_layout(height=600, paper_bgcolor=COLOR_MAP['--void-purple'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['--chrome-grey'])
#     st.plotly_chart(fig, use_container_width=True)
    
#     anomalies_in_state = state_df[state_df['risk_color'] == 'Anomaly'].sort_values('z_score', ascending=False)
#     if not anomalies_in_state.empty:
#         st.subheader(f"🚩 Top Risk Districts in {selected_state}")
#         for index, row in anomalies_in_state.head(5).iterrows():
#             st.metric(label=f"{row['district']}", value=f"{row['total_adult_enrolments']} Enrolments", delta=f"Risk Score: {row['z_score']:.2f}", delta_color="inverse")
# else:
#     st.warning("Adult enrolment data not available.")
    
# st.markdown("---")

# # --- Q5: THE CAPACITY CLIFF ---
# st.header("2. The Capacity Cliff Projection")
# st.markdown("_Question: Which states are trending towards an operational overload in the next 3 months?_")

# if not df_forecasts.empty:
#     states = sorted(df_forecasts['state'].unique())
#     selected_state = st.selectbox("Select a State to Forecast:", states, index=0)

#     df_plot = df_forecasts[df_forecasts['state'] == selected_state].copy()
#     df_plot['month_display'] = df_plot['month'].dt.strftime('%b %Y')
    
#     # Simple Plotting (No Holt Model Logic Here - It's Done in ETL)
#     fig_forecast = px.bar(
#         df_plot[df_plot['type'] == 'Historical'], 
#         x='month_display', y='value', 
#         title=f"3-Month Workload Projection for {selected_state}",
#         color_discrete_sequence=[SOLID_COLORS['blue']]
#     )
#     fig_forecast.update_traces(name='Historical', showlegend=True)
    
#     forecast_data = df_plot[df_plot['type'] == 'Forecast']
#     fig_forecast.add_bar(x=forecast_data['month_display'], y=forecast_data['value'], name='Forecast', marker_color=SOLID_COLORS['yellow'])
    
#     peak_cap = df_plot[df_plot['type'] == 'Historical']['value'].max()
#     fig_forecast.add_hline(y=peak_cap, line_dash="dot", line_color=SOLID_COLORS['red'], annotation_text="Peak Capacity")
    
#     # Ensure all months are shown on X-axis (Fix for gaps)
#     all_months = df_plot['month_display'].tolist()
#     fig_forecast.update_xaxes(categoryorder='array', categoryarray=all_months)

#     fig_forecast.update_layout(paper_bgcolor=COLOR_MAP['--void-purple'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['--chrome-grey'])
#     st.plotly_chart(fig_forecast, use_container_width=True)
# else:
#     st.warning("Forecast data not available.")

# st.markdown("---")

# # --- Q6: THE MIGRATION INDEX ---
# st.header("3. The Migration Index")
# st.markdown("_Question: Which districts behave like 'Transit Hubs' with high population churn?_")

# if not df_pincode.empty:
#     df_to_plot = df_pincode.sort_values('migration_index', ascending=False).head(20)
#     fig_migration = px.bar(
#         df_to_plot, x='migration_index', y='district', orientation='h', title="Top 20 Districts by Population Churn",
#         color='migration_index', color_continuous_scale=[SOLID_COLORS['blue'], SOLID_COLORS['red']]
#     )
#     fig_migration.update_layout(height=600, paper_bgcolor=COLOR_MAP['--void-purple'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['--chrome-grey'], yaxis={'categoryorder':'total ascending'})
#     st.plotly_chart(fig_migration, use_container_width=True)



# import streamlit as st
# import pandas as pd
# import duckdb
# import plotly.express as px
# import numpy as np

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Risk Assessment", page_icon="🎯", layout="wide")

# # --- COLORS ---
# COLOR_MAP = {
#     'bg': '#0F001A', 
#     'cyan': '#00FFFF', 
#     'pink': '#FF00AA', 
#     'gold': '#FFD700', 
#     'grey': '#B0B0B0', 
#     'red': '#FF4B4B',
#     'blue': '#1976D2',
# }

# css = f"""
# <style>
#     .stApp {{ background-color: {COLOR_MAP['bg']}; }}
#     h1, h2, h3, div, label {{ color: {COLOR_MAP['cyan']}; }}
#     p, .stMarkdown, .st-emotion-cache-16idsys p {{ color: {COLOR_MAP['grey']}; }}
#     div[data-testid="stMetricValue"] {{ color: {COLOR_MAP['red']} !important; }}
# </style>
# """
# st.markdown(css, unsafe_allow_html=True)

# # --- LOAD PRE-CALCULATED RISK TABLES ---
# @st.cache_data
# def load_risk_data():
#     try:
#         con = duckdb.connect('database/analytics.db', read_only=True)
#         df_risk_state = con.execute("SELECT * FROM risk_state").fetchdf()
#         df_risk_dist = con.execute("SELECT * FROM risk_district").fetchdf()
#         df_risk_pin = con.execute("SELECT * FROM risk_pincode").fetchdf() # NEW
#         df_daily = con.execute("SELECT * FROM district_daily").fetchdf()
#         con.close()
        
#         # Normalize
#         if not df_risk_dist.empty: df_risk_dist['district'] = df_risk_dist['district'].str.title()
#         if not df_risk_pin.empty: 
#             df_risk_pin['district'] = df_risk_pin['district'].str.title()
#             df_risk_pin['pincode'] = df_risk_pin['pincode'].astype(str)
            
#         return df_risk_state, df_risk_dist, df_risk_pin, df_daily
#     except Exception as e:
#         st.error(f"Data Error: {e}")
#         return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# df_risk_state, df_risk_dist, df_risk_pin, df_daily = load_risk_data()

# st.title("🎯 Risk Assessment")

# # ==========================================
# # 1. CONTROLS (HIERARCHY)
# # ==========================================
# with st.container():
#     c1, c2, c3 = st.columns([1, 1, 1])
#     with c1:
#         view_level = st.radio("Analysis Level:", ["National", "State", "District"], horizontal=True)
    
#     active_df = pd.DataFrame()
#     daily_subset = pd.DataFrame()
#     entity_col = ""
#     selected_state = None
#     selected_dist = None
    
#     if view_level == "National":
#         active_df = df_risk_state.copy()
#         daily_subset = df_daily.copy()
#         entity_col = 'state'
        
#     elif view_level == "State":
#         state_list = sorted(df_risk_dist['state'].unique())
#         with c2: selected_state = st.selectbox("Select State:", state_list)
        
#         active_df = df_risk_dist[df_risk_dist['state'] == selected_state].copy()
#         daily_subset = df_daily[df_daily['state'] == selected_state].copy()
#         entity_col = 'district'
        
#     elif view_level == "District":
#         state_list = sorted(df_risk_dist['state'].unique())
#         with c2: selected_state = st.selectbox("Select State:", state_list)
        
#         dist_list = sorted(df_risk_dist[df_risk_dist['state'] == selected_state]['district'].unique())
#         with c3: selected_dist = st.selectbox("Select District:", dist_list)
        
#         # KEY CHANGE: Load Pincode Risk Table
#         active_df = df_risk_pin[(df_risk_pin['state'] == selected_state) & (df_risk_pin['district'] == selected_dist)].copy()
#         daily_subset = df_daily[(df_daily['state'] == selected_state) & (df_daily['district'] == selected_dist)].copy()
#         entity_col = 'pincode'

# # ==========================================
# # Q1: GHOST EXCLUSION HUNTER
# # ==========================================
# st.markdown("---")
# st.header("1. The 'Ghost' Exclusion Hunter")

# if not active_df.empty:
#     c1, c2 = st.columns([3, 1])
    
#     with c1:
#         color_map = {"Ghost Risk": COLOR_MAP['red'], "High Growth": COLOR_MAP['cyan'], "Normal": COLOR_MAP['grey']}
        
#         # Dynamic Title
#         context = selected_dist if selected_dist else (selected_state if selected_state else "All India")
        
#         fig = px.scatter(
#             active_df, 
#             x="total_transactions", 
#             y="total_enrol", 
#             color="Status",
#             size="total_transactions",
#             hover_name=entity_col,
#             color_discrete_map=color_map,
#             labels={'total_transactions': 'Total Volume', 'total_enrol': 'New Enrolments'},
#             title=f"Expected vs Actual Enrolment ({context})"
#         )
        
#         # Regression Line (Only if > 1 point)
#         if len(active_df) > 1 and 'predicted_enrol' in active_df.columns:
#             line_data = active_df.sort_values('total_transactions')
#             fig.add_traces(px.line(line_data, x='total_transactions', y='predicted_enrol').data[0])
#             fig.data[-1].line.color = COLOR_MAP['gold']
#             fig.data[-1].line.dash = 'dot'
#             fig.data[-1].name = 'Fair Target'

#         fig.update_layout(height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'])
#         st.plotly_chart(fig, use_container_width=True)

#     with c2:
#         # Metrics
#         ghosts = active_df[active_df['Status'] == "Ghost Risk"].sort_values('z_score', ascending=True).head(3)
#         st.subheader("⚠️ Risk Alert")
#         if not ghosts.empty:
#             for _, row in ghosts.iterrows():
#                 # Format name nicely
#                 name = str(row[entity_col])
#                 if entity_col == 'pincode': name = f"PIN: {name}"
                
#                 st.metric(
#                     label=name,
#                     value=f"{int(row['total_enrol']):,}",
#                     delta=f"-{int(abs(row['residual']))} Missing Enrolments",
#                     delta_color="inverse"
#                 )
#         else:
#             st.success(f"No critical risks in {context}.")

# with st.expander("ℹ️ How to read Ghost Hunter"):
#     st.markdown("""
#     *   **The Concept:** Identifying areas that process high volumes (Updates) but fail to enroll new citizens (Children).
#     *   **Granularity:** 
#         *   **National:** Compares States.
#         *   **State:** Compares Districts.
#         *   **District:** Compares Pincodes (Villages/Centers).
#     *   **<span style='color:#FF4B4B'>Red Dots (Ghost Risk):</span>** Entities falling statistically below the 'Fair Target' line.
#     """, unsafe_allow_html=True)

# # ==========================================
# # Q2: CAPACITY CLIFF (MONTHLY)
# # ==========================================
# st.markdown("---")
# st.header("2. Capacity Stress Test (Monthly)")

# if not daily_subset.empty:
#     daily_subset['date'] = pd.to_datetime(daily_subset['date'])
#     daily_subset['Month'] = daily_subset['date'].dt.strftime('%Y-%m')
    
#     monthly_ts = daily_subset.groupby('Month')['total_transactions'].sum().reset_index()
    
#     if not monthly_ts.empty:
#         # Threshold: 95th Percentile
#         capacity_limit = monthly_ts['total_transactions'].quantile(0.95)
        
#         fig_cap = px.bar(
#             monthly_ts, 
#             x='Month', 
#             y='total_transactions', 
#             labels={'total_transactions': 'Monthly Volume'},
#             color_discrete_sequence=[COLOR_MAP['cyan']]
#         )
        
#         fig_cap.add_hline(y=capacity_limit, line_dash="dash", line_color=COLOR_MAP['red'], annotation_text="Stress Limit (95th %)")
#         fig_cap.update_layout(height=450, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'])
#         st.plotly_chart(fig_cap, use_container_width=True)

# with st.expander("ℹ️ How to read Capacity Stress"):
#     st.markdown("""
#     *   **Red Line:** Historical Peak Capacity (95th Percentile).
#     *   **Insight:** If bars consistently cross the red line, the infrastructure in this specific area (State/District/Pincode) is structurally overloaded.
#     """, unsafe_allow_html=True)

# # ==========================================
# # Q3: MIGRATION INDEX
# # ==========================================
# st.markdown("---")
# st.header("3. Migration & Churn Index")

# if not active_df.empty:
#     data_to_plot = active_df.sort_values('migration_index', ascending=False)
#     if len(data_to_plot) > 15: data_to_plot = data_to_plot.head(15)
        
#     fig_mig = px.bar(
#         data_to_plot, 
#         x='migration_index', 
#         y=entity_col, 
#         orientation='h',
#         color='migration_index', 
#         color_continuous_scale=[COLOR_MAP['blue'], COLOR_MAP['pink']],
#         labels={'migration_index': 'Demographic Update %', entity_col: entity_col.title()},
#         text='migration_index'
#     )
    
#     fig_mig.update_layout(
#         height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', 
#         font_color=COLOR_MAP['grey'], yaxis=dict(categoryorder='total ascending', type='category'), # 'type':'category' fixes pincode strings
#         coloraxis_showscale=False
#     )
#     fig_mig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
#     st.plotly_chart(fig_mig, use_container_width=True)

# with st.expander("ℹ️ How to read Migration Index"):
#     st.markdown("**Metric:** % of transactions that are Demographic Updates. High % = Transient Population.", unsafe_allow_html=True)

# import streamlit as st
# import pandas as pd
# import duckdb
# import plotly.express as px
# from sklearn.linear_model import LinearRegression
# from scipy.stats import zscore

# st.set_page_config(page_title="Risk Assessment", page_icon="🎯", layout="wide")

# # --- 🎨 DESIGN PIVOT: NEON NOIR ---
# COLOR_MAP = {
#     'bg': '#000000', 'cyan': '#00E5FF', 'pink': '#FF00FF', 
#     'gold': '#CCFF00', # Lime Green
#     'grey': '#888888', 'red': '#FF2A2A', # Bright Red for Risk
#     'blue': '#2962FF'
# }

# font_css = """
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
# .stApp { background-color: #000000; }
# html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

# h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; }
# p, .stMarkdown { color: #A0A0A0; }
# div[data-testid="stMetricValue"] { color: #FF2A2A !important; text-shadow: 0 0 10px rgba(255, 42, 42, 0.4); }

# /* Sidebar */
# section[data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #222; }
# </style>
# """
# st.markdown(font_css, unsafe_allow_html=True)
# # ----------------------------------------

# @st.cache_data
# def load_data():
#     try:
#         con = duckdb.connect('database/analytics.db', read_only=True)
#         s = con.execute("SELECT * FROM risk_state").fetchdf()
#         d = con.execute("SELECT * FROM risk_district").fetchdf()
#         p = con.execute("SELECT * FROM risk_pincode").fetchdf()
#         daily = con.execute("SELECT * FROM district_daily").fetchdf()
#         con.close()
        
#         # Data Cleaning
#         if not d.empty: d['district'] = d['district'].str.title()
#         if not p.empty: 
#             p['district'] = p['district'].str.title()
#             p['pincode'] = p['pincode'].astype(str).str.replace('.0', '', regex=False)
            
#         return s, d, p, daily
#     except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# df_s, df_d, df_p, df_daily = load_data()

# # --- SIDEBAR View Controller  (FIXED) ---
# with st.sidebar:
#     st.header("🔭 View Controller ")
#     view_level = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (District)"])
    
#     selected_state, selected_dist = None, None
    
#     if view_level in ["Mosaic (State)", "Tessera (District)"]:
#         state_list = sorted(df_d['state'].unique())
#         selected_state = st.selectbox("Select State:", state_list)
        
#     if view_level == "Tessera (District)":
#         dist_list = sorted(df_d[df_d['state']==selected_state]['district'].unique())
#         selected_dist = st.selectbox("Select District:", dist_list)

#     # Footer
#     st.markdown("---")
#     st.markdown(
#         f"""
#         <div style='text-align: center; margin-top: 20px; font-family: "Outfit", sans-serif;'>
#             <span style='color: #666; font-size: 14px; font-weight: 600;'>UIDAI_23</span>
#             <span style='color: #333; margin: 0 8px;'>|</span>
#             <span style='color: #00E5FF; font-size: 14px; letter-spacing: 1px;'>DATA PALETTE</span>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# # --- DATA FILTERING ---
# active_df, daily_sub, col = pd.DataFrame(), pd.DataFrame(), ""

# if view_level == "Adamento (National)":
#     active_df, daily_sub, col = df_s.copy(), df_daily.copy(), 'state'
# elif view_level == "Mosaic (State)" and selected_state:
#     active_df = df_d[df_d['state']==selected_state].copy()
#     daily_sub = df_daily[df_daily['state']==selected_state].copy()
#     col = 'district'
# elif view_level == "Tessera (District)" and selected_dist:
#     active_df = df_p[(df_p['state']==selected_state) & (df_p['district']==selected_dist)].copy()
#     daily_sub = df_daily[(df_daily['state']==selected_state) & (df_daily['district']==selected_dist)].copy()
#     col = 'pincode'
#     # Ensure string format for active selection
#     if not active_df.empty: active_df['pincode'] = active_df['pincode'].astype(str)

# st.title("Risk Assessment")

# # --- Q1 GHOST ---
# st.header("1. The 'Ghost' Exclusion Hunter")
# st.markdown("We are catching centers that process thousands of adults but suspiciously turn away every single child.")
# if not active_df.empty:
#     c1, c2 = st.columns([3, 1])
#     with c1:
#         color_map = {"Ghost Risk": COLOR_MAP['red'], "High Growth": COLOR_MAP['cyan'], "Normal": COLOR_MAP['grey']}
#         fig = px.scatter(active_df, x="total_transactions", y="total_enrol", color="Status", size="total_transactions", hover_name=col, color_discrete_map=color_map, title=f"Expected vs Actual ({view_level})")
        
#         if len(active_df) > 1 and 'predicted_enrol' in active_df.columns:
#             line_data = active_df.sort_values('total_transactions')
#             fig.add_traces(px.line(line_data, x='total_transactions', y='predicted_enrol').data[0])
#             fig.data[-1].line.color = COLOR_MAP['gold']; fig.data[-1].line.dash = 'dot'; fig.data[-1].name = 'Fair Target'
        
#         fig.update_layout(height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'],xaxis_title='Total Volume', yaxis_title='New Enrolments')
#         st.plotly_chart(fig, use_container_width=True)

#     with c2:
#         ghosts = active_df[active_df['Status'] == "Ghost Risk"].sort_values('z_score').head(3)
#         st.subheader("Risk Alert ❗")
#         if not ghosts.empty:
#             for _, r in ghosts.iterrows():
#                 val = str(r[col]) if col!='pincode' else f"PIN: {r[col]}"
#                 st.metric(label=val, value=f"{int(r['total_enrol']):,}", delta=f"-{int(abs(r['residual']))} Missing", delta_color="inverse")
#         else: st.success("No anomalies.")

# with st.expander("ℹ️ How to read this Scatter Plot: The Ghost Hunter"):
#     st.markdown("""
#     **Why are we asking this?** To detect centers that are busy making money on updates but failing to enroll children (Exclusion Risk).
    
#     **The Technique: Linear Regression (The 'Fair' Line)**
#     We calculate a mathematical trend line. If a district does $X$ amount of total work, it *should* reasonably do $Y$ amount of child enrolments.
    
#     **Interpretation:**
#     *   **Yellow Line:** The "Fair Target." Where the district should be statistically.
#     *   **<span style='color:#FF4B4B'>Red Dot (Ghost Risk):</span>** Significantly below the line. These centers are busy but have near-zero child enrolment. **High Risk.**
#     *   **<span style='color:#00FFFF'>Cyan Dot (High Growth):</span>** Above the line. Enrolling more children than expected. Good performance.
#     """, unsafe_allow_html=True)

# # --- Q2 CAPACITY ---
# st.markdown("---"); st.header("2. Capacity Stress Test (Monthly)")
# st.markdown("Are we approaching the operational limits of our infrastructure?")
# if not daily_sub.empty:
#     daily_sub['date'] = pd.to_datetime(daily_sub['date']); daily_sub['M'] = daily_sub['date'].dt.strftime('%Y-%m')
#     m_ts = daily_sub.groupby('M')['total_transactions'].sum().reset_index()
#     if not m_ts.empty:
#         limit = m_ts['total_transactions'].quantile(0.95)
#         fig = px.bar(m_ts, x='M', y='total_transactions', color_discrete_sequence=[COLOR_MAP['cyan']])
#         fig.add_hline(y=limit, line_dash="dash", line_color=COLOR_MAP['red'], annotation_text="Strain Limit")
#         fig.update_layout(height=450, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'],xaxis_title='Month', yaxis_title='Monthly Volume')
#         st.plotly_chart(fig, use_container_width=True)

# with st.expander("ℹ️ How to read this Chart: Capacity Stress Test"):
#     st.markdown("""
#     **Why are we asking this?** To predict infrastructure failure before servers crash or staff burn out.
    
#     **The Technique: Quantile Benchmarking**
#     We look at the 95th Percentile of historical volume. This establishes a "Safety Limit" based on past data.
    
#     **Interpretation:**
#     *   **Red Dashed Line:** The "Breaking Point."
#     *   **Bars Crossing Line:** The infrastructure is **Overheated**. Staff are overworked. Immediate capacity augmentation (more machines/staff) is required.
#     """, unsafe_allow_html=True)

# # --- Q3 MIGRATION ---
# st.markdown("---"); st.header("3. Migration & Churn Index")
# st.markdown("Identifying 'Transit Hubs' with high population churn.")    
# if not active_df.empty:
#     churn = active_df.sort_values('migration_index', ascending=False).head(15)
    
#     # Y-Axis Categorical Fix
#     fig = px.bar(
#         churn, x='migration_index', y=col, orientation='h', 
#         color='migration_index', color_continuous_scale=[COLOR_MAP['blue'], COLOR_MAP['pink']],
#         text='migration_index'
#     )
    
#     fig.update_layout(
#         height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', 
#         font_color=COLOR_MAP['grey'], 
#         yaxis=dict(categoryorder='total ascending', type='category'), # Forces String Labels
#         coloraxis_showscale=False,
#         xaxis_title='Demographic Update %', yaxis_title=col.title()
#     )
#     fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
#     st.plotly_chart(fig, use_container_width=True)

# with st.expander("ℹ️ How to read this Gauge: Migration & Churn"):
#     st.markdown("""
#     **Why are we asking this?** To identify transient populations (students, migrant labor) vs. stable families.
    
#     **The Technique: Ratio Analysis**
#     We calculate the ratio of Demographic Updates vs. Total Transactions.
    
#     **Interpretation:**
#     *   **High Value (>70% - <span style='color:#FF00AA'>Pink</span>):** This area is a "Transit Hub." People move frequently.
#     *   **Strategy:** Do not deploy permanent enrolment centers here. Deploy **Update Kiosks** instead.
#     """, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
from sklearn.linear_model import LinearRegression
from scipy.stats import zscore

st.set_page_config(page_title="Risk Assessment", page_icon="🎯", layout="wide")

# --- 🎨 THEME: TRICOLOR INTELLIGENCE (Dark Mode) ---
COLOR_MAP = {
    'bg': '#050505',           # Deepest Black-Blue
    'card': '#111111',         # Card Background
    'cyan': '#2979FF',         # Electric Blue (Technology/Standard)
    'pink': '#FF9100',         # Neon Saffron (High Variance/Alerts)
    'gold': '#00E676',         # Signal Green (Safe/Target)
    'red': '#FF3D00',          # High Contrast Red (Risk/Anomaly)
    'grey': '#9E9E9E',         # Muted Text
    'blue': '#2979FF'          # Alias for Cyan
}

font_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
.stApp { background-color: #050505; }

/* Global Typography */
html, body, [class*="css"], h1, h2, h3, h4, .stMarkdown, .stMetricLabel {
    font-family: 'Outfit', sans-serif !important;
}

h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; letter-spacing: -0.5px; }
p, .stMarkdown { color: #9E9E9E !important; }

/* Metric Values - Red for Risk Emphasis */
div[data-testid="stMetricValue"] { 
    color: #FF3D00 !important; 
    text-shadow: 0 0 15px rgba(255, 61, 0, 0.3);
    font-weight: 600; 
}

/* --- FORCE DARK SIDEBAR --- */
section[data-testid="stSidebar"] {
    background-color: #050505 !important;
    border-right: 1px solid #222 !important;
}
div[data-testid="stSidebarNav"] {
    background-color: #050505 !important;
}

/* Sidebar Inputs */
.stSelectbox div[data-baseweb="select"] > div { background-color: #111 !important; color: white !important; border-color: #333 !important; }
.stSelectbox div[data-baseweb="select"] > div:hover { border-color: #2979FF !important; }
</style>
"""
st.markdown(font_css, unsafe_allow_html=True)
# ----------------------------------------

@st.cache_data
def load_data():
    try:
        con = duckdb.connect('database/analytics.db', read_only=True)
        s = con.execute("SELECT * FROM risk_state").fetchdf()
        d = con.execute("SELECT * FROM risk_district").fetchdf()
        p = con.execute("SELECT * FROM risk_pincode").fetchdf()
        daily = con.execute("SELECT * FROM district_daily").fetchdf()
        con.close()
        
        # Data Cleaning
        if not d.empty: d['district'] = d['district'].str.title()
        if not p.empty: 
            p['district'] = p['district'].str.title()
            p['pincode'] = p['pincode'].astype(str).str.replace('.0', '', regex=False)
            
        return s, d, p, daily
    except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_state, df_dist, df_pin, df_daily = load_data()

# --- SIDEBAR View Controller ---
with st.sidebar:
    st.header("🔭 View Controller")
    # Note the options here: Pincode is the last one
    view_level = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (District)"])
    
    selected_state, selected_dist = None, None
    
    # FIX: Check for "Tessera (District)", not "Tessera (District)"
    if view_level in ["Mosaic (State)", "Tessera (District)"]:
        states = sorted(df_dist['state'].unique())
        
        # Default to Maharashtra
        st_ix = states.index('Maharashtra') if 'Maharashtra' in states else 0
        selected_state = st.selectbox("Select State:", states, index=st_ix)
        
    # FIX: Check for "Tessera (District)"
    if view_level == "Tessera (District)":
        # Filter districts belonging to the selected state
        dists = sorted(df_dist[df_dist['state'] == selected_state]['district'].unique())
        
        # Default to Jalgaon
        dt_ix = dists.index('Jalgaon') if 'Jalgaon' in dists else 0
        selected_dist = st.selectbox("Select District:", dists, index=dt_ix)

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; margin-top: 20px; font-family: "Outfit", sans-serif;'>
            <span style='color: #666; font-size: 14px; font-weight: 600;'>UIDAI_23</span>
            <span style='color: #333; margin: 0 8px;'>|</span>
            <span style='color: {COLOR_MAP['cyan']}; font-size: 14px; letter-spacing: 1px;'>DATA PALETTE</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- DATA FILTERING ---
active_df, daily_sub, col = pd.DataFrame(), pd.DataFrame(), ""

if view_level == "Adamento (National)":
    active_df, daily_sub, col = df_state.copy(), df_daily.copy(), 'state'
elif view_level == "Mosaic (State)" and selected_state:
    active_df = df_dist[df_dist['state']==selected_state].copy()
    daily_sub = df_daily[df_daily['state']==selected_state].copy()
    col = 'district'
elif view_level == "Tessera (District)" and selected_dist:
    active_df = df_pin[(df_pin['state']==selected_state) & (df_pin['district']==selected_dist)].copy()
    daily_sub = df_daily[(df_daily['state']==selected_state) & (df_daily['district']==selected_dist)].copy()
    col = 'pincode'
    if not active_df.empty: active_df['pincode'] = active_df['pincode'].astype(str)

st.title("Risk Assessment Engine")

# ----------------------------------------
# Q1: GHOST HUNTER
# ----------------------------------------
st.header("1. The 'Ghost' Exclusion Hunter")
st.markdown("We are catching centers that process thousands of adults for profit but suspiciously turn away every single child.")
st.caption("We use Linear Regression to flag exclusion anomalies where actual enrolment deviates significantly from the statistical expectation.")

if not active_df.empty:
    c1, c2 = st.columns([3, 1])
    with c1:
        # Colors: Red (Risk), Blue (Growth), Grey (Normal)
        color_map = {"Ghost Risk": COLOR_MAP['red'], "High Growth": COLOR_MAP['cyan'], "Normal": COLOR_MAP['grey']}
        
        fig = px.scatter(
            active_df, x="total_transactions", y="total_enrol", 
            color="Status", size="total_transactions", 
            hover_name=col, color_discrete_map=color_map, 
            title=f"Regression Analysis: Expected vs Actual ({view_level})"
        )
        
        # Add the "Fair Line"
        if len(active_df) > 1 and 'predicted_enrol' in active_df.columns:
            line_data = active_df.sort_values('total_transactions')
            fig.add_traces(px.line(line_data, x='total_transactions', y='predicted_enrol').data[0])
            fig.data[-1].line.color = COLOR_MAP['gold'] # Green Line
            fig.data[-1].line.dash = 'dot'
            fig.data[-1].name = 'Fair Target'
        
        fig.update_layout(height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'], xaxis_title='Total Volume', yaxis_title='New Enrolments')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        ghosts = active_df[active_df['Status'] == "Ghost Risk"].sort_values('z_score').head(3)
        st.subheader("Anomaly Detected ⚠️")
        if not ghosts.empty:
            for _, r in ghosts.iterrows():
                val = str(r[col]) if col!='pincode' else f"PIN: {r[col]}"
                # Metric shows the gap
                st.metric(label=val, value=f"{int(r['total_enrol']):,}", delta=f"-{int(abs(r['residual']))} Missing Gap", delta_color="inverse")
        else: st.info("No significant statistical anomalies detected.")

with st.expander("ℹ️ How to interpret the Ghost Hunter"):
    st.markdown(f"""
    **The Insight:**
    This model detects **Exclusion Risk**. If a center is busy (High X-axis) but enrolling zero children (Low Y-axis), it indicates a refusal of service to difficult demographics.
    
    **The Technique: Linear Regression & Residual Analysis**
    We calculate a "Fair Trend Line" based on peer performance. The Z-Score tells us how far a specific unit is from this fair line.
    
    **Visual Guide:**
    *   **<span style='color:{COLOR_MAP['gold']}'>Green Dashed Line:</span>** The "Fair Target." Mathematically, where the district should be.
    *   **<span style='color:{COLOR_MAP['red']}'>Red Dot (Ghost Risk):</span>** Significantly below the line. Busy centers, but zero child enrolment. **High Risk.**
    *   **<span style='color:{COLOR_MAP['cyan']}'>Blue Dot (High Growth):</span>** Above the line. Enrolling more than expected.
    """, unsafe_allow_html=True)

# ----------------------------------------
# Q2: CAPACITY STRESS
# ----------------------------------------
st.markdown("---")
st.header("2. Capacity Stress Test")
st.markdown("We are predicting which centers are about to crash or burn out because they are working beyond their safety limits.")
st.caption("This module compares current monthly loads against the 95th Percentile historical benchmark.")

if not daily_sub.empty:
    daily_sub['date'] = pd.to_datetime(daily_sub['date']); daily_sub['M'] = daily_sub['date'].dt.strftime('%Y-%m')
    m_ts = daily_sub.groupby('M')['total_transactions'].sum().reset_index()
    if not m_ts.empty:
        limit = m_ts['total_transactions'].quantile(0.95)
        
        fig = px.bar(m_ts, x='M', y='total_transactions', color_discrete_sequence=[COLOR_MAP['cyan']])
        # Add Limit Line
        fig.add_hline(y=limit, line_dash="dash", line_color=COLOR_MAP['red'], annotation_text="Strain Limit (P95)")
        
        fig.update_layout(height=450, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'],xaxis_title='Timeline', yaxis_title='Monthly Volume')
        st.plotly_chart(fig, use_container_width=True)

with st.expander("ℹ️ How to interpret the Capacity Stress Test"):
    st.markdown(f"""
    **The Insight:**
    Predictive maintenance for human and digital infrastructure.
    
    **The Technique: Quantile Benchmarking**
    We set the "Breaking Point" at the 95th percentile of historical data. Consistent breaches indicate a need for immediate resource augmentation.
    
    **Visual Guide:**
    *   **<span style='color:{COLOR_MAP['red']}'>Red Dashed Line:</span>** The Safety Limit.
    *   **Bars Crossing Line:** The infrastructure is **Overheated**. Staff are overworked, and servers may crash.
    """, unsafe_allow_html=True)

# ----------------------------------------
# Q3: MIGRATION & CHURN
# ----------------------------------------
st.markdown("---")
st.header("3. Migration & Churn Index")
st.markdown("We are identifying areas where people move frequently (like students or laborers) so we don't waste money building permanent offices there.")
st.caption("High churn ratios indicate a transit hub requiring lightweight update kiosks rather than full enrolment kits.")

if not active_df.empty:
    churn = active_df.sort_values('migration_index', ascending=False).head(15)
    
    # Gradient: Blue (Low Churn) -> Saffron (High Churn)
    fig = px.bar(
        churn, x='migration_index', y=col, orientation='h', 
        color='migration_index', color_continuous_scale=[COLOR_MAP['cyan'], COLOR_MAP['pink']],
        text='migration_index'
    )
    
    fig.update_layout(
        height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', 
        font_color=COLOR_MAP['grey'], 
        yaxis=dict(categoryorder='total ascending', type='category'), 
        coloraxis_showscale=False,
        xaxis_title='Demographic Update Ratio (%)', yaxis_title=col.title()
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with st.expander("ℹ️ How to interpret the Churn Index"):
    st.markdown(f"""
    **The Insight:**
    Differentiation between **Stable Residential Zones** and **Transient Hubs**.
    
    **The Technique: Ratio Analysis**
    We calculate the ratio: `Demographic_Updates / Total_Transactions`.
    
    **Visual Guide:**
    *   **High Value (>70% - <span style='color:{COLOR_MAP['pink']}'>Neon Saffron</span>):** This area is a "Transit Hub."
    *   **Strategy:** Do not deploy permanent enrolment centers here. Deploy **Mobile Update Kiosks** to handle address changes efficiently.
    """, unsafe_allow_html=True)