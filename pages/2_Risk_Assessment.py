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
    # Note: Page 2 uses "Tessera (Pincode)"
    view_level = st.radio("Granularity:", ["Adamento (National)", "Mosaic (State)", "Tessera (Pincode)"], index=2)
    
    selected_state, selected_dist = None, None
    
    if view_level in ["Mosaic (State)", "Tessera (Pincode)"]:
        states = sorted(df_dist['state'].unique())
        
        # Default to Maharashtra
        st_ix = states.index('Maharashtra') if 'Maharashtra' in states else 0
        selected_state = st.selectbox("Select State:", states, index=st_ix)
        
    if view_level == "Tessera (Pincode)":
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
# FIX: Changed "Tessera (District)" to "Tessera (Pincode)" to match Radio Button
elif view_level == "Tessera (Pincode)" and selected_dist:
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