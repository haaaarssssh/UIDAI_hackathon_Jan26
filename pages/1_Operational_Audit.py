# import streamlit as st
# import pandas as pd
# import duckdb
# import plotly.express as px
# import plotly.graph_objects as go
# import json

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Operational Audit", page_icon="🩺", layout="wide")

# # --- COLOR & STYLE ---
# SOLID_COLORS = {
#     'red': '#D32F2F', 'blue': '#1976D2', 'green': '#388E3C', 'yellow': '#FBC02D'
# }
# COLOR_MAP = {
#     '--void-purple': '#0F001A', '--toxic-cyan': '#00FFFF', '--chrome-grey': '#B0B0B0','--neon-magenta': '#FF00FF', '--corroded-gold': '#FFD700'
# }
# css = f"""
# <style>
#     .stApp {{ background-color: {COLOR_MAP['--void-purple']}; }}
#     h1, h2, h3 {{ color: {COLOR_MAP['--toxic-cyan']}; }}
#     p, div, label, .st-emotion-cache-16idsys p {{ color: {COLOR_MAP['--chrome-grey']}; }}
# </style>
# """
# st.markdown(css, unsafe_allow_html=True)

# # --- DATA LOADING ---
# @st.cache_data
# def load_audit_data():
#     try:
#         with open('data/india_districts_simplified.geojson', encoding='utf-8') as f:
#             geojson = json.load(f)
#     except:
#         geojson = None

#     con = duckdb.connect(database='database/analytics.db', read_only=True)
    
#     # 1. Fetch District Detail
#     df_district_detail = con.execute("""
#         SELECT state, district, consistency, intensity, archetype_label 
#         FROM district_summary
#     """).fetchdf()
    
#     # 2. Fetch Daily Data
#     df_daily = con.execute("SELECT date, state, total_demo, total_enrol, total_bio FROM district_daily").fetchdf()
#     con.close()

#     # --- AGGREGATE TO STATE LEVEL ---
#     if not df_district_detail.empty:
#         df_state_map = df_district_detail.groupby('state').agg({
#             'consistency': 'mean',
#             'intensity': 'mean'
#         }).reset_index()

#         # National Thresholds
#         c_thresh = df_state_map['consistency'].quantile(0.75)
#         i_thresh = df_state_map['intensity'].quantile(0.75)

#         def get_state_archetype(row):
#             if row['consistency'] >= c_thresh and row['intensity'] >= i_thresh: return 'High-Consistency / High-Intensity'
#             elif row['consistency'] >= c_thresh: return 'High-Consistency / Stable'
#             elif row['intensity'] >= i_thresh: return 'High-Intensity / Sporadic'
#             return 'Standard Operations'

#         df_state_map['archetype_label'] = df_state_map.apply(get_state_archetype, axis=1)
#     else:
#         df_state_map = pd.DataFrame()

#     if not df_daily.empty:
#         df_daily['date'] = pd.to_datetime(df_daily['date'])
#         try:
#             df_daily['month_period'] = df_daily['date'].dt.to_period('M')
#         except:
#             df_daily['month_period'] = df_daily['date'].dt.strftime('%Y-%m')
#         df_daily['month'] = df_daily['date'].dt.month

#     return geojson, df_state_map, df_district_detail, df_daily

# geojson, df_state_map, df_district_detail, df_daily = load_audit_data()

# # --- PAGE LAYOUT ---
# st.title("🩺 Operational Audit")
# st.markdown("Diagnosing system stability and performance drivers.")

# # --- Q1: THE NATIONAL MAP (State Level - Reliable) ---
# st.header("1. Operational DNA: A National Footprint")
# archetype_colors = {
#     'High-Consistency / High-Intensity': SOLID_COLORS['yellow'],
#     'High-Consistency / Stable': SOLID_COLORS['green'],
#     'High-Intensity / Sporadic': SOLID_COLORS['red'],
#     'Standard Operations': SOLID_COLORS['blue'],
# }

# if geojson is not None and not df_state_map.empty:
#     fig_map = px.choropleth_mapbox(
#         df_state_map, 
#         geojson=geojson, 
#         featureidkey="properties.name", 
#         locations="state", 
#         color="archetype_label",
#         mapbox_style="carto-darkmatter", 
#         color_discrete_map=archetype_colors, 
#         height=500, zoom=3.4, center={"lat": 22.5, "lon": 82.0}
#     )
#     fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor=COLOR_MAP['--void-purple'])
#     st.plotly_chart(fig_map, use_container_width=True)
# else:
#     st.warning("Map Unavailable")

# st.markdown("---")

# # --- SUBSECTION: TYPOGRAPHIC STRATEGY CLOUD (WITH JITTER) ---
# st.markdown("### 🔍 Deep Dive: District Performance Map")
# st.markdown("_Districts distributed by performance. **High** = High Volume. **Right** = High Reliability._")

# if not df_district_detail.empty:
#     states_list = sorted(df_district_detail['state'].unique())
#     def_idx = states_list.index('Maharashtra') if 'Maharashtra' in states_list else 0
#     selected_state = st.selectbox("Select State to Investigate:", options=states_list, index=def_idx)
    
#     # Filter
#     state_dists = df_district_detail[df_district_detail['state'] == selected_state].copy()
    
#     if not state_dists.empty:
#         # --- THE FIX: MANUAL JITTER FOR TEXT SEPARATION ---
#         import numpy as np
        
#         # 1. Create a "Visual X" coordinate
#         # If standard consistency is clustered, we spread it out
#         rng = np.random.default_rng(42) # Fixed seed for consistency
#         # Add random spread between -1.5 and +1.5 to the X score
#         state_dists['visual_x'] = state_dists['consistency'] + rng.uniform(-1000.5, 1000.5, size=len(state_dists))
        
#         nat_cons_thresh = df_district_detail['consistency'].quantile(0.75)
#         nat_int_thresh = df_district_detail['intensity'].quantile(0.75)

#         # Scale Font Size based on Volume (Refined range: Min 8px, Max 18px to reduce clutter)
#         min_vol = state_dists['intensity'].min()
#         max_vol = state_dists['intensity'].max()
#         if max_vol == min_vol:
#             state_dists['font_size'] = 12
#         else:
#             state_dists['font_size'] = 9 + ((state_dists['intensity'] - min_vol) / (max_vol - min_vol) * 14)

#         # 2. Create the Chart using Visual X
#         fig_quad = px.scatter(
#             state_dists,
#             x="visual_x", # USE JITTERED X
#             y="intensity",
#             text="district", 
#             color="archetype_label", 
#             color_discrete_map={
#                 'High-Intensity / Sporadic': SOLID_COLORS['red'],
#                 'High-Consistency / High-Intensity': SOLID_COLORS['yellow'],
#                 'High-Consistency / Stable': SOLID_COLORS['green'],
#                 'Standard Operations': SOLID_COLORS['blue'],
#                 'Data Blindspot': '#444'
#             },
#             hover_data={'intensity':':.0f', 'consistency':':.1f', 'archetype_label':False, 'visual_x':False},
#         )

#         # 3. Typography Mode
#         fig_quad.update_traces(
#             mode='text', 
#             textposition='middle center',
#             textfont=dict(family="Arial") # Use cleaner font
#         )
        
#         # Apply calculated sizes & colors manually to ensuring coloring works
#         for trace in fig_quad.data:
#             # Match dataframe to trace category
#             trace_cat = trace.name
#             subset = state_dists[state_dists['archetype_label'] == trace_cat]
#             if not subset.empty:
#                 # Plotly express creates one trace per color, but ordering is tricky
#                 # Simplification: Apply uniform styling derived from the color map for readability
#                 trace.textfont.color = trace.marker.color
#                 # We apply the average size of this group to avoid list length mismatch errors 
#                 # (A visual trade-off for zero latency code simplicity)
#                 avg_size = subset['font_size'].mean()
#                 trace.textfont.size = avg_size 

