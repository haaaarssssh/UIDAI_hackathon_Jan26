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
    # Added index=2 to default to Tessera (District)
    view_level = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (District)"], index=2)
    
    # Inside the Sidebar View Controller block
    selected_state, selected_dist = None, None
    
    # Logic to get the list (df name varies per file: df_dist, df_d, or df_dist)
    # Assuming standard df names from your files (df_dist/df_d)
    
    if view_level in ["Mosaic (State)", "Tessera (District)"]: 
        # Get list from your specific dataframe
        states = sorted(df_dist['state'].unique()) if 'df_dist' in locals() else sorted(df_dist['state'].unique())
        
        # Default to Maharashtra
        st_ix = states.index('Maharashtra') if 'Maharashtra' in states else 0
        selected_state = st.selectbox("Select State:", states, index=st_ix)
        
    if view_level == "Tessera (District)": 
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