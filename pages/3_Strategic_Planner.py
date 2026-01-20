# import streamlit as st
# import pandas as pd
# import duckdb
# import plotly.express as px
# import numpy as np
# # (LinearRegression import removed as it wasn't being used in this specific block, simplifying imports)

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Strategic Planner", page_icon="💡", layout="wide")

# # --- COLOR & STYLE ---
# MODERN_COLORS = {
#     'background': '#0F001A', 
#     'text': '#EAEAEA', 
#     'text_subtle': '#A0A0A0',
#     # Semantic Colors for the Quadrants
#     'hyper_growth': '#00FFFF',   # Cyan: High Energy / Max People
#     'last_mile': '#FF00AA',      # Magenta: Urgent / Inclusivity Focus
#     'digital_mature': '#FBC02D', # Yellow: Stable / Maintenance
#     'dormant': '#333333'         # Grey: Inactive
# }
# css = f"""
# <style>
#     .stApp {{ background-color: {MODERN_COLORS['background']}; }}
#     h1, h2, h3 {{ color: {MODERN_COLORS['hyper_growth']}; }}
#     p, label, .stMarkdown {{ color: {MODERN_COLORS['text_subtle']}; }}
# </style>
# """
# st.markdown(css, unsafe_allow_html=True)

# # --- DATA LOADING ---
# @st.cache_data
# def load_planner_data():
#     con = duckdb.connect(database='database/analytics.db', read_only=True)
#     df_summary = con.execute("SELECT * FROM district_summary").fetchdf()
#     df_daily = con.execute("SELECT date, district, total_transactions FROM district_daily").fetchdf()
#     con.close()

#     if not df_daily.empty:
#         df_daily['date'] = pd.to_datetime(df_daily['date'])
        
#     if df_summary.empty:
#         return pd.DataFrame(), df_daily

#     # --- AGGREGATION ---
#     # FIX: Changed 'total_bio_updates' -> 'total_bio' and 'total_demo_updates' -> 'total_demo'
#     # to match the ETL pipeline output.
#     district_agg = {
#         'total_child_enrolments': 'sum', 
#         'total_adult_enrolments': 'sum',
#         'total_bio': 'sum',   # Corrected Name
#         'total_demo': 'sum',  # Corrected Name
#         'total_transactions': 'sum', 
#         'state': 'first',
#         'enrolment_gap': 'first'
#     }
    
#     # Group by district in case the summary table has multiple rows per district (it shouldn't, but safe to do)
#     df_district = df_summary.groupby('district').agg(district_agg).reset_index()
    
#     # Calculate Demand Types
#     df_district['Enrolment_Demand'] = df_district['total_child_enrolments'] + df_district['total_adult_enrolments']
#     df_district['Update_Demand'] = df_district['total_bio'] + df_district['total_demo'] # Corrected Names
    
#     # --- THE PIVOT: LOGIC FOR "SERVICE DELIVERY MATRIX" ---
#     # We use Medians as the "Fair Benchmark"
#     med_enrol = df_district['Enrolment_Demand'].median()
#     med_update = df_district['Update_Demand'].median()
    
#     def assign_strategy(row):
#         is_high_enrol = row['Enrolment_Demand'] >= med_enrol
#         is_high_update = row['Update_Demand'] >= med_update
        
#         if is_high_enrol and is_high_update: 
#             return "Hyper-Growth Hubs" # Max People / Easy Wins
#         elif is_high_enrol and not is_high_update: 
#             return "The Last Mile"     # High Exclusion / Needs Camps
#         elif not is_high_enrol and is_high_update: 
#             return "Digital Mature"    # Needs Self-Service
#         else: 
#             return "Low Intensity"
            
#     df_district['Strategy_Quadrant'] = df_district.apply(assign_strategy, axis=1)
    
#     return df_district, df_daily

# df_planner, df_daily_planner = load_planner_data()


# # --- PAGE LAYOUT ---
# st.title("💡 Strategic Planner")
# st.markdown("Turning operational data into **social impact** and **resource efficiency**.")

# # --- Q7: THE SERVICE DELIVERY MATRIX (The Pivot) ---
# st.header("1. The Service Delivery Matrix")
# st.markdown("_Answering the question: **How do we cater to specific needs while maximizing reach?**_")

# if not df_planner.empty:
#     c1, c2, c3 = st.columns(3)
#     c1.metric("Total Districts Mapped", f"{len(df_planner)}")
#     c2.metric("Last Mile Districts (High Priority)", f"{len(df_planner[df_planner['Strategy_Quadrant']=='The Last Mile'])}")
#     c3.metric("Hyper-Growth Hubs (High Volume)", f"{len(df_planner[df_planner['Strategy_Quadrant']=='Hyper-Growth Hubs'])}")

#     # Color Map for Clarity
#     strategy_colors = {
#         "Hyper-Growth Hubs": MODERN_COLORS['hyper_growth'],
#         "The Last Mile": MODERN_COLORS['last_mile'],
#         "Digital Mature": MODERN_COLORS['digital_mature'],
#         "Low Intensity": MODERN_COLORS['dormant'],
#         '(?)': '#2a2a2a'
#     }

#     fig_treemap = px.treemap(
#         df_planner,
#         path=[px.Constant("All India"), 'Strategy_Quadrant', 'state', 'district'],
#         values='total_transactions', # Size = Max People
#         color='Strategy_Quadrant',   # Color = The Need
#         color_discrete_map=strategy_colors,
#         custom_data=['state', 'Enrolment_Demand', 'Update_Demand']
#     )
    
#     fig_treemap.update_traces(
#         marker=dict(line=dict(width=1, color=MODERN_COLORS['background'])), # Clean borders
#         root_color=MODERN_COLORS['background'],
#         textinfo="label+value",
#         hovertemplate="<b>%{label}</b><br>Total Vol: %{value}<br>New Enrolments: %{customdata[1]}<br>Updates: %{customdata[2]}<extra></extra>"
#     )
    