#         # 4. The Quadrant Lines
#         fig_quad.add_vline(x=nat_cons_thresh, line_width=1, line_dash="dash", line_color="#444")
#         fig_quad.add_hline(y=nat_int_thresh, line_width=1, line_dash="dash", line_color="#444")

#         # 5. Background Labels (Fixed Transparency & Bold HTML)
#         x_min, x_max = state_dists['visual_x'].min(), state_dists['visual_x'].max()
#         y_max = state_dists['intensity'].max() * 1.1 # Headroom
#         y_min = state_dists['intensity'].min()
        
#         fig_quad.add_annotation(x=x_min, y=y_max, text="<b>🚩 RISK</b>", showarrow=False, font=dict(color=SOLID_COLORS['red'], size=16), opacity=0.3)
#         fig_quad.add_annotation(x=x_max, y=y_max, text="<b>⭐ GOLD</b>", showarrow=False, font=dict(color=SOLID_COLORS['yellow'], size=16), opacity=0.3)

#         # 6. Layout adjustments
#         fig_quad.update_layout(
#             height=650,
#             paper_bgcolor=COLOR_MAP['--void-purple'],
#             plot_bgcolor='rgba(0,0,0,0)',
#             font=dict(color=COLOR_MAP['--chrome-grey']),
#             showlegend=False, 
#             # Hide X axis grid because it's jittered/fuzzy now
#             xaxis=dict(title="Reliability Score", showgrid=False, zeroline=False, showticklabels=False),
#             yaxis=dict(title="Transaction Volume", showgrid=False, zeroline=False),
#             margin=dict(t=40, l=40, r=40, b=40)
#         )

#         st.plotly_chart(fig_quad, use_container_width=True)
#         st.caption("Chart uses horizontal spread (jitter) to prevent text overlap for highly clustered districts.")

#     else:
#         st.info("No data available.")
# else:
#     st.warning("District details not available.")
# st.markdown("---")
# import streamlit as st
# import pandas as pd
# import duckdb
# import folium
# from streamlit_folium import st_folium
# import plotly.express as px
# import json

# # --- PAGE CONFIG ---
# st.set_page_config(page_title="Operational Audit", page_icon="🩺", layout="wide")

# # --- COLORS & STYLE ---
# COLOR_MAP = {
#     'bg': '#0F001A', 
#     'cyan': '#00FFFF', 
#     'pink': '#FF00AA', 
#     'gold': '#FFD700', 
#     'grey': '#B0B0B0', 
#     'blue': '#1976D2',
#     'red': '#FF4B4B',   
#     'slate': '#2F3336', 
#     'border': '#4A4A4A'
# }

# css = f"""
# <style>
#     .stApp {{ background-color: {COLOR_MAP['bg']}; }}
#     h1, h2, h3, div, label {{ color: {COLOR_MAP['cyan']}; }}
#     p, .stMarkdown, .st-emotion-cache-16idsys p {{ color: {COLOR_MAP['grey']}; }}
    
#     .legend-box {{
#         display: flex; flex-direction: row; gap: 20px; 
#         background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px;
#         margin-bottom: 10px; border: 1px solid #333;
#         align-items: center;
#     }}
#     .legend-item {{ display: flex; align-items: center; gap: 8px; font-size: 14px; color: {COLOR_MAP['grey']}; }}
#     .dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
#     .stRadio [role=radiogroup] {{ flex-direction: row; gap: 20px; }}
# </style>
# """
# st.markdown(css, unsafe_allow_html=True)

# # --- DATA LOADING ---
# @st.cache_data
# def load_data_coordinates():
#     try:
#         with open('data/india_districts_simplified.geojson', encoding='utf-8') as f:
#             geojson = json.load(f)
#         con = duckdb.connect('database/analytics.db', read_only=True)
#         df_state = con.execute("SELECT * FROM state_geo").fetchdf()
#         df_dist = con.execute("SELECT * FROM dist_geo").fetchdf()
#         df_pin = con.execute("SELECT * FROM pin_geo").fetchdf()
#         df_daily = con.execute("SELECT * FROM district_daily").fetchdf()
#         df_pin_daily = con.execute("SELECT * FROM pincode_daily").fetchdf()
#         con.close()
        
#         # Normalize
#         if not df_dist.empty: df_dist['district'] = df_dist['district'].str.title()
#         if not df_daily.empty: df_daily['district'] = df_daily['district'].str.title()
        
#         return geojson, df_state, df_dist, df_pin, df_daily, df_pin_daily
#     except Exception as e:
#         st.error(f"Data Error: {e}")
#         return None, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# geojson, df_state, df_dist, df_pin, df_daily, df_pin_daily = load_data_coordinates()

# # --- HELPER: DYNAMIC GEOJSON FILTER ---
# def filter_geojson(full_geojson, state_name=None, district_name=None):
#     if not full_geojson: return None
#     filtered_features = []
#     props = full_geojson['features'][0]['properties']
#     st_keys = ['st_nm', 'state', 'STATE', 'name_1']
#     st_key = next((k for k in st_keys if k in props), 'st_nm')
#     dt_keys = ['district', 'dtname', 'DISTRICT', 'name_2']
#     dt_key = next((k for k in dt_keys if k in props), 'district')

#     for feature in full_geojson['features']:
#         p = feature['properties']
#         if state_name:
#             map_state = p.get(st_key, '').lower()
#             if state_name.lower() not in map_state and map_state not in state_name.lower(): continue
#         if district_name:
#             map_dist = p.get(dt_key, '').lower()
#             if district_name.lower() not in map_dist: continue
#         filtered_features.append(feature)
    
#     if not filtered_features: return None
#     return {"type": "FeatureCollection", "features": filtered_features}

# st.title("🩺 Operational Geoscanner")

# # ==========================================
# # 1. MAP CONTROLS
# # ==========================================
# st.header("1. The Access Inequality Map")

# with st.container():
#     c1, c2, c3 = st.columns([2, 1, 1])
#     with c1:
#         view_mode = st.radio("Select Zoom Level:", ["1. National Load (State)", "2. District Grid", "3. Pincode Trace"], label_visibility="collapsed")
    
#     selected_state = None
#     selected_dist = None
#     if view_mode in ["2. District Grid", "3. Pincode Trace"]:
#         with c2:
#             state_list = sorted(df_dist['state'].unique()) if not df_dist.empty else []
#             selected_state = st.selectbox("Select State:", state_list)
#     if view_mode == "3. Pincode Trace":
#         with c3:
#             dist_list = []
#             if selected_state and not df_dist.empty:
#                 dist_list = sorted(df_dist[df_dist['state'] == selected_state]['district'].unique())
#             selected_dist = st.selectbox("Select District:", dist_list)

# # --- UNIFIED LEGEND ---
# st.markdown(f"""
#     <div class="legend-box">
#         <div class="legend-item">
#             <span class="dot" style="background:{COLOR_MAP['cyan']}"></span> <b>High Intensity</b> (Urban / Hubs)
#         </div>
#         <div class="legend-item">
#             <span class="dot" style="background:{COLOR_MAP['pink']}"></span> <b>The Last Mile</b> (Remote / Low Infra)
#         </div>
#         <div class="legend-item">
#             <span class="dot" style="background:{COLOR_MAP['gold']}"></span> <b>Standard Ops</b>
#         </div>
#         <div class="legend-item" style="margin-left: auto; font-style: italic; opacity: 0.7;">
#             *Dot Size = Transaction Volume
#         </div>
#     </div>
# """, unsafe_allow_html=True)

# # ==========================================
# # 2. MAP RENDERER
# # ==========================================
# m = folium.Map(location=[22.5, 82.0], zoom_start=5, tiles=None)
# folium.TileLayer(
#     tiles="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png",
#     attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
#     name='Void Dark',
#     control=False
# ).add_to(m)

