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
    'bg': '#050505',           # Deepest Black-Blue
    'card': '#111111',         # Card Background
    'cyan': '#2979FF',         # Electric Blue
    'pink': '#FF9100',         # Neon Saffron
    'gold': '#00E676',         # Signal Green
    'red': '#FF3D00',          # High Contrast Red
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
        with open('data/india_districts_simplified.geojson', encoding='utf-8') as f: geojson = json.load(f)
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
    # Added index=2 to default to "Tessera (District)"
    view_mode = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (District)"], index=2)
    
    selected_state, selected_dist = None, None
    
    # Defaults: Maharashtra -> Jalgaon
    if view_mode in ["Mosaic (State)", "Tessera (District)"]: 
        states = sorted(df_dist['state'].unique()) if not df_dist.empty else []
        st_ix = states.index('Maharashtra') if 'Maharashtra' in states else 0
        selected_state = st.selectbox("Select State:", states, index=st_ix)
        
    if view_mode == "Tessera (District)":
        dists = sorted(df_dist[df_dist['state'] == selected_state]['district'].unique()) if not df_dist.empty and selected_state else []
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
            col = COLOR_MAP['gold']
            if r['archetype']=='Remote Node': col = COLOR_MAP['pink']
            elif r['archetype']=='High Volume': col = COLOR_MAP['cyan']
            folium.CircleMarker([r['lat'],r['lon']], radius=4, color=col, fill=True, fill_opacity=0.9, popup=str(r['pincode'])).add_to(m)

# Square Layout
c1, c2, c3 = st.columns([1, 3, 1])
with c2:
    st_folium(m, width=700, height=700, returned_objects=[])

with st.expander("ℹ️ How to interpret the Access Inequality Map"):
    st.markdown(f"""
    **The Insight:**
    This geospatial model helps distinguish between areas of **high operational stress** (crowding) and **infrastructural voids** (scarcity).
    
    **Visual Guide:**
    *   **<span style='color:{COLOR_MAP['cyan']}'>Electric Blue (High Intensity):</span>** Urban Hubs.
    *   **<span style='color:{COLOR_MAP['pink']}'>Neon Saffron (Remote Node):</span>** The "Last Mile" (Priority).
    *   **<span style='color:{COLOR_MAP['gold']}'>Signal Green (Standard):</span>** Balanced.
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
    
    **Visual Guide:**
    *   **Line Chart:** Identifying "Crunch Time" (peaks in total volume).
    *   **Area Chart (Mix):**
        *   If **<span style='color:{COLOR_MAP['pink']}'>Neon Saffron (Demographic Updates)</span>** dominates, the market is mature.
        *   If **<span style='color:{COLOR_MAP['cyan']}'>Electric Blue (Enrolments)</span>** dominates, the region requires active intervention.
    """, unsafe_allow_html=True)