#     fig_treemap.update_layout(
#         height=700,
#         paper_bgcolor=MODERN_COLORS['background'],
#         font_color=MODERN_COLORS['text_subtle'],
#         margin = dict(t=20, l=10, r=10, b=10),
#     )
#     st.plotly_chart(fig_treemap, use_container_width=True)

#     with st.expander("ℹ️ How to interpret this Matrix (Government Rubric)"):
#         st.markdown(f"""
#         This matrix segments districts based on **what the citizens actually need**, ensuring we don't apply a "one size fits all" solution.
        
#         1.  <span style='color:{MODERN_COLORS['hyper_growth']}'>■</span> **Hyper-Growth Hubs:** High demand for EVERYTHING. 
#             *   *Strategy:* **Capacity Augmentation.** Deploy more machines and permanent staff. This captures the "Max People."
            
#         2.  <span style='color:{MODERN_COLORS['last_mile']}'>■</span> **The Last Mile (Inclusivity):** High demand for **New Enrolments** (Children/Unreached), low updates.
#             *   *Strategy:* **Mobile Camps.** These citizens are likely remote or excluded. We must go to them.
            
#         3.  <span style='color:{MODERN_COLORS['digital_mature']}'>■</span> **Digital Mature:** High demand for **Updates**, low new enrolments.
#             *   *Strategy:* **Self-Service / Online.** The population is already enrolled; they just need maintenance.
#         """, unsafe_allow_html=True)
# else:
#     st.warning("Strategic data not available.")

# st.markdown("---")

# # --- Q8: THE 'INVISIBLE CHILD' INITIATIVE ---
# st.header("2. The 'Invisible Child' Initiative")
# st.markdown("_Identifying districts where child enrolment is statistically lower than expected (Potential Exclusion)._")

# if not df_planner.empty:
#     # Aggregation toggle
#     analysis_level = st.radio("View Level:", ("State Level", "District Level"), horizontal=True)

#     if analysis_level == "State Level":
#         df_plot = df_planner.groupby('state')['enrolment_gap'].sum().reset_index().sort_values('enrolment_gap', ascending=False)
#         y_col = 'state'
#     else:
#         df_plot = df_planner.sort_values('enrolment_gap', ascending=False).head(20)
#         y_col = 'district'

#     fig_gap = px.bar(
#         df_plot.sort_values('enrolment_gap', ascending=True),
#         x='enrolment_gap', y=y_col, orientation='h', 
#         title=f"Largest Enrolment Gaps ({analysis_level})",
#         labels={'enrolment_gap': 'Missing Enrolments (Estimated)', y_col: y_col.title()},
#         color='enrolment_gap', color_continuous_scale=['#222', MODERN_COLORS['last_mile']]
#     )
#     fig_gap.update_layout(height=600, paper_bgcolor=MODERN_COLORS['background'], plot_bgcolor='rgba(0,0,0,0)', font_color=MODERN_COLORS['text_subtle'])
#     st.plotly_chart(fig_gap, use_container_width=True)
# else:
#     st.warning("Gap analysis data not available.")

# st.markdown("---")

# # --- Q9: THE 'SMART GOAL' SETTER ---
# st.header("3. The 'Smart Goal' Setter")
# st.markdown("_Setting realistic targets based on district-specific volatility._")

# if not df_daily_planner.empty:
#     districts = sorted(df_planner['district'].unique())
#     # Default to a "Last Mile" district if possible to show impact
#     last_mile_dists = df_planner[df_planner['Strategy_Quadrant'] == 'The Last Mile']['district'].unique()
#     def_dist = last_mile_dists[0] if len(last_mile_dists) > 0 else districts[0]
    
#     selected_district = st.selectbox("Select District:", districts, index=list(districts).index(def_dist) if def_dist in districts else 0)
    
#     district_daily_df = df_daily_planner[df_daily_planner['district'] == selected_district]['total_transactions']
    
#     if len(district_daily_df) > 5:
#         # Live Simulation (Lightweight)
#         n_sims = 1000
#         # Use sample without replacement if data is small, or with replacement
#         sims = [district_daily_df.sample(n=30, replace=True).sum() for _ in range(n_sims)]
#         p10, p50, p90 = np.percentile(sims, [10, 50, 90])
        
#         c1, c2, c3 = st.columns(3)
#         c1.metric("Conservative Target", f"{int(p10):,}", help="90% chance of hitting this")
#         c2.metric("Likely Outcome", f"{int(p50):,}", help="Median expectation")
#         c3.metric("Ambitious Target", f"{int(p90):,}", help="Top 10% performance scenario")
        
#         fig_dist = px.histogram(x=sims, nbins=30, title=f"Probabilistic Forecast: {selected_district}")
#         fig_dist.update_traces(marker_color=MODERN_COLORS['digital_mature'])
#         fig_dist.update_layout(
#             paper_bgcolor=MODERN_COLORS['background'], 
#             plot_bgcolor='rgba(0,0,0,0)', 
#             font_color=MODERN_COLORS['text_subtle'],
#             xaxis_title="Predicted Monthly Volume",
#             yaxis_title="Frequency of Outcome"
#         )
#         st.plotly_chart(fig_dist, use_container_width=True)
#     else:
#         st.warning("Insufficient data for simulation.")
# else:
#     st.warning("Daily data not available.")


# import streamlit as st
# import pandas as pd
# import duckdb
# import plotly.express as px
# import numpy as np

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Strategic Planner", page_icon="💡", layout="wide")