# def style_slate(feature):
#     return {'fillColor': COLOR_MAP['slate'], 'color': COLOR_MAP['border'], 'weight': 1, 'fillOpacity': 0.7}

# # --- VIEW LOGIC ---

# if view_mode == "1. National Load (State)":
#     if geojson:
#         folium.GeoJson(geojson, name="India", style_function=style_slate).add_to(m)
#         m.fit_bounds([[6.0, 68.0], [37.5, 97.5]])
#     if not df_dist.empty:
#         # Aggregate State Data
#         state_agg = df_dist.groupby('state').agg({'total_transactions': 'sum', 'active_pincodes': 'sum', 'lat': 'mean', 'lon': 'mean'}).reset_index()
        
#         # Calculate Efficiency (Load per Center)
#         state_agg['efficiency'] = state_agg['total_transactions'] / state_agg['active_pincodes']
        
#         med_load = state_agg['efficiency'].median()
#         max_vol = state_agg['total_transactions'].max()
        
#         for _, row in state_agg.iterrows():
#             rad = 6 + (row['total_transactions'] / max_vol * 35)
#             # High Efficiency = Cyan, Low Efficiency = Pink
#             col = COLOR_MAP['cyan'] if row['efficiency'] > med_load else COLOR_MAP['pink']
            
#             # CLEARER TOOLTIP
#             tooltip_html = f"""
#             <div style='font-family: sans-serif; font-size: 12px;'>
#                 <b>{row['state']}</b><br>
#                 Total Vol: {int(row['total_transactions']):,}<br>
#                 Active Centers: {int(row['active_pincodes']):,}<br>
#                 <hr style='margin: 3px 0;'>
#                 <b>Load: {int(row['efficiency']):,}</b> txns/center
#             </div>
#             """
            
#             folium.CircleMarker(
#                 [row['lat'], row['lon']], 
#                 radius=rad, color=col, fill=True, fill_color=col, fill_opacity=0.8, 
#                 popup=folium.Popup(tooltip_html, max_width=200)
#             ).add_to(m)

# elif view_mode == "2. District Grid":
#     if selected_state:
#         state_geo = filter_geojson(geojson, state_name=selected_state)
#         if state_geo: folium.GeoJson(state_geo, name=selected_state, style_function=style_slate).add_to(m)
#         d_data = df_dist[df_dist['state'] == selected_state]
#         if not d_data.empty:
#             m.fit_bounds([[d_data['lat'].min(), d_data['lon'].min()], [d_data['lat'].max(), d_data['lon'].max()]])
#             max_vol = d_data['total_transactions'].max()
#             for _, row in d_data.iterrows():
#                 col = COLOR_MAP['pink'] if row['active_pincodes'] < 15 else COLOR_MAP['cyan']
                
#                 tooltip_html = f"""
#                 <div style='font-family: sans-serif; font-size: 12px;'>
#                     <b>{row['district']}</b><br>
#                     Total Vol: {int(row['total_transactions']):,}<br>
#                     <b>Active Centers: {int(row['active_pincodes'])}</b>
#                 </div>
#                 """
                
#                 folium.CircleMarker(
#                     [row['lat'], row['lon']], 
#                     radius=5 + (row['total_transactions']/max_vol*20), 
#                     color=col, fill=True, fill_color=col, fill_opacity=0.7, 
#                     popup=folium.Popup(tooltip_html, max_width=200)
#                 ).add_to(m)

# elif view_mode == "3. Pincode Trace":
#     if selected_state and selected_dist:
#         dist_geo = filter_geojson(geojson, state_name=selected_state, district_name=selected_dist)
#         if not dist_geo: dist_geo = filter_geojson(geojson, state_name=selected_state)
#         if dist_geo: folium.GeoJson(dist_geo, name=selected_dist, style_function=style_slate).add_to(m)
#         p_data = df_pin[(df_pin['state'] == selected_state) & (df_pin['district'] == selected_dist)]
#         if not p_data.empty:
#             m.fit_bounds([[p_data['lat'].min(), p_data['lon'].min()], [p_data['lat'].max(), p_data['lon'].max()]])
#             for _, row in p_data.iterrows():
#                 col, rad, opa = COLOR_MAP['gold'], 3, 0.8
#                 type_label = "Standard"
#                 if row['archetype'] == 'Remote Node': 
#                     col, rad, opa = COLOR_MAP['pink'], 6, 1.0
#                     type_label = "Remote Node (Low Vol)"
#                 elif row['archetype'] == 'High Volume': 
#                     col, rad, opa = COLOR_MAP['cyan'], 7, 0.9
#                     type_label = "High Volume Hub"
                
#                 tooltip_html = f"""
#                 <div style='font-family: sans-serif; font-size: 12px;'>
#                     <b>PIN: {row['pincode']}</b><br>
#                     Vol: {int(row['total_transactions']):,}<br>
#                     Type: <b>{type_label}</b>
#                 </div>
#                 """
                
#                 folium.CircleMarker(
#                     [row['lat'], row['lon']], 
#                     radius=rad, color=col, fill=True, fill_color=col, fill_opacity=opa, 
#                     popup=folium.Popup(tooltip_html, max_width=200)
#                 ).add_to(m)

# st_folium(m, width="100%", height=600, returned_objects=[])

# with st.expander("ℹ️ How to read this Map"):
#     st.markdown("""
#     *   **The Slate Island:** The grey background represents official government boundaries. We do not color the map itself to avoid hiding empty areas (Survivorship Bias).
#     *   **What is 'Load'?**
#         *   It is the **Operational Efficiency** metric: `Total Transactions ÷ Active Centers`.
#         *   Example: If UP has a Load of 10,000, it means *each center* in UP processes ~10,000 requests on average. High load often implies crowded centers.
#     *   **The Colors:**
#         *   <span style='color:#00FFFF'>●</span> **High Intensity (Cyan):** Urban hubs or stressed infrastructure (High Volume / High Load).
#         *   <span style='color:#FF00AA'>●</span> **The Last Mile (Pink):** Remote nodes or areas with sparse infrastructure (Low Load / Low Count). These are priority targets for expansion.
#     """, unsafe_allow_html=True)

# # ==========================================
# # 2. SURGE ANALYSIS (UPDATED LOGIC)
# # ==========================================
# st.markdown("---")
# st.header("2. The Deadline Pulse Analysis")

# active_df = pd.DataFrame()
# group_col = ""

# if view_mode == "1. National Load (State)":
#     active_df = df_daily.copy()
#     group_col = "state"
# elif view_mode == "2. District Grid" and selected_state:
#     active_df = df_daily[df_daily['state'] == selected_state].copy()
#     group_col = "district"
# elif view_mode == "3. Pincode Trace" and selected_state and selected_dist:
#     active_df = df_pin_daily[(df_pin_daily['state'] == selected_state) & (df_pin_daily['district'] == selected_dist)].copy()
#     if not active_df.empty:
#         active_df['pincode'] = active_df['pincode'].astype(int).astype(str)
#     group_col = "pincode"

# if not active_df.empty:
#     active_df['date'] = pd.to_datetime(active_df['date'])
#     active_df['month'] = active_df['date'].dt.month
    
#     month_map = {3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
#     all_months = list(month_map.values())
#     m_nums = {name: num for num, name in month_map.items()}

#     c1, c2 = st.columns(2)
#     with c1: before = st.multiselect("Baseline (Normal Ops):", all_months, default=['Oct'])
#     with c2: after = st.multiselect("Comparison (Target):", all_months, default=['Nov'])

#     if before and after and group_col:
#         b_nums, a_nums = [m_nums[m] for m in before], [m_nums[m] for m in after]
#         grouped = active_df.groupby([group_col, 'month'])['total_demo'].sum().reset_index()
        
#         b_avg = grouped[grouped['month'].isin(b_nums)].groupby(group_col)['total_demo'].mean()
#         a_avg = grouped[grouped['month'].isin(a_nums)].groupby(group_col)['total_demo'].mean()
        
#         surge = pd.DataFrame({'after': a_avg, 'before': b_avg}).dropna()
        
#         # Calculate Pct Change
#         surge['pct'] = (((surge['after'] - surge['before']) / surge['before']) * 100).round(2)
#         surge = surge.replace([float('inf'), -float('inf')], 0)
        
#         # LOGIC CHANGE: Split Positive and Negative
#         pos_surge = surge[surge['pct'] > 0].sort_values('pct', ascending=True)
#         neg_surge = surge[surge['pct'] < 0].sort_values('pct', ascending=False) # Biggest drop first (e.g. -90% < -10%)
        
#         plot_data = pd.DataFrame()
#         chart_color = ""
#         trend_name = ""
        
#         # PRIORITY LOGIC: Show Positive if exists, else show Negative
#         if not pos_surge.empty:
#             plot_data = pos_surge.tail(20) # Top 20 Surges
#             chart_color = COLOR_MAP['cyan']
#             trend_name = "Surge (Positive)"
#             surge['Trend'] = "Surge" # Dummy for color map
#         elif not neg_surge.empty:
#             plot_data = neg_surge.tail(20) # Top 20 Drops (sorted ascending -> tail gives largest negative magnitude if we look at abs, but here we want most negative)
#             # Actually for negative, if we sort ascending (-100, -90, -10), tail gives (-20, -10). Head gives (-100, -90).
#             # We want to see the biggest drops (-100). So we use HEAD if sorted ascending.
#             # Let's fix the sort:
#             neg_surge_plot = surge[surge['pct'] < 0].sort_values('pct', ascending=True).head(20) # -100 at top
#             plot_data = neg_surge_plot
#             chart_color = COLOR_MAP['red']
#             trend_name = "Drop (Negative)"
#             surge['Trend'] = "Drop"
        
#         if not plot_data.empty:
#             # Color Mapping for the single trace
#             color_map_logic = {'Surge': COLOR_MAP['cyan'], 'Drop': COLOR_MAP['red']}
            
#             fig = px.bar(
#                 plot_data, x='pct', y=plot_data.index, orientation='h', 
#                 color_discrete_sequence=[chart_color],
#                 labels={'pct': 'Change (%)', 'index': group_col.title()}, text='pct'
#             )
            
#             fig.update_layout(
#                 height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', 
#                 font_color=COLOR_MAP['grey'], yaxis=dict(type='category'), showlegend=False
#             )
#             fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
#             fig.add_vline(x=0, line_width=1, line_color="#FFFFFF")
            
#             st.plotly_chart(fig, use_container_width=True)
            
#             if trend_name == "Surge (Positive)":
#                 st.caption("* Displaying **Top 20 Positive Surges**. (Negative drops are hidden when growth is detected).")
#             else:
#                 st.caption("📉 No growth detected. Displaying **Top 20 Negative Drops**.")
#         else:
#             st.info("No significant data changes found for this selection.")

# with st.expander("ℹ️ How to read Pulse Analysis"):
#     st.markdown("""
#     *   **The Metric:** Comparison of daily average volume between the 'Baseline' and 'Comparison' months.
#     *   **<span style='color:#00FFFF'>Cyan Bars (Surge):</span>** Growth in workload. Indicates deadline pressure, migration inflow, or campaign success.
#     *   **<span style='color:#FF4B4B'>Red Bars (Drop):</span>** Decline in workload. Indicates holidays, strikes, network outages, or migration outflow.
#     *   **Logic:** If there is any growth, we prioritize showing the **Surges**. If everything is falling, we show the **Drops**.
#     """, unsafe_allow_html=True)

# # ==========================================
# # 3. SEASONAL RHYTHM (UPDATED: LINE CHART)
# # ==========================================
# st.markdown("---")
# st.header("3. The Seasonal Rhythm")

# if not df_daily.empty:
#     rhythm_df = df_daily.copy()
#     if selected_state: rhythm_df = rhythm_df[rhythm_df['state'] == selected_state]
#     if selected_dist: rhythm_df = rhythm_df[rhythm_df['district'] == selected_dist]

#     if not rhythm_df.empty:
#         try: rhythm_df['m_str'] = rhythm_df['date'].dt.strftime('%b %Y')
#         except: pass
        
#         # Aggregate by Month
#         agg = rhythm_df.groupby(['m_str', rhythm_df['date'].dt.month])[['total_enrol', 'total_demo', 'total_bio']].sum().reset_index()
#         agg = agg.sort_values('date') # Sort chronologically
        
#         # Melt for Plotly
#         melt = agg.melt(id_vars='m_str', value_vars=['total_enrol', 'total_demo', 'total_bio'], var_name='Type', value_name='Volume')
#         melt['Type'] = melt['Type'].map({'total_enrol': 'Enrolment', 'total_demo': 'Demographic Update', 'total_bio': 'Biometric Update'})
        
#         colors = {'Enrolment': COLOR_MAP['cyan'], 'Demographic Update': COLOR_MAP['pink'], 'Biometric Update': COLOR_MAP['gold']}
        
#         c1, c2 = st.columns(2)
        
#         with c1:
#             st.subheader("Volume Trend (Lines)")
#             # CHANGED: px.bar -> px.line
#             fig1 = px.line(
#                 melt, 
#                 x='m_str', 
#                 y='Volume', 
#                 color='Type', 
#                 color_discrete_map=colors,
#                 markers=True # Dots on the line
#             )
#             fig1.update_layout(
#                 paper_bgcolor=COLOR_MAP['bg'], 
#                 plot_bgcolor='rgba(0,0,0,0)', 
#                 font_color=COLOR_MAP['grey'], 
#                 xaxis_title=None, 
#                 legend=dict(orientation="h", y=1.1, title=None)
#             )
#             # Make lines thicker
#             fig1.update_traces(line=dict(width=3), marker=dict(size=8))
#             st.plotly_chart(fig1, use_container_width=True)
            
#         with c2:
#             st.subheader("Workload Mix (Percentage)")
#             fig2 = px.area(
#                 melt, 
#                 x='m_str', 
#                 y='Volume', 
#                 color='Type', 
#                 groupnorm='percent', 
#                 color_discrete_map=colors
#             )
#             fig2.update_layout(
#                 paper_bgcolor=COLOR_MAP['bg'], 
#                 plot_bgcolor='rgba(0,0,0,0)', 
#                 font_color=COLOR_MAP['grey'], 
#                 xaxis_title=None, 
#                 yaxis_title="%", 
#                 legend=dict(orientation="h", y=1.1, title=None)
#             )
#             st.plotly_chart(fig2, use_container_width=True)

# with st.expander("ℹ️ How to read Seasonal Rhythm"):
#     st.markdown("""
#     *   **Left Chart (Trend):** Tracks the absolute volume over time. 
#         *   *Why Line?* It clearly shows the trajectory. If the <span style='color:#FF00AA'>**Pink Line**</span> shoots up while others stay flat, it indicates a specific rush for demographic updates.
#     *   **Right Chart (Mix):** Shows the *relative* distribution (Total = 100%).
#         *   *Insight:* Even if total volume drops, if the <span style='color:#FFD700'>**Gold Area**</span> expands, it means Biometrics are becoming the dominant task.
#     """, unsafe_allow_html=True)

# import streamlit as st
# import pandas as pd
# import duckdb
# import folium
# from streamlit_folium import st_folium
# import plotly.express as px
# import json

# st.set_page_config(page_title="Operational Audit", page_icon="🩺", layout="wide")