# MODERN_COLORS = {'background': '#0F001A', 'text': '#EAEAEA', 'text_subtle': '#A0A0A0', 'hyper_growth': '#00FFFF', 'last_mile': '#FF00AA', 'digital_mature': '#FBC02D', 'dormant': '#333333'}
# css = f"""<style>.stApp {{ background-color: {MODERN_COLORS['background']}; }} h1, h2, h3 {{ color: {MODERN_COLORS['hyper_growth']}; }} p, label, .stMarkdown, .stRadio label {{ color: {MODERN_COLORS['text_subtle']}; }} .stRadio [role=radiogroup] {{ flex-direction: row; gap: 20px; }}</style>"""
# st.markdown(css, unsafe_allow_html=True)

# # --- DATA LOADING ---
# @st.cache_data
# def load_planner_data():
#     try:
#         con = duckdb.connect(database='database/analytics.db', read_only=True)
#         # Load Pre-calculated Summaries
#         df_state = con.execute("SELECT * FROM state_summary").fetchdf()
#         df_dist = con.execute("SELECT * FROM district_summary").fetchdf()
#         df_pin = con.execute("SELECT * FROM pincode_summary").fetchdf()
        
#         # Load Daily for Simulation
#         df_daily = con.execute("SELECT date, state, district, total_transactions FROM district_daily").fetchdf()
#         df_pin_daily = con.execute("SELECT date, state, district, pincode, total_transactions FROM pincode_daily").fetchdf()
#         con.close()

#         if not df_daily.empty: df_daily['date'] = pd.to_datetime(df_daily['date'])
#         if not df_pin_daily.empty: df_pin_daily['date'] = pd.to_datetime(df_pin_daily['date'])
            
#         def process_quadrants(df):
#             if df.empty: return df
#             if 'total_child_enrolments' in df.columns:
#                 df['Enrolment_Demand'] = df['total_child_enrolments'] + df['total_adult_enrolments']
#                 df['Update_Demand'] = df['total_bio'] + df['total_demo']
#             med_enrol, med_update = df['Enrolment_Demand'].median(), df['Update_Demand'].median()
#             def assign(row):
#                 if row['Enrolment_Demand'] >= med_enrol and row['Update_Demand'] >= med_update: return "Hyper-Growth Hubs" 
#                 elif row['Enrolment_Demand'] >= med_enrol: return "The Last Mile"     
#                 elif row['Update_Demand'] >= med_update: return "Digital Mature"    
#                 else: return "Low Intensity"
#             df['Strategy_Quadrant'] = df.apply(assign, axis=1)
#             return df

#         df_state = process_quadrants(df_state)
#         df_dist = process_quadrants(df_dist)
#         df_pin = process_quadrants(df_pin)
        
#         df_dist['district'] = df_dist['district'].str.title()
#         df_pin['district'] = df_pin['district'].str.title()
#         df_pin['pincode'] = df_pin['pincode'].astype(str)
        
#         return df_state, df_dist, df_pin, df_daily, df_pin_daily
#     except Exception as e:
#         st.error(f"Data Error: {e}"); return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# df_state_plan, df_dist_plan, df_pin_plan, df_daily_sim, df_pin_sim = load_planner_data()

# st.title("💡 Strategic Planner")
# st.markdown("Turning operational data into **social impact** and **resource efficiency**.")

# # ==========================================
# # 1. CONTROLS
# # ==========================================
# selected_state, selected_dist = None, None
# filtered_df = pd.DataFrame()
# current_level_name = "State"

# with st.container():
#     c1, c2, c3 = st.columns([1, 1, 1])
#     with c1: view_level = st.radio("Strategy Level:", ["National", "State", "District"], label_visibility="collapsed")
    
#     if view_level == "National":
#         filtered_df = df_state_plan.copy()
#         current_level_name = "State"
#     elif view_level == "State":
#         with c2: selected_state = st.selectbox("Select State:", sorted(df_dist_plan['state'].unique()))
#         filtered_df = df_dist_plan[df_dist_plan['state'] == selected_state].copy()
#         current_level_name = "District"
#     elif view_level == "District":
#         with c2: selected_state = st.selectbox("Select State:", sorted(df_dist_plan['state'].unique()))
#         with c3: selected_dist = st.selectbox("Select District:", sorted(df_dist_plan[df_dist_plan['state']==selected_state]['district'].unique()))
#         filtered_df = df_pin_plan[(df_pin_plan['state'] == selected_state) & (df_pin_plan['district'] == selected_dist)].copy()
#         current_level_name = "Pincode"

# # ==========================================
# # Q7: SERVICE DELIVERY MATRIX
# # ==========================================
# st.markdown("---"); st.header("1. The Service Delivery Matrix")

# if not filtered_df.empty:
#     c1, c2, c3 = st.columns(3)
#     c1.metric(f"Total {current_level_name}s", f"{len(filtered_df)}")
#     c2.metric("Last Mile Priority", f"{len(filtered_df[filtered_df['Strategy_Quadrant']=='The Last Mile'])}")
#     c3.metric("Hyper-Growth", f"{len(filtered_df[filtered_df['Strategy_Quadrant']=='Hyper-Growth Hubs'])}")

#     strategy_colors = {"Hyper-Growth Hubs": MODERN_COLORS['hyper_growth'], "The Last Mile": MODERN_COLORS['last_mile'], "Digital Mature": MODERN_COLORS['digital_mature'], "Low Intensity": MODERN_COLORS['dormant'], '(?)': '#2a2a2a'}
    
#     path_list = []
#     if view_level == "National": path_list = [px.Constant("India"), 'Strategy_Quadrant', 'state']
#     elif view_level == "State": path_list = [px.Constant(selected_state), 'Strategy_Quadrant', 'district']
#     elif view_level == "District": path_list = [px.Constant(selected_dist), 'Strategy_Quadrant', 'pincode']