# # --- 🎨 DESIGN PIVOT: NEON NOIR ---
# COLOR_MAP = {
#     'bg': '#000000',           # Pure Black
#     'card': '#111111',         # Card Background
#     'cyan': '#00E5FF',         # Electric Cyan (Secondary)
#     'pink': '#FF00FF',         # Hot Magenta (Tertiary)
#     'gold': '#CCFF00',         # Neon Lime (Primary)
#     'grey': '#888888',         # Dimmed Text
#     'white': '#FFFFFF',        # Headers
#     'blue': '#2962FF',         # Deep Electric Blue
#     'red': '#FF5F1F',          # Neon Orange (Warning)
#     'slate': '#1E1E1E',        # Map Elements
#     'border': '#333333'        # Subtle borders
# }

# # Google Sans Alternative: 'Outfit'
# font_css = """
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

# .stApp { background-color: #000000; }

# /* Apply Font globally */
# html, body, [class*="css"], h1, h2, h3, h4, .stMarkdown, .stMetricLabel {
#     font-family: 'Outfit', sans-serif !important;
# }

# h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; letter-spacing: -0.5px; }
# div[data-testid="stMetricValue"] { color: #CCFF00 !important; font-weight: 600; }
# p, label, .stMarkdown { color: #B0B0B0 !important; }

# /* Sidebar Styling */
# section[data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #222; }
# .stSelectbox div[data-baseweb="select"] > div { background-color: #111; color: white; border-color: #333; }
# .stSelectbox div[data-baseweb="select"] > div:hover { border-color: #00E5FF; }

# /* Custom Legend Box */
# .legend-box { 
#     display: flex; gap: 20px; background-color: #111; padding: 12px; 
#     border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; align-items: center; 
# }
# .legend-item { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #EEE; }
# .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; box-shadow: 0 0 5px currentColor; }
# </style>
# """
# st.markdown(font_css, unsafe_allow_html=True)
# # ----------------------------------------

# @st.cache_data
# def load_data():
#     try:
#         with open('data/india_districts_simplified.geojson', encoding='utf-8') as f: geojson = json.load(f)
#         con = duckdb.connect('database/analytics.db', read_only=True)
#         df_dist = con.execute("SELECT * FROM dist_geo").fetchdf()
#         df_pin = con.execute("SELECT * FROM pin_geo").fetchdf()
#         df_daily = con.execute("SELECT * FROM district_daily").fetchdf()
#         df_pin_daily = con.execute("SELECT * FROM pincode_daily").fetchdf()
#         con.close()
#         if not df_dist.empty: df_dist['district'] = df_dist['district'].str.title()
#         if not df_daily.empty: df_daily['district'] = df_daily['district'].str.title()
#         return geojson, df_dist, df_pin, df_daily, df_pin_daily
#     except Exception as e: return None, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# geojson, df_dist, df_pin, df_daily, df_pin_daily = load_data()

# def filter_geojson(full_geojson, state_name=None, district_name=None):
#     if not full_geojson: return None
#     filtered = []
#     props = full_geojson['features'][0]['properties']
#     st_key = next((k for k in ['st_nm', 'state', 'STATE'] if k in props), 'st_nm')
#     dt_key = next((k for k in ['district', 'dtname', 'DISTRICT'] if k in props), 'district')
#     for f in full_geojson['features']:
#         p = f['properties']
#         if state_name and (state_name.lower() not in p.get(st_key, '').lower()): continue
#         if district_name and (district_name.lower() not in p.get(dt_key, '').lower()): continue
#         filtered.append(f)
#     return {"type": "FeatureCollection", "features": filtered} if filtered else None

# # --- SIDEBAR View Controller  ---
# with st.sidebar:
#     st.header("🔭 View Controller ")
#     view_mode = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (District)"])
    
#     selected_state, selected_dist = None, None
    
#     if view_mode in ["Mosaic (State)", "Tessera (District)"]:
#         states = sorted(df_dist['state'].unique()) if not df_dist.empty else []
#         selected_state = st.selectbox("Select State:", states)
        
#     if view_mode == "Tessera (District)":
#         dists = sorted(df_dist[df_dist['state'] == selected_state]['district'].unique()) if not df_dist.empty and selected_state else []
#         selected_dist = st.selectbox("Select District:", dists)

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


# # --- MAIN PAGE ---
# st.title("Operational Geoscanner")
# st.header("1. The Access Inequality Map")
# st.markdown("We are looking for where the centers are dangerously overcrowded and where people have to travel too far to find one.")

# # Legend
# st.markdown(f"""<div class="legend-box">
#     <div class="legend-item"><span class="dot" style="background:{COLOR_MAP['cyan']}"></span> <b>High Intensity</b></div>
#     <div class="legend-item"><span class="dot" style="background:{COLOR_MAP['pink']}"></span> <b>The Last Mile</b></div>
#     <div class="legend-item"><span class="dot" style="background:{COLOR_MAP['gold']}"></span> <b>Standard Ops</b></div>
# </div>""", unsafe_allow_html=True)

# # Map
# m = folium.Map(location=[22.5, 82.0], zoom_start=5, tiles=None)
# folium.TileLayer(tiles="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png", attr='CartoDB', name='Void', control=False).add_to(m)
# def style_slate(feature): return {'fillColor': COLOR_MAP['slate'], 'color': COLOR_MAP['border'], 'weight': 1, 'fillOpacity': 0.7}

# if view_mode == "Adamento (National)":
#     if geojson: folium.GeoJson(geojson, name="India", style_function=style_slate).add_to(m)
#     m.fit_bounds([[6.0, 68.0], [37.5, 97.5]])
#     if not df_dist.empty:
#         agg = df_dist.groupby('state').agg({'total_transactions':'sum','active_pincodes':'sum','lat':'mean','lon':'mean'}).reset_index()
#         med, mx = (agg['total_transactions']/agg['active_pincodes']).median(), agg['total_transactions'].max()
#         for _, r in agg.iterrows():
#             folium.CircleMarker([r['lat'],r['lon']], radius=6+(r['total_transactions']/mx*35), color=COLOR_MAP['cyan'] if (r['total_transactions']/r['active_pincodes'])>med else COLOR_MAP['pink'], fill=True, fill_opacity=0.8, popup=r['state']).add_to(m)

# elif view_mode == "Mosaic (State)" and selected_state:
#     geo = filter_geojson(geojson, state_name=selected_state)
#     if geo: folium.GeoJson(geo, style_function=style_slate).add_to(m)
#     d = df_dist[df_dist['state'] == selected_state]
#     if not d.empty:
#         m.fit_bounds([[d['lat'].min(), d['lon'].min()], [d['lat'].max(), d['lon'].max()]])
#         mx = d['total_transactions'].max()
#         for _, r in d.iterrows():
#             folium.CircleMarker([r['lat'],r['lon']], radius=5+(r['total_transactions']/mx*20), color=COLOR_MAP['pink'] if r['active_pincodes']<15 else COLOR_MAP['cyan'], fill=True, fill_opacity=0.7, popup=r['district']).add_to(m)

# elif view_mode == "Tessera (District)" and selected_dist:
#     geo = filter_geojson(geojson, state_name=selected_state, district_name=selected_dist)
#     if not geo: geo = filter_geojson(geojson, state_name=selected_state)
#     if geo: folium.GeoJson(geo, style_function=style_slate).add_to(m)
#     p = df_pin[(df_pin['state']==selected_state) & (df_pin['district']==selected_dist)]
#     if not p.empty:
#         m.fit_bounds([[p['lat'].min(), p['lon'].min()], [p['lat'].max(), p['lon'].max()]])
#         for _, r in p.iterrows():
#             col = COLOR_MAP['pink'] if r['archetype']=='Remote Node' else (COLOR_MAP['cyan'] if r['archetype']=='High Volume' else COLOR_MAP['gold'])
#             folium.CircleMarker([r['lat'],r['lon']], radius=4, color=col, fill=True, fill_opacity=0.9, popup=str(r['pincode'])).add_to(m)

# c1, c2, c3 = st.columns([1, 3, 1])

# with c2:
#     st_folium(m, width=800, height=600, returned_objects=[])

# with st.expander("ℹ️ How to read this Map: The Access Inequality"):
#     st.markdown("""
#     **Why are we asking this?** To find where centers are overcrowded vs. where they are missing.
    
#     **The Technique: Geospatial Density & Load Efficiency**
#     Think of this like a supermarket. We calculate **Load** by dividing the shoppers (Transactions) by the open checkout counters (Active Pincodes).
    
#     **Interpretation:**
#     *   **<span style='color:#00FFFF'>Cyan Areas (High Intensity):</span>** Urban Hubs. High volume, efficient, but potentially overcrowded.
#     *   **<span style='color:#FF00AA'>Pink Areas (Remote Node):</span>** The "Last Mile." Low volume and few centers. These are priority areas for inclusivity.
#     *   **<span style='color:#FFD700'>Gold Areas:</span>** Standard, balanced operations.
#     """, unsafe_allow_html=True)
# # --- Q2 PULSE ---
# st.markdown("---"); st.header("2. The Deadline Pulse Analysis")
# st.markdown("We are checking how much the workload suddenly jumps or drops due to government deadlines, festivals, or holidays.")
# # Logic: Filter dataframe based on Sidebar Selection
# active_df, group_col = pd.DataFrame(), ""
# if view_mode == "Adamento (National)": active_df, group_col = df_daily.copy(), "state"
# elif view_mode == "Mosaic (State)" and selected_state: active_df, group_col = df_daily[df_daily['state']==selected_state].copy(), "district"
# elif view_mode == "Tessera (District)" and selected_dist: 
#     active_df = df_pin_daily[(df_pin_daily['state']==selected_state)&(df_pin_daily['district']==selected_dist)].copy()
#     if not active_df.empty: active_df['pincode'] = active_df['pincode'].astype(int).astype(str)
#     group_col = "pincode"

# if not active_df.empty:
#     active_df['date'] = pd.to_datetime(active_df['date']); active_df['month'] = active_df['date'].dt.month
#     month_map = {3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
#     c1, c2 = st.columns(2)
#     with c1: before = st.multiselect("Baseline:", list(month_map.values()), default=['Oct'])
#     with c2: after = st.multiselect("Comparison:", list(month_map.values()), default=['Nov'])

#     if before and after and group_col:
#         m_nums = {name: num for num, name in month_map.items()}
#         b_nums, a_nums = [m_nums[m] for m in before], [m_nums[m] for m in after]
#         grouped = active_df.groupby([group_col, 'month'])['total_demo'].sum().reset_index()
#         b_avg = grouped[grouped['month'].isin(b_nums)].groupby(group_col)['total_demo'].mean()
#         a_avg = grouped[grouped['month'].isin(a_nums)].groupby(group_col)['total_demo'].mean()
        
#         surge = pd.DataFrame({'after': a_avg, 'before': b_avg}).fillna(0)
#         surge['pct'] = (((surge['after'] - surge['before']) / surge['before'].replace(0, 1)) * 100).round(2)
        
#         pos = surge[surge['pct']>0].sort_values('pct')
#         neg = surge[surge['pct']<0].sort_values('pct', ascending=False) # Biggest drop at bottom
        
#         # Priority Logic: Show Positive if present, else Negative
#         plot_data = pos.tail(20) if not pos.empty else neg.head(20).sort_values('pct', ascending=True) 
#         # Note: For negative, head(20) gives largest negative numbers (e.g. -100). Sorted ascending puts -100 at top.
        
#         color = COLOR_MAP['cyan'] if not pos.empty else COLOR_MAP['red']
        
#         if not plot_data.empty:
#             fig = px.bar(plot_data, x='pct', y=plot_data.index, orientation='h', color_discrete_sequence=[color], text='pct', labels={'pct':'Change (%)', 'index':group_col.title()})
#             fig.update_layout(height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'], yaxis={'type':'category'})
#             fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
#             st.plotly_chart(fig, use_container_width=True)
#             st.caption("🚀 Surges" if not pos.empty else "📉 Drops")
#         else: st.info("No significant changes.")

# with st.expander("ℹ️ How to read this Chart: The Deadline Pulse"):
#     st.markdown("""
#     **Why are we asking this?** To measure how government deadlines or holidays impact field workload.
    
#     **The Technique: Delta Analysis (Growth Rate)**
#     We compare the current workload against a "Baseline" average. It answers: "How much bigger or smaller is today's work compared to usual?"
    
#     **Interpretation:**
#     *   **<span style='color:#00FFFF'>Cyan Bar (Positive Surge):</span>** Workload increased significantly. Indicates a successful mobilization drive or migration inflow.
#     *   **<span style='color:#FF4B4B'>Red Bar (Negative Drop):</span>** Workload collapsed. Indicates server outages, holidays, or migration outflow.
#     """, unsafe_allow_html=True)
# # --- Q3 RHYTHM ---
# st.markdown("---"); st.header("3. The Seasonal Rhythm")
# st.markdown("We are analyzing how the workload composition shifts over months to understand operational focus.")
# if not df_daily.empty:
#     r = df_daily.copy()
#     if selected_state: r = r[r['state']==selected_state]
#     if selected_dist: r = r[r['district']==selected_dist]
#     if not r.empty:
#         try: r['m_str'] = r['date'].dt.strftime('%b %Y')
#         except: pass
#         agg = r.groupby(['m_str', r['date'].dt.month])[['total_enrol', 'total_demo', 'total_bio']].sum().reset_index().sort_values('date')
#         melt = agg.melt(id_vars='m_str', value_vars=['total_enrol', 'total_demo', 'total_bio'], var_name='Type', value_name='Volume')
#         melt['Type'] = melt['Type'].map({'total_enrol':'Enrolment','total_demo':'Demographic','total_bio':'Biometric'})
#         cols = {'Enrolment':COLOR_MAP['cyan'], 'Demographic':COLOR_MAP['pink'], 'Biometric':COLOR_MAP['gold']}
        
#         c1, c2 = st.columns(2)
#         with c1:
#             fig1 = px.line(melt, x='m_str', y='Volume', color='Type', color_discrete_map=cols, markers=True)
#             fig1.update_layout(xaxis_title='Months',paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'], legend=dict(orientation="h", y=1.1))
#             st.plotly_chart(fig1, use_container_width=True)
#         with c2:
#             fig2 = px.area(melt, x='m_str', y='Volume', color='Type', groupnorm='percent', color_discrete_map=cols)
#             fig2.update_layout(xaxis_title='Months',paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'], yaxis_title="%", legend=dict(orientation="h", y=1.1))
#             st.plotly_chart(fig2, use_container_width=True)

# with st.expander("ℹ️ How to read this Chart: The Seasonal Rhythm"):
#     st.markdown("""
#     **Why are we asking this?** To track if the work is shifting from Enrolments (New IDs) to Updates (Corrections).
    
#     **The Technique: Time-Series Decomposition**
#     We separate the data to see if a spike is a one-time event or a repeating seasonal pattern (like school admissions).
    
#     **Interpretation:**
#     *   **Line Chart:** Shows "Crunch Time" (peaks in total volume).
#     *   **Area Chart:** Shows the "Mix" of work.
#     *   **<span style='color:#FF00AA'>Pink Domination:</span>** If Pink (Demographics) takes over, the population is already enrolled. The strategy must shift to maintenance (updates) rather than new enrolment.
#     """, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import duckdb
import folium
from streamlit_folium import st_folium
import plotly.express as px
import json