#     fig_treemap = px.treemap(filtered_df, path=path_list, values='total_transactions', color='Strategy_Quadrant', color_discrete_map=strategy_colors, custom_data=['Enrolment_Demand', 'Update_Demand'])
#     fig_treemap.update_traces(marker=dict(line=dict(width=1, color=MODERN_COLORS['background'])), root_color=MODERN_COLORS['background'], textinfo="label+value", hovertemplate="<b>%{label}</b><br>Vol: %{value}<br>Enrols: %{customdata[0]}<br>Updates: %{customdata[1]}")
#     fig_treemap.update_layout(height=600, paper_bgcolor=MODERN_COLORS['background'], font_color=MODERN_COLORS['text_subtle'], margin = dict(t=20, l=10, r=10, b=10))
#     st.plotly_chart(fig_treemap, use_container_width=True)

#     with st.expander("ℹ️ Strategic Playbook"):
#         st.markdown(f"1. <span style='color:{MODERN_COLORS['hyper_growth']}'>■</span> **Hyper-Growth:** Permanent centers.<br>2. <span style='color:{MODERN_COLORS['last_mile']}'>■</span> **Last Mile:** Mobile camps.<br>3. <span style='color:{MODERN_COLORS['digital_mature']}'>■</span> **Digital Mature:** Self-Service.", unsafe_allow_html=True)

# # ==========================================
# # Q8: INVISIBLE CHILD
# # ==========================================
# st.markdown("---"); st.header("2. The 'Invisible Child' Initiative")

# if not filtered_df.empty:
#     df_plot = filtered_df.sort_values('enrolment_gap', ascending=False)
#     # Ensure ID column is lower case for plotting logic consistency
#     id_col = current_level_name.lower()
    
#     # Filter only positive gaps
#     df_plot = df_plot[df_plot['enrolment_gap'] > 0].head(20)

#     if not df_plot.empty:
#         fig_gap = px.bar(df_plot.sort_values('enrolment_gap', ascending=True), x='enrolment_gap', y=id_col, orientation='h', title=f"Top Missing Enrolments ({current_level_name})", labels={'enrolment_gap': 'Missing Gap', id_col: current_level_name}, color='enrolment_gap', color_continuous_scale=['#222', MODERN_COLORS['last_mile']])
#         fig_gap.update_layout(height=600, paper_bgcolor=MODERN_COLORS['background'], plot_bgcolor='rgba(0,0,0,0)', font_color=MODERN_COLORS['text_subtle'], yaxis=dict(type='category'))
#         st.plotly_chart(fig_gap, use_container_width=True)
#     else:
#         st.success("No significant enrolment gaps detected here.")

# # ==========================================
# # Q9: SMART GOAL SETTER
# # ==========================================
# st.markdown("---"); st.header("3. The 'Smart Goal' Setter")

# sim_source = pd.DataFrame()
# entity_list = []
# entity_name = ""

# if view_level == "District":
#     # Use Pincode Daily for Simulation
#     sim_source = df_pin_sim[(df_pin_sim['state'] == selected_state) & (df_pin_sim['district'] == selected_dist)]
#     if not sim_source.empty: sim_source['pincode'] = sim_source['pincode'].astype(str)
#     entity_list = sorted(filtered_df['pincode'].unique())
#     entity_name = "pincode"
# else:
#     # Use District Daily for Simulation (States are aggregated from District Daily)
#     sim_source = df_daily_sim.copy()
#     if view_level == "State": sim_source = sim_source[sim_source['state'] == selected_state]
    
#     # If National view, we simulate States. If State view, we simulate Districts.
#     if view_level == "National":
#         # Aggregate to State level for simulation source
#         sim_source = sim_source.groupby(['date', 'state'])['total_transactions'].sum().reset_index()
#         entity_list = sorted(filtered_df['state'].unique())
#         entity_name = "state"
#     else:
#         entity_list = sorted(filtered_df['district'].unique())
#         entity_name = "district"

# if not sim_source.empty and len(entity_list) > 0:
#     # Auto Select
#     prio = filtered_df[filtered_df['Strategy_Quadrant'] == 'The Last Mile'][entity_name].unique()
#     ix = list(entity_list).index(prio[0]) if len(prio) > 0 and prio[0] in entity_list else 0
#     sel_ent = st.selectbox(f"Select {entity_name.title()} to Simulate:", entity_list, index=ix)
    
#     ts = sim_source[sim_source[entity_name] == sel_ent]['total_transactions']
    
#     if len(ts) > 5:
#         sims = [ts.sample(n=30, replace=True).sum() for _ in range(1000)]
#         p10, p50, p90 = np.percentile(sims, [10, 50, 90])
#         c1, c2, c3 = st.columns(3)
#         c1.metric("Conservative", f"{int(p10):,}"); c2.metric("Likely", f"{int(p50):,}"); c3.metric("Ambitious", f"{int(p90):,}")
#         fig_sim = px.histogram(x=sims, nbins=40, title=f"Probabilistic Forecast: {sel_ent}")
#         fig_sim.update_traces(marker_color=MODERN_COLORS['digital_mature'])
#         fig_sim.add_vline(x=p50, line_dash="dash", line_color="white")
#         fig_sim.update_layout(paper_bgcolor=MODERN_COLORS['background'], plot_bgcolor='rgba(0,0,0,0)', font_color=MODERN_COLORS['text_subtle'], showlegend=False)
#         st.plotly_chart(fig_sim, use_container_width=True)
#     else: st.warning(f"Insufficient history for {sel_ent}.")

# import streamlit as st
# import pandas as pd
# import duckdb
# import plotly.express as px
# import numpy as np

# st.set_page_config(page_title="Strategic Planner", page_icon="💡", layout="wide")

# # --- 🎨 DESIGN PIVOT: NEON NOIR ---
# # Mapping keys to new Neon Fluorescents
# MODERN_COLORS = {
#     'bg': '#000000', 
#     'text': '#FFFFFF', 
#     'sub': '#A0A0A0', 
#     'cyan': '#00E5FF',      # Secondary
#     'pink': '#FF00FF',      # Tertiary
#     'gold': '#CCFF00',      # Primary (Lime)
#     'dark': '#111111', 
#     'dormant': "#333333"
# }

# # --- IN pages/3_Strategic_Planner.py ---

# font_css = """
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

# .stApp { background-color: #000000; }

# /* Global Typography */
# html, body, [class*="css"] { 
#     font-family: 'Outfit', sans-serif !important; 
# }

# h1, h2, h3 { color: #FFFFFF; font-weight: 700; }
# p, label, .stMarkdown { color: #AAAAAA; }

# /* Metrics Styling */
# div[data-testid="stMetricLabel"] { color: #CCFF00 !important; }
# div[data-testid="stMetricValue"] { color: #FFFFFF !important; }

# /* --- FORCE DARK SIDEBAR --- */
# section[data-testid="stSidebar"] {
#     background-color: #050505 !important; /* Forces Dark Background */
#     border-right: 1px solid #222 !important;
# }
# div[data-testid="stSidebarNav"] {
#     background-color: #050505 !important;
# }

# /* Sidebar Inputs Background */
# .stSelectbox div[data-baseweb="select"] > div { 
#     background-color: #111 !important; 
#     color: white !important; 
#     border-color: #333 !important; 
# }
# </style>
# """
# st.markdown(font_css, unsafe_allow_html=True)
# # ----------------------------------------
# @st.cache_data
# def load_data():
#     try:
#         con = duckdb.connect('database/analytics.db', read_only=True)
#         s = con.execute("SELECT * FROM state_summary").fetchdf()
#         d = con.execute("SELECT * FROM district_summary").fetchdf()
#         p = con.execute("SELECT * FROM pincode_summary").fetchdf()
#         daily = con.execute("SELECT * FROM district_daily").fetchdf()
#         p_daily = con.execute("SELECT * FROM pincode_daily").fetchdf()
#         con.close()
        
#         def quad(df):
#             if df.empty: return df
#             if 'total_child_enrolments' in df: df['E'] = df['total_child_enrolments']+df['total_adult_enrolments']; df['U'] = df['total_bio']+df['total_demo']
#             me, mu = df['E'].median(), df['U'].median()
#             df['Quad'] = df.apply(lambda r: "Hyper-Growth Hubs" if r['E']>=me and r['U']>=mu else ("The Last Mile" if r['E']>=me else ("Digital Mature" if r['U']>=mu else "Low Intensity")), axis=1)
#             return df

#         s, d, p = quad(s), quad(d), quad(p)
#         if not d.empty: d['district'] = d['district'].str.title()
#         if not p.empty: p['district'] = p['district'].str.title(); p['pincode'] = p['pincode'].astype(str)
#         return s, d, p, daily, p_daily
#     except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# df_s, df_d, df_p, df_daily, df_p_daily = load_data()

# # --- SIDEBAR View Controller  ---
# with st.sidebar:
#     st.header("🔭 View Controller ")
#     view_level = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (District)"])
#     selected_state, selected_dist = None, None
#     if view_level in ["Mosaic (State)", "Tessera (District)"]:
#         selected_state = st.selectbox("Select State:", sorted(df_d['state'].unique()))
#     if view_level == "Tessera (District)":
#         selected_dist = st.selectbox("Select District:", sorted(df_d[df_d['state']==selected_state]['district'].unique()))
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
# filt_df, col_name = pd.DataFrame(), ""
# if view_level == "Adamento (National)": filt_df, col_name = df_s.copy(), "State"
# elif view_level == "Mosaic (State)" and selected_state: filt_df, col_name = df_d[df_d['state']==selected_state].copy(), "District"
# elif view_level == "Tessera (District)" and selected_dist: filt_df, col_name = df_p[(df_p['state']==selected_state)&(df_p['district']==selected_dist)].copy(), "Pincode"

# st.title("Strategic Planner")

# # --- Q1 MATRIX ---
# st.header("1. The Service Delivery Matrix")
# st.markdown("We are deciding exactly where to build a permanent office versus where to just send a mobile van based on local needs.")
# if not filt_df.empty:
#     c1, c2, c3 = st.columns(3)
#     c1.metric(f"Total {col_name}s", f"{len(filt_df)}")
#     c2.metric("Last Mile Priority", f"{len(filt_df[filt_df['Quad']=='The Last Mile'])}")
#     c3.metric("Hyper-Growth", f"{len(filt_df[filt_df['Quad']=='Hyper-Growth Hubs'])}")

#     colors = {"Hyper-Growth Hubs": MODERN_COLORS['cyan'], "The Last Mile": MODERN_COLORS['pink'], "Digital Mature": MODERN_COLORS['gold'], "Low Intensity": MODERN_COLORS['dormant']}
#     path = [px.Constant("India"), 'Quad', 'state'] if view_level=="Adamento (National)" else ([px.Constant(selected_state), 'Quad', 'district'] if view_level=="Mosaic (State)" else [px.Constant(selected_dist), 'Quad', 'pincode'])
    
#     fig = px.treemap(filt_df, path=path, values='total_transactions', color='Quad', color_discrete_map=colors)
#     fig.update_traces(marker=dict(line=dict(width=1, color=MODERN_COLORS['bg'])), root_color=MODERN_COLORS['bg'])
#     fig.update_layout(height=600, paper_bgcolor=MODERN_COLORS['bg'], font_color=MODERN_COLORS['sub'], margin=dict(t=20,l=10,r=10,b=10))
#     st.plotly_chart(fig, use_container_width=True)

# with st.expander("ℹ️ How to read this Matrix: Service Delivery"):
#     st.markdown("""
#     **Why are we asking this?** To segment districts into 4 strategic quadrants for resource allocation.
    
#     **📊 The Technique: Median-Based Matrix Segmentation**
#     We divide districts based on whether they are above or below the Median for Enrolment and Updates.
    