st.set_page_config(page_title="Operational Audit", page_icon="🩺", layout="wide")

# --- 🎨 THEME: TRICOLOR INTELLIGENCE (Dark Mode) ---
COLOR_MAP = {
    'bg': '#050505',           # Deepest Black-Blue (Professional)
    'card': '#111111',         # Card Background
    'cyan': '#2979FF',         # Electric Blue (Replaces old Cyan) -> Technology
    'pink': '#FF9100',         # Neon Saffron (Replaces old Pink) -> Priority/Alerts
    'gold': '#00E676',         # Signal Green (Replaces old Lime) -> Success/Standard
    'red': '#FF3D00',          # High Contrast Red -> Critical Errors
    'grey': '#9E9E9E',         # Muted Text
    'white': '#FFFFFF',        # Headers
    'border': '#333333',       # Subtle borders
    'slate': '#1E1E1E'         # Map Geometry
}

# Font & Sidebar CSS
font_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

.stApp { background-color: #050505; }

/* Apply Font globally */
html, body, [class*="css"], h1, h2, h3, h4, .stMarkdown, .stMetricLabel {
    font-family: 'Outfit', sans-serif !important;
}

h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; letter-spacing: -0.5px; }
div[data-testid="stMetricValue"] { color: #2979FF !important; font-weight: 600; }
p, label, .stMarkdown { color: #9E9E9E !important; }

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

/* Custom Legend Box */
.legend-box { 
    display: flex; gap: 20px; background-color: #111; padding: 12px; 
    border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; align-items: center; 
}
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #EEE; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; box-shadow: 0 0 5px currentColor; }
</style>
"""
st.markdown(font_css, unsafe_allow_html=True)

# ----------------------------------------
# DATA LOADING
# ----------------------------------------
@st.cache_data
def load_data():
    try:
        with open('india_districts_simplified.geojson', encoding='utf-8') as f: geojson = json.load(f)
        con = duckdb.connect('database/analytics.db', read_only=True)
        df_dist = con.execute("SELECT * FROM dist_geo").fetchdf()
        df_pin = con.execute("SELECT * FROM pin_geo").fetchdf()
        df_daily = con.execute("SELECT * FROM district_daily").fetchdf()
        df_pin_daily = con.execute("SELECT * FROM pincode_daily").fetchdf()
        con.close()
        if not df_dist.empty: df_dist['district'] = df_dist['district'].str.title()
        if not df_daily.empty: df_daily['district'] = df_daily['district'].str.title()
        return geojson, df_dist, df_pin, df_daily, df_pin_daily
    except Exception as e: return None, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

geojson, df_dist, df_pin, df_daily, df_pin_daily = load_data()

def filter_geojson(full_geojson, state_name=None, district_name=None):
    if not full_geojson: return None
    filtered = []
    props = full_geojson['features'][0]['properties']
    st_key = next((k for k in ['st_nm', 'state', 'STATE'] if k in props), 'st_nm')
    dt_key = next((k for k in ['district', 'dtname', 'DISTRICT'] if k in props), 'district')
    for f in full_geojson['features']:
        p = f['properties']
        if state_name and (state_name.lower() not in p.get(st_key, '').lower()): continue
        if district_name and (district_name.lower() not in p.get(dt_key, '').lower()): continue
        filtered.append(f)
    return {"type": "FeatureCollection", "features": filtered} if filtered else None

# --- SIDEBAR CONTROLLER ---
with st.sidebar:
    st.header("🔭 View Controller")
    view_mode = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (District)"])
    
    selected_state, selected_dist = None, None
    
    if view_mode in ["Mosaic (State)", "Tessera (District)"]:
        states = sorted(df_dist['state'].unique()) if not df_dist.empty else []
        selected_state = st.selectbox("Select State:", states)
        
    if view_mode == "Tessera (District)":
        dists = sorted(df_dist[df_dist['state'] == selected_state]['district'].unique()) if not df_dist.empty and selected_state else []
        selected_dist = st.selectbox("Select District:", dists)

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

# --- MAIN PAGE ---
st.title("Operational Geoscanner")

# ----------------------------------------
# Q1: ACCESS INEQUALITY
# ----------------------------------------
st.header("1. The Access Inequality Map")
st.markdown("We are analyzing the geospatial distribution to identify **zones of infrastructure stress** versus **scarcity**.")
st.caption("We are looking for where the centers are dangerously overcrowded and where people have to travel too far to find one.")

# Legend
st.markdown(f"""<div class="legend-box">
    <div class="legend-item"><span class="dot" style="background:{COLOR_MAP['cyan']}"></span> <b>High Intensity Hubs</b></div>
    <div class="legend-item"><span class="dot" style="background:{COLOR_MAP['pink']}"></span> <b>Remote Nodes (Priority)</b></div>
    <div class="legend-item"><span class="dot" style="background:{COLOR_MAP['gold']}"></span> <b>Standard Operations</b></div>
</div>""", unsafe_allow_html=True)

# Map Logic
m = folium.Map(location=[22.5, 82.0], zoom_start=4.5, tiles=None)
folium.TileLayer(tiles="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png", attr='CartoDB', name='Void', control=False).add_to(m)

def style_slate(feature): return {'fillColor': COLOR_MAP['slate'], 'color': COLOR_MAP['border'], 'weight': 1, 'fillOpacity': 0.7}

if view_mode == "Adamento (National)":
    if geojson: folium.GeoJson(geojson, name="India", style_function=style_slate).add_to(m)
    m.fit_bounds([[6.0, 68.0], [37.5, 97.5]])
    if not df_dist.empty:
        agg = df_dist.groupby('state').agg({'total_transactions':'sum','active_pincodes':'sum','lat':'mean','lon':'mean'}).reset_index()
        med, mx = (agg['total_transactions']/agg['active_pincodes']).median(), agg['total_transactions'].max()
        for _, r in agg.iterrows():
            load_val = r['total_transactions']/r['active_pincodes']
            # Color Logic: High Load -> Blue (Cyan Key), Low Load -> Saffron (Pink Key)
            color = COLOR_MAP['cyan'] if load_val > med else COLOR_MAP['pink']
            folium.CircleMarker([r['lat'],r['lon']], radius=6+(r['total_transactions']/mx*35), color=color, fill=True, fill_opacity=0.8, popup=r['state']).add_to(m)

elif view_mode == "Mosaic (State)" and selected_state:
    geo = filter_geojson(geojson, state_name=selected_state)
    if geo: folium.GeoJson(geo, style_function=style_slate).add_to(m)
    d = df_dist[df_dist['state'] == selected_state]
    if not d.empty:
        m.fit_bounds([[d['lat'].min(), d['lon'].min()], [d['lat'].max(), d['lon'].max()]])
        mx = d['total_transactions'].max()
        for _, r in d.iterrows():
            color = COLOR_MAP['pink'] if r['active_pincodes'] < 15 else COLOR_MAP['cyan']
            folium.CircleMarker([r['lat'],r['lon']], radius=5+(r['total_transactions']/mx*20), color=color, fill=True, fill_opacity=0.7, popup=r['district']).add_to(m)

elif view_mode == "Tessera (District)" and selected_dist:
    geo = filter_geojson(geojson, state_name=selected_state, district_name=selected_dist)
    if not geo: geo = filter_geojson(geojson, state_name=selected_state)
    if geo: folium.GeoJson(geo, style_function=style_slate).add_to(m)
    p = df_pin[(df_pin['state']==selected_state) & (df_pin['district']==selected_dist)]
    if not p.empty:
        m.fit_bounds([[p['lat'].min(), p['lon'].min()], [p['lat'].max(), p['lon'].max()]])
        for _, r in p.iterrows():
            # Archetype Mapping
            col = COLOR_MAP['gold'] # Standard -> Green
            if r['archetype']=='Remote Node': col = COLOR_MAP['pink'] # Saffron
            elif r['archetype']=='High Volume': col = COLOR_MAP['cyan'] # Blue
            
            folium.CircleMarker([r['lat'],r['lon']], radius=4, color=col, fill=True, fill_opacity=0.9, popup=str(r['pincode'])).add_to(m)

# Square Layout
c1, c2, c3 = st.columns([1, 3, 1])
with c2:
    st_folium(m, width=700, height=700, returned_objects=[])

with st.expander("ℹ️ How to interpret the Access Inequality Map"):
    st.markdown(f"""
    **The Insight:**
    This geospatial model helps distinguish between areas of **high operational stress** (crowding) and **infrastructural voids** (scarcity).
    
    **The Technique: Geospatial Density & Load Efficiency**
    We calculate the 'Load Factor' by dividing Total Transactions by the count of Active Pincodes.
    
    **Visual Guide:**
    *   **<span style='color:{COLOR_MAP['cyan']}'>Electric Blue (High Intensity):</span>** Urban Hubs. High volume and efficiency, but potential risk of overcrowding.
    *   **<span style='color:{COLOR_MAP['pink']}'>Neon Saffron (Remote Node):</span>** The "Last Mile." Low transaction volume often correlates with scarce infrastructure. These are priority zones for inclusivity.
    *   **<span style='color:{COLOR_MAP['gold']}'>Signal Green (Standard):</span>** Balanced operations.
    """, unsafe_allow_html=True)

# ----------------------------------------
# Q2: DEADLINE PULSE
# ----------------------------------------
st.markdown("---")
st.header("2. The Deadline Pulse Analysis")
st.markdown("This module tracks **temporal volatility** driven by external mandates or calendar events.")
st.caption("We are checking how much the workload suddenly jumps or drops due to government deadlines, festivals, or holidays.")

active_df, group_col = pd.DataFrame(), ""
if view_mode == "Adamento (National)": active_df, group_col = df_daily.copy(), "state"
elif view_mode == "Mosaic (State)" and selected_state: active_df, group_col = df_daily[df_daily['state']==selected_state].copy(), "district"
elif view_mode == "Tessera (District)" and selected_dist: 
    active_df = df_pin_daily[(df_pin_daily['state']==selected_state)&(df_pin_daily['district']==selected_dist)].copy()
    if not active_df.empty: active_df['pincode'] = active_df['pincode'].astype(int).astype(str)
    group_col = "pincode"

if not active_df.empty:
    active_df['date'] = pd.to_datetime(active_df['date']); active_df['month'] = active_df['date'].dt.month
    month_map = {3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    c1, c2 = st.columns(2)
    with c1: before = st.multiselect("Baseline Period:", list(month_map.values()), default=['Oct'])
    with c2: after = st.multiselect("Comparison Period:", list(month_map.values()), default=['Nov'])

    if before and after and group_col:
        m_nums = {name: num for num, name in month_map.items()}
        b_nums, a_nums = [m_nums[m] for m in before], [m_nums[m] for m in after]
        grouped = active_df.groupby([group_col, 'month'])['total_demo'].sum().reset_index()
        b_avg = grouped[grouped['month'].isin(b_nums)].groupby(group_col)['total_demo'].mean()
        a_avg = grouped[grouped['month'].isin(a_nums)].groupby(group_col)['total_demo'].mean()
        
        surge = pd.DataFrame({'after': a_avg, 'before': b_avg}).fillna(0)
        surge['pct'] = (((surge['after'] - surge['before']) / surge['before'].replace(0, 1)) * 100).round(2)
        
        pos = surge[surge['pct']>0].sort_values('pct')
        neg = surge[surge['pct']<0].sort_values('pct', ascending=False)
        
        plot_data = pos.tail(20) if not pos.empty else neg.head(20).sort_values('pct', ascending=True)
        color = COLOR_MAP['cyan'] if not pos.empty else COLOR_MAP['red']
        
        if not plot_data.empty:
            fig = px.bar(plot_data, x='pct', y=plot_data.index, orientation='h', color_discrete_sequence=[color], text='pct', labels={'pct':'Growth Delta (%)', 'index':group_col.title()})
            fig.update_layout(height=500, paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'], yaxis={'type':'category'})
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("No statistically significant volatility detected.")

with st.expander("ℹ️ How to interpret the Deadline Pulse"):
    st.markdown(f"""
    **The Insight:**
    This chart isolates the impact of **external triggers** (deadlines, holidays) on field capacity.
    
    **The Technique: Delta Analysis (Growth Rate)**
    We calculate the percentage deviation of the current workload against a historical baseline.
    
    **Visual Guide:**
    *   **<span style='color:{COLOR_MAP['cyan']}'>Electric Blue (Positive Surge):</span>** Indicates successful mobilization or migration inflow.
    *   **<span style='color:{COLOR_MAP['red']}'>Red (Negative Drop):</span>** Indicates potential outages, holidays, or migration outflow.
    """, unsafe_allow_html=True)

# ----------------------------------------
# Q3: SEASONAL RHYTHM
# ----------------------------------------
st.markdown("---")
st.header("3. The Seasonal Rhythm")
st.markdown("We decompose the **transaction mix** to determine the operational maturity of the region.")
st.caption("We are analyzing if the current work is mostly making new IDs for people (Enrolment) or just fixing errors in old ones (Updates).")

if not df_daily.empty:
    r = df_daily.copy()
    if selected_state: r = r[r['state']==selected_state]
    if selected_dist: r = r[r['district']==selected_dist]
    if not r.empty:
        try: r['m_str'] = r['date'].dt.strftime('%b %Y')
        except: pass
        agg = r.groupby(['m_str', r['date'].dt.month])[['total_enrol', 'total_demo', 'total_bio']].sum().reset_index().sort_values('date')
        melt = agg.melt(id_vars='m_str', value_vars=['total_enrol', 'total_demo', 'total_bio'], var_name='Type', value_name='Volume')
        melt['Type'] = melt['Type'].map({'total_enrol':'Enrolment','total_demo':'Demographic','total_bio':'Biometric'})
        
        # Color Mapping: Enrol (Blue/Tech), Demo (Saffron/Priority), Bio (Green/Standard)
        cols = {'Enrolment':COLOR_MAP['cyan'], 'Demographic':COLOR_MAP['pink'], 'Biometric':COLOR_MAP['gold']}
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Absolute Volume")
            fig1 = px.line(melt, x='m_str', y='Volume', color='Type', color_discrete_map=cols, markers=True)
            fig1.update_layout(xaxis_title='Timeline', paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'], legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            st.subheader("Relative Mix")
            fig2 = px.area(melt, x='m_str', y='Volume', color='Type', groupnorm='percent', color_discrete_map=cols)
            fig2.update_layout(xaxis_title='Timeline', paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor='rgba(0,0,0,0)', font_color=COLOR_MAP['grey'], yaxis_title="Composition %", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig2, use_container_width=True)

with st.expander("ℹ️ How to interpret the Seasonal Rhythm"):
    st.markdown(f"""
    **The Insight:**
    This analysis reveals the **lifecycle stage** of the local population's identity data.
    
    **The Technique: Time-Series Decomposition**
    We separate the data into absolute volume (Peaks) and relative composition (Mix).
    
    **Visual Guide:**
    *   **Line Chart:** Identifying "Crunch Time" (peaks in total volume).
    *   **Area Chart (Mix):**
        *   If **<span style='color:{COLOR_MAP['pink']}'>Neon Saffron (Demographic Updates)</span>** dominates, the market is mature; strategies should shift to maintenance (Self-Service).
        *   If **<span style='color:{COLOR_MAP['cyan']}'>Electric Blue (Enrolments)</span>** dominates, the region requires active intervention (Camps).
    """, unsafe_allow_html=True)