#     **🔍 Interpretation:**
#     *   **<span style='color:#00FFFF'>Hyper-Growth (High/High):</span>** Max demand. Strategy: **Permanent Centers**.
#     *   **<span style='color:#FF00AA'>The Last Mile (High Enrol/Low Update):</span>** Remote, unconnected. Strategy: **Mobile Camps**.
#     *   **<span style='color:#FBC02D'>Digital Mature (Low Enrol/High Update):</span>** Tech-savvy. Strategy: **Self-Service/Online**.
#     *   **Low Intensity:** Maintain status quo.
#     """, unsafe_allow_html=True)
# # --- Q2 GAP ---
# st.markdown("---"); st.header("2. The 'Invisible Child' Initiative")
# st.markdown("We are calculating the exact number of children missing from the database to give field teams a specific 'Hit List.'")
# if not filt_df.empty:
#     plot_df = filt_df.sort_values('enrolment_gap', ascending=False)
#     y_c = col_name.lower()
    
#     if view_level == "Adamento (National)": plot_df = plot_df.head(20)
#     elif view_level == "Tessera (District)": plot_df = plot_df.head(20)

#     plot_df = plot_df[plot_df['enrolment_gap'] > 0]

#     if not plot_df.empty:
#         fig = px.bar(plot_df.sort_values('enrolment_gap'), x='enrolment_gap', y=y_c, orientation='h', color='enrolment_gap', color_continuous_scale=['#222', MODERN_COLORS['pink']], title=f"Missing Enrolments ({col_name})")
#         fig.update_layout(height=600, paper_bgcolor=MODERN_COLORS['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=MODERN_COLORS['sub'], yaxis={'type':'category'},xaxis_title="Estimated Missing Children",yaxis_title=col_name)
#         st.plotly_chart(fig, use_container_width=True)
#     else: st.success("No significant gaps.")

# with st.expander("ℹ️ How to read this Chart: The Invisible Child"):
#     st.markdown("""
#     **Why are we asking this?** To estimate the exact number of missing children in a specific area for the Bal Aadhaar campaign.
    
#     **📊 The Technique: Predictive Gap Modeling**
#     We use a regression model to predict how many children *should* exist, and subtract the actual enrolled count.
    
#     **🔍 Interpretation:**
#     *   **Bar Length:** Represents the estimated number of **Missing Children**.
#     *   This generates a prioritized "Hit List" for field officers to target schools and anganwadis.
#     """, unsafe_allow_html=True)

# # --- Q3 SIMULATION ---
# st.markdown("---"); st.header("3. The 'Smart Goal' Setter")
# st.markdown("We are setting fair, realistic daily targets for officers based on their local history, instead of forcing unfair quotas on them.")
# sim_src, ent_list, ent_key = pd.DataFrame(), [], ""

# if view_level == "Tessera (District)":
#     sim_src = df_p_daily[(df_p_daily['state']==selected_state)&(df_p_daily['district']==selected_dist)].copy()
#     if not sim_src.empty: sim_src['pincode'] = sim_src['pincode'].astype(str)
#     ent_list, ent_key = sorted(filt_df['pincode'].unique()), "pincode"
# else:
#     sim_src = df_daily.copy()
#     if view_level == "Mosaic (State)": sim_src = sim_src[sim_src['state']==selected_state]
#     if view_level == "Adamento (National)": sim_src = sim_src.groupby(['date','state'])['total_transactions'].sum().reset_index()
#     ent_list, ent_key = sorted(filt_df[col_name.lower()].unique()), col_name.lower()

# if not sim_src.empty and len(ent_list)>0:
#     prio = filt_df[filt_df['Quad']=='The Last Mile'][ent_key].unique()
#     ix = list(ent_list).index(prio[0]) if len(prio)>0 and prio[0] in ent_list else 0
#     sel = st.selectbox(f"Select {ent_key.title()} to Simulate:", ent_list, index=ix)
    
#     ts = sim_src[sim_src[ent_key]==sel]['total_transactions']
#     if len(ts)>5:
#         sims = [ts.sample(n=30, replace=True).sum() for _ in range(1000)]
#         p10, p50, p90 = np.percentile(sims, [10, 50, 90])
#         c1, c2, c3 = st.columns(3)
#         c1.metric("Conservative (P10)", f"{int(p10):,}"); c2.metric("Likely (P50)", f"{int(p50):,}"); c3.metric("Ambitious (P90)", f"{int(p90):,}")
#         fig = px.histogram(x=sims, nbins=40, title=f"Probabilistic Forecast: {sel}")
#         fig.update_traces(marker_color=MODERN_COLORS['gold'])
#         fig.add_vline(x=p50, line_dash="dash", line_color="white")
#         fig.update_layout(paper_bgcolor=MODERN_COLORS['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=MODERN_COLORS['sub'], showlegend=False,xaxis_title="Predicted Monthly Volume",yaxis_title="Frequency of Outcome",yaxis=dict(type='linear'))
#         st.plotly_chart(fig, use_container_width=True)
#     else: st.warning("Insufficient data.")

# with st.expander("ℹ️ How to read this Chart: Smart Goal Setter"):
#     st.markdown("""
#     **Why are we asking this?** To set fair, probability-based targets for officers instead of arbitrary quotas.
    
#     **📊 The Technique: Monte Carlo Simulation (Bootstrapping)**
#     We simulate the next month 1,000 times based on the specific district's historical daily performance.
    
#     **🔍 Interpretation:**
#     *   **Conservative (P10):** A safe target. Achievable 90% of the time. Use for **Base Salary**.
#     *   **Ambitious (P90):** A stretch target. Achievable only 10% of the time. Use for **Bonuses**.
#     """, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Strategic Planner", page_icon="💡", layout="wide")

# --- 🎨 THEME: TRICOLOR INTELLIGENCE (Dark Mode) ---
COLOR_MAP = {
    'bg': '#050505',           # Deepest Black-Blue
    'card': '#111111',         # Card Background
    'cyan': '#2979FF',         # Electric Blue (Hyper-Growth/Tech)
    'pink': '#FF9100',         # Neon Saffron (Last Mile/Priority)
    'gold': '#00E676',         # Signal Green (Mature/Safe)
    'red': '#FF3D00',          # Critical
    'grey': '#9E9E9E',         # Muted Text
    'dormant': '#1E1E1E'       # Low Intensity
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
p, label, .stMarkdown { color: #9E9E9E !important; }

/* Metrics Styling */
div[data-testid="stMetricLabel"] { color: #2979FF !important; }
div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 600; }

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
# DATA LOADING
# ----------------------------------------
@st.cache_data
def load_data():
    try:
        con = duckdb.connect('database/analytics.db', read_only=True)
        s = con.execute("SELECT * FROM state_summary").fetchdf()
        d = con.execute("SELECT * FROM district_summary").fetchdf()
        p = con.execute("SELECT * FROM pincode_summary").fetchdf()
        daily = con.execute("SELECT * FROM district_daily").fetchdf()
        p_daily = con.execute("SELECT * FROM pincode_daily").fetchdf()
        con.close()
        
        def quad(df):
            if df.empty: return df
            if 'total_child_enrolments' in df: df['E'] = df['total_child_enrolments']+df['total_adult_enrolments']; df['U'] = df['total_bio']+df['total_demo']
            me, mu = df['E'].median(), df['U'].median()
            df['Quad'] = df.apply(lambda r: "Hyper-Growth Hubs" if r['E']>=me and r['U']>=mu else ("The Last Mile" if r['E']>=me else ("Digital Mature" if r['U']>=mu else "Low Intensity")), axis=1)
            return df

        s, d, p = quad(s), quad(d), quad(p)
        if not d.empty: d['district'] = d['district'].str.title()
        if not p.empty: p['district'] = p['district'].str.title(); p['pincode'] = p['pincode'].astype(str)
        return s, d, p, daily, p_daily
    except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_state, df_dist, df_pin, df_daily, df_p_daily = load_data()

# --- SIDEBAR CONTROLLER ---
with st.sidebar:
    st.header("🔭 View Controller")
    view_level = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (District)"])
    # Inside the Sidebar View Controller block
    selected_state, selected_dist = None, None
    
    # Logic to get the list (df name varies per file: df_dist, df_d, or df_dist)
    # Assuming standard df names from your files (df_dist/df_d)
    
    if view_level in ["Mosaic (State)", "Tessera (District)"]: # Or "Tessera (Pincode)" for Page 2
        # Get list from your specific dataframe
        # Note: Replace 'df_source' with df_dist (Page 1), df_d (Page 2/3)
        states = sorted(df_dist['state'].unique()) if 'df_dist' in locals() else sorted(df_dist['state'].unique())
        
        # Default to Maharashtra
        st_ix = states.index('Maharashtra') if 'Maharashtra' in states else 0
        selected_state = st.selectbox("Select State:", states, index=st_ix)
        
    if view_level == "Tessera (District)": # Or "Tessera (Pincode)" for Page 2
        # Get list
        source_df = df_dist if 'df_dist' in locals() else df_dist
        dists = sorted(source_df[source_df['state'] == selected_state]['district'].unique())
        
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
filt_df, col_name = pd.DataFrame(), ""
if view_level == "Adamento (National)": filt_df, col_name = df_state.copy(), "State"
elif view_level == "Mosaic (State)" and selected_state: filt_df, col_name = df_dist[df_dist['state']==selected_state].copy(), "District"
elif view_level == "Tessera (District)" and selected_dist: filt_df, col_name = df_pin[(df_pin['state']==selected_state)&(df_pin['district']==selected_dist)].copy(), "Pincode"

st.title("Strategic Planning Console")

# ----------------------------------------
# Q1: SERVICE MATRIX
# ----------------------------------------
st.header("1. The Service Delivery Matrix")
st.markdown("We are deciding exactly where to build a permanent office versus where to just send a mobile van based on local needs.")
st.caption("A quadrant analysis separating regions by 'Growth Demand' vs 'Maintenance Demand' to optimize asset deployment.")

if not filt_df.empty:
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Total {col_name}s", f"{len(filt_df)}")
    c2.metric("Last Mile Priority", f"{len(filt_df[filt_df['Quad']=='The Last Mile'])}")
    c3.metric("Hyper-Growth Hubs", f"{len(filt_df[filt_df['Quad']=='Hyper-Growth Hubs'])}")

    # Palette Mapping: Blue(Growth), Saffron(Last Mile), Green(Mature)
    colors = {
        "Hyper-Growth Hubs": COLOR_MAP['cyan'], 
        "The Last Mile": COLOR_MAP['pink'], 
        "Digital Mature": COLOR_MAP['gold'], 
        "Low Intensity": COLOR_MAP['dormant']
    }
    
    path = [px.Constant("India"), 'Quad', 'state'] if view_level=="Adamento (National)" else ([px.Constant(selected_state), 'Quad', 'district'] if view_level=="Mosaic (State)" else [px.Constant(selected_dist), 'Quad', 'pincode'])
    
    fig = px.treemap(filt_df, path=path, values='total_transactions', color='Quad', color_discrete_map=colors)
    fig.update_traces(marker=dict(line=dict(width=1, color=COLOR_MAP['bg'])), root_color=COLOR_MAP['bg'])
    fig.update_layout(height=600, paper_bgcolor=COLOR_MAP['bg'], font_color=COLOR_MAP['grey'], margin=dict(t=20,l=10,r=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

with st.expander("ℹ️ How to interpret the Service Matrix"):
    st.markdown(f"""
    **The Insight:**
    One strategy does not fit all. We segment regions to align infrastructure with actual user behavior.
    
    **The Technique: Median-Based Segmentation**
    We divide units into 4 quadrants based on their position relative to the median Enrolment and Update volume.
    
    **Strategic Actions:**
    *   **<span style='color:{COLOR_MAP['cyan']}'>Hyper-Growth (Blue):</span>** High demand for everything. Strategy: **Permanent Centers (ASK)**.
    *   **<span style='color:{COLOR_MAP['pink']}'>The Last Mile (Saffron):</span>** High enrollment need, unconnected. Strategy: **Mobile Camps**.
    *   **<span style='color:{COLOR_MAP['gold']}'>Digital Mature (Green):</span>** Tech-savvy, updates only. Strategy: **Self-Service Online**.
    """, unsafe_allow_html=True)

# ----------------------------------------
# Q2: INVISIBLE CHILD
# ----------------------------------------
st.markdown("---")
st.header("2. The 'Invisible Child' Initiative")
st.markdown("We are calculating the exact number of children missing from the database to give field teams a specific 'Hit List.'")
st.caption("Predictive gap modeling to quantify exclusion in the 0-5 and 5-17 age brackets.")

if not filt_df.empty:
    plot_df = filt_df.sort_values('enrolment_gap', ascending=False)
    y_c = col_name.lower()
    
    if view_level == "Adamento (National)": plot_df = plot_df.head(20)
    elif view_level == "Tessera (District)": plot_df = plot_df.head(20)

    plot_df = plot_df[plot_df['enrolment_gap'] > 0]

    if not plot_df.empty:
        # Gradient: Dark to Saffron (Priority)
        fig = px.bar(
            plot_df.sort_values('enrolment_gap'), x='enrolment_gap', y=y_c, orientation='h', 
            color='enrolment_gap', color_continuous_scale=['#222', COLOR_MAP['pink']], 
            title=f"Estimated Missing Enrolments ({col_name})"
        )
        fig.update_layout(
            height=600, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', 
            font_color=COLOR_MAP['grey'], yaxis={'type':'category'},
            xaxis_title="Estimated Missing Children", yaxis_title=col_name,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else: st.success("No significant exclusion gaps detected.")

with st.expander("ℹ️ How to interpret the Invisible Child Model"):
    st.markdown("""
    **The Insight:**
    "Low enrollment" is vague. Field officers need specific targets.
    
    **The Technique: Predictive Gap Modeling**
    We use regression to predict the expected child population based on adult population density, then subtract actual enrolments.
    
    **Visual Guide:**
    *   **Bar Length:** Represents the headcount of **Missing Children**.
    *   This generates a prioritized "Hit List" for the Bal Aadhaar campaign.
    """, unsafe_allow_html=True)

# ----------------------------------------
# Q3: SMART GOAL SETTER
# ----------------------------------------
st.markdown("---")
st.header("3. The 'Smart Goal' Setter")
st.markdown("We are setting fair, realistic daily targets for officers based on their local history, instead of forcing unfair quotas on them.")
st.caption("Monte Carlo simulations to generate probabilistic performance benchmarks.")

sim_src, ent_list, ent_key = pd.DataFrame(), [], ""

if view_level == "Tessera (District)":
    sim_src = df_p_daily[(df_p_daily['state']==selected_state)&(df_p_daily['district']==selected_dist)].copy()
    if not sim_src.empty: sim_src['pincode'] = sim_src['pincode'].astype(str)
    ent_list, ent_key = sorted(filt_df['pincode'].unique()), "pincode"
else:
    sim_src = df_daily.copy()
    if view_level == "Mosaic (State)": sim_src = sim_src[sim_src['state']==selected_state]
    if view_level == "Adamento (National)": sim_src = sim_src.groupby(['date','state'])['total_transactions'].sum().reset_index()
    ent_list, ent_key = sorted(filt_df[col_name.lower()].unique()), col_name.lower()

if not sim_src.empty and len(ent_list)>0:
    prio = filt_df[filt_df['Quad']=='The Last Mile'][ent_key].unique()
    ix = list(ent_list).index(prio[0]) if len(prio)>0 and prio[0] in ent_list else 0
    sel = st.selectbox(f"Select {ent_key.title()} to Simulate:", ent_list, index=ix)
    
    ts = sim_src[sim_src[ent_key]==sel]['total_transactions']
    if len(ts)>5:
        sims = [ts.sample(n=30, replace=True).sum() for _ in range(1000)]
        p10, p50, p90 = np.percentile(sims, [10, 50, 90])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Safe Base (P10)", f"{int(p10):,}")
        c2.metric("Likely Target (P50)", f"{int(p50):,}")
        c3.metric("Ambitious Goal (P90)", f"{int(p90):,}")
        
        fig = px.histogram(x=sims, nbins=40, title=f"Probabilistic Forecast: {sel}")
        fig.update_traces(marker_color=COLOR_MAP['gold']) # Green for Success Targets
        fig.add_vline(x=p50, line_dash="dash", line_color="white")
        fig.update_layout(
            paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', 
            font_color=COLOR_MAP['grey'], showlegend=False,
            xaxis_title="Predicted Monthly Volume", yaxis_title="Frequency",
            yaxis=dict(type='linear')
        )
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("Insufficient historical data for simulation.")

with st.expander("ℹ️ How to interpret the Smart Goal Setter"):
    st.markdown("""
    **The Insight:**
    A field officer in a remote village cannot be judged by the same standards as one in a metro city.
    
    **The Technique: Monte Carlo Simulation**
    We simulate the next month 1,000 times using that specific center's historical DNA.
    
    **Benchmarks:**
    *   **Conservative (P10):** Achieved 90% of the time. Use for **Base Salary**.
    *   **Ambitious (P90):** Achieved only 10% of the time. Use for **Performance Bonuses**.
    """, unsafe_allow_html=True)