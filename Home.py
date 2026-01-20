# # Home.py

# import streamlit as st

# # --- PAGE CONFIGURATION ---
# # This must be the first Streamlit command in your script.
# st.set_page_config(
#     page_title="Aadhaar Insights Dashboard",
#     page_icon="🔑",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'About': "Dashboard for UIDAI Stakeholders. Analyzing Aadhaar operational data from March to December 2025."
#     }
# )

# # --- VISUAL STYLE GUIDE (Mandatory for consistency) ---
# COLOR_MAP = {
#     '--void-purple': '#0F001A',
#     '--toxic-cyan': '#00FFFF',
#     '--chrome-grey': '#B0B0B0',
# }
# css = f"""
# <style>
#     .stApp {{
#         background-color: {COLOR_MAP['--void-purple']};
#     }}
#     h1, h2, h3 {{
#         color: {COLOR_MAP['--toxic-cyan']};
#     }}
#     p, div, label, .st-emotion-cache-16idsys p, .st-emotion-cache-1aehpvj p {{
#         color: {COLOR_MAP['--chrome-grey']};
#     }}
#     .st-emotion-cache-1gulkj5 {{
#         border-top: 2px solid {COLOR_MAP['--toxic-cyan']};
#     }}
# </style>
# """
# st.markdown(css, unsafe_allow_html=True)

# # --- SIDEBAR ---
# with st.sidebar:
#     st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=100)
#     st.title("Navigation")
#     st.info("Select a page above to explore the analysis.")

# # --- MAIN PAGE CONTENT ---

# st.title("Unlocking Societal Trends in Aadhaar Enrolment and Updates")

# st.markdown("""
# This interactive dashboard provides a high-level analysis of pre-processed Aadhaar operational data, focusing on the period from **March to December 2025**. It is designed for UIDAI stakeholders to gain rapid, actionable insights into system performance, potential risks, and strategic opportunities.
# """)

# st.markdown("---")

# st.header("Guiding Principles")

# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("Brutal Clarity")
#     st.write("""
#     Every chart and metric is designed to provide direct, unambiguous, and honest insights. We avoid vanity metrics and focus on what truly matters for operational excellence and strategic decision-making.
#     """)

# with col2:
#     st.subheader("Zero Latency")
#     st.write("""
#     The application is designed for instantaneous response. All heavy computations, statistical modeling, and simulations have been performed in a one-time ETL pre-processing step. This dashboard only queries and visualizes the final, pre-calculated results.
#     """)

# st.markdown("---")

# st.header("Explore the Dashboard")

# st.write("Select a page from the sidebar to begin your analysis. Each page is designed to answer a specific set of strategic questions:")

# st.subheader("🩺 Operational Audit")
# st.markdown("""
# **Purpose:** To diagnose the health and stability of the Aadhaar system across the country.
# - **Key Questions:** Where are our operations most consistent and intense? How do external events impact user behavior? What are the natural seasonal rhythms of our workload?
# """)

# st.subheader("🎯 Risk Assessment")
# st.markdown("""
# **Purpose:** To proactively identify and flag potential data integrity risks and future operational bottlenecks.
# - **Key Questions:** Which districts show anomalous enrolment patterns that require investigation? Are any states trending towards exceeding their historical operational capacity? Where are the national hotspots for population churn?
# """)

# st.subheader("💡 Strategic Planner")
# st.markdown("""
# **Purpose:** To transform data-driven insights into actionable recommendations for resource allocation and targeted campaigns.
# - **Key Questions:** How can we classify districts to apply the right strategic focus? Where is the greatest untapped potential for child enrolment? What are fair and data-driven performance targets for a given district?
# """)
# import streamlit as st
# import pandas as pd
# import duckdb
# import plotly.graph_objects as go

# # --- PAGE CONFIG ---
# st.set_page_config(
#     page_title="Identity Ops: Neural Center",
#     page_icon="",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # --- 🎨 DESIGN PIVOT: NEON NOIR ---
# COLOR_MAP = {
#     'bg': '#000000',           
#     'cyan': '#00E5FF',         
#     'pink': '#FF00FF',         
#     'gold': '#CCFF00',         
#     'grey': '#888888',         
#     'tile_empty': '#1A1A1A',   
#     'border': '#333333',
#     'card_bg': '#0A0A0A'
# }

# # --- IN home.py ---

# font_css = """
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

# .stApp { background-color: #000000; }

# /* Global Typography */
# html, body, [class*="css"], h1, h2, h3, h4, .stMarkdown, .stMetricLabel, .stCaption {
#     font-family: 'Outfit', sans-serif !important;
# }

# h1 { color: #FFFFFF !important; font-weight: 700; letter-spacing: -1px; font-size: 2.5rem !important; }
# h2, h3 { color: #FFFFFF !important; font-weight: 600; }
# p, li { color: #B0B0B0 !important; line-height: 1.6; }
# strong { color: #CCFF00 !important; font-weight: 600; }

# /* Tabs Styling */
# .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #333; }
# .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; color: #888; }
# .stTabs [aria-selected="true"] { color: #CCFF00 !important; border-bottom: 2px solid #CCFF00 !important; }

# /* --- FORCE DARK SIDEBAR --- */
# section[data-testid="stSidebar"] {
#     background-color: #050505 !important; /* Forces Dark Background */
#     border-right: 1px solid #222 !important;
# }
# div[data-testid="stSidebarNav"] {
#     background-color: #050505 !important;
# }

# /* --- TEAM CARD STYLING --- */
# .team-card {
#     background-color: #0A0A0A;
#     border: 1px solid #333;
#     padding: 25px;
#     border-radius: 12px;
#     text-align: center;
#     height: 100%;
#     min-height: 320px;
#     display: flex;
#     flex-direction: column;
#     align-items: center;
#     justify-content: center;
#     transition: all 0.3s ease;
# }
# .team-card:hover { 
#     border-color: #00E5FF; 
#     box-shadow: 0 0 15px rgba(0, 229, 255, 0.1);
#     transform: translateY(-5px); 
# }
# .role-text { color: #00E5FF !important; font-size: 0.9rem; font-weight: 700; margin-top: 10px; letter-spacing: 1px; text-transform: uppercase; }
# .inst-text { color: #888 !important; font-size: 0.85rem; font-style: italic; margin-top: 5px; }

# /* --- TECH PILLS --- */
# .tech-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
# .tech-pill {
#     background-color: #111;
#     border: 1px solid #333;
#     color: #CCFF00;
#     padding: 5px 15px;
#     border-radius: 20px;
#     font-size: 0.8rem;
#     font-weight: 600;
# }

# /* --- PHILOSOPHY BOX --- */
# .philo-box {
#     background: linear-gradient(90deg, #0A0A0A 0%, #111 100%);
#     border-left: 4px solid #FF00FF;
#     padding: 20px;
#     border-radius: 0 10px 10px 0;
#     margin-bottom: 20px;
# }
# </style>
# """
# st.markdown(font_css, unsafe_allow_html=True)

# # --- SIDEBAR ---
# with st.sidebar:
#     st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=100)
#     st.title("Navigation")
#     st.info("Select a module above.")
    
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

# # --- DATA LOADER (Cached) ---
# @st.cache_data
# def load_home_data():
#     try:
#         con = duckdb.connect('database/analytics.db', read_only=True)
#         nat = con.execute("SELECT * FROM national_daily").fetchdf()
#         sta = con.execute("SELECT * FROM state_daily").fetchdf()
#         dis = con.execute("SELECT date, state, district, total_transactions FROM district_daily").fetchdf()
#         con.close()
#         for df in [nat, sta, dis]:
#             if not df.empty: df['date'] = pd.to_datetime(df['date'])
#         if not sta.empty: sta['state'] = sta['state'].str.title()
#         if not dis.empty: dis['state'] = dis['state'].str.title(); dis['district'] = dis['district'].str.title()
#         return nat, sta, dis
#     except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# df_nat, df_sta, df_dis = load_home_data()

# # --- HELPER: GITHUB WAFFLE CHART ---
# def plot_github_waffle(df, title_suffix=""):
#     start_date = pd.Timestamp("2025-02-24") 
#     end_date = pd.Timestamp("2026-01-04")
#     full_date_range = pd.date_range(start=start_date, end=end_date, freq='D')
#     skeleton = pd.DataFrame({'date': full_date_range})
    
#     if not df.empty:
#         df = df[(df['date'] >= "2025-03-01") & (df['date'] <= "2025-12-31")]
#         data_grouped = df.groupby('date')['total_transactions'].sum().reset_index()
#         merged = skeleton.merge(data_grouped, on='date', how='left').fillna(0)
#     else:
#         merged = skeleton; merged['total_transactions'] = 0

#     merged['WeekIndex'] = (merged['date'] - start_date).dt.days // 7
#     merged['DayOfWeek'] = merged['date'].dt.dayofweek
#     merged['Y_Coord'] = 6 - merged['DayOfWeek'] 
#     merged['Text'] = merged['date'].dt.strftime('%d %b') + ": " + merged['total_transactions'].astype(int).astype(str) + " Operations "

#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=merged['WeekIndex'], y=merged['Y_Coord'], mode='markers',
#         marker=dict(
#             symbol='square', size=12, color=merged['total_transactions'],
#             colorscale=[[0.0, COLOR_MAP['tile_empty']], [0.00001, '#004d40'], [1.0, COLOR_MAP['gold']]],
#             line=dict(color=COLOR_MAP['bg'], width=1), showscale=False
#         ),
#         text=merged['Text'], hoverinfo='text'
#     ))
#     fig.update_layout(
#         title=f"Activity Matrix {title_suffix}", title_font=dict(color=COLOR_MAP['grey'], size=14, family='Outfit'),
#         paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor=COLOR_MAP['bg'], height=180, margin=dict(t=40, l=40, b=20, r=20),
#         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
#         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True)
#     )
#     st.plotly_chart(fig, use_container_width=True)

# # ==========================================
# # 1. HERO SECTION
# # ==========================================
# st.title("Identity Ops: Neural Center")
# st.markdown("""
# <div style="font-size: 1.2rem; color: #A0A0A0; max-width: 800px; margin-bottom: 30px;">
#     Analyzing the heartbeat of the <strong>world's largest digital identity framework</strong>. 
#     This dashboard transforms a billion static data points into a living, breathing narrative of 
#     <span style="color:#00E5FF">Access</span>, <span style="color:#FF00FF">Inclusion</span>, and <span style="color:#CCFF00">Efficiency</span>.
# </div>
# """, unsafe_allow_html=True)

# # ==========================================
# # 2. DATA CALENDAR
# # ==========================================
# st.markdown("###  Aadhar Data Calendar (2025)")
# tab_nat, tab_sta, tab_dist = st.tabs(["🇮🇳 National View", "🏛️ State Mosaic", "🏙️ District Lens"])

# with tab_nat: plot_github_waffle(df_nat, "(All India)")
# with tab_sta:
#     if not df_sta.empty:
#         s = st.selectbox("Select State:", sorted(df_sta['state'].unique()))
#         plot_github_waffle(df_sta[df_sta['state'] == s], f"({s})")
# with tab_dist:
#     if not df_dis.empty:
#         c1, c2 = st.columns(2)
#         s_state = c1.selectbox("Filter State:", sorted(df_dis['state'].unique()), key="ds")
#         s_dist = c2.selectbox("Select District:", sorted(df_dis[df_dis['state']==s_state]['district'].unique()), key="dd")
#         plot_github_waffle(df_dis[(df_dis['state']==s_state)&(df_dis['district']==s_dist)], f"({s_dist})")

# st.markdown("---")

# # ==========================================
# # 3. PHILOSOPHY & TECH STACK
# # ==========================================
# col_phil, col_tech = st.columns([1.5, 1])

# with col_phil:
#     st.header(" Core Philosophy")
#     st.markdown("""
#     <div class="philo-box">
#         <strong>1. Beyond Aggregation:</strong> We don't just sum up numbers. We deconstruct them into granular signals (Pincodes & Days).<br><br>
#         <strong>2. The Last Mile First:</strong> Our algorithms prioritize the "Invisible" users—remote villages and excluded children—over high-volume metro cities.<br><br>
#         <strong>3. Probabilistic, Not Deterministic:</strong> We use statistical modeling (Z-Scores, Monte Carlo) to embrace the uncertainty of field operations rather than setting rigid, unfair targets.
#     </div>
#     """, unsafe_allow_html=True)

# with col_tech:
#     st.header(" Tech Stack")
#     st.markdown("""
#     <div class="tech-container">
#         <span class="tech-pill">Python 3.9</span>
#         <span class="tech-pill" style="border-color:#FF4B4B; color:#FF4B4B">Streamlit</span>
#         <span class="tech-pill" style="border-color:#00E5FF; color:#00E5FF">DuckDB (OLAP)</span>
#         <span class="tech-pill" style="border-color:#FF00FF; color:#FF00FF">Plotly Express</span>
#         <span class="tech-pill">Scikit-Learn</span>
#         <span class="tech-pill">Folium Geospatial</span>
#         <span class="tech-pill">Pandas / NumPy</span>
#     </div>
#     """, unsafe_allow_html=True)
#     st.caption("Built for high-performance, in-memory analytics without external server dependencies.")

# st.markdown("---")

# # ==========================================
# # 4. MEET THE ARCHITECTS
# # ==========================================
# st.header(" Meet the Architects")

# # Avatar URLs configured for descriptions
# # Harsh: Pale skin, Black hair, Short flat style
# harsh_url = "https://api.dicebear.com/9.x/notionists/svg?seed=Alexander"
# # Ashu: Tanned/Wheatish skin, Receding/High forehead (Caesar Side Part), Black hair
# ashu_url = "https://api.dicebear.com/9.x/lorelei/svg?seed=Nolan"

# col_team1, col_team2 = st.columns(2)

# with col_team1:
#     st.markdown(f"""
#     <div class="team-card">
#         <img src="{harsh_url}" style="width:120px; height:120px; border-radius:50%; border:3px solid #333; margin-bottom:15px;">
#         <h3 style="margin:0; color:white; font-size:1.4rem;">Harsh N. Patil</h3>
#         <div class="role-text">Team Lead & Strategist</div>
#         <div class="inst-text">BS in Data Science, IIT Madras</div>
#     </div>
#     """, unsafe_allow_html=True)

# with col_team2:
#     st.markdown(f"""
#     <div class="team-card">
#         <img src="{ashu_url}" style="width:120px; height:120px; border-radius:50%; border:3px solid #333; margin-bottom:15px;">
#         <h3 style="margin:0; color:white; font-size:1.4rem;">Ashitosh K. Jagtap</h3>
#         <div class="role-text">Full Stack Developer</div>
#         <div class="inst-text">BS in Data Science, IIT Madras</div>
#     </div>
#     """, unsafe_allow_html=True)

# st.markdown("<br><br>", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import duckdb
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Identity Ops: Neural Center",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🎨 THEME: TRICOLOR INTELLIGENCE (Dark Mode) ---
COLOR_MAP = {
    'bg': '#050505',           # Deepest Black-Blue
    'card': '#111111',         # Card Background
    'cyan': '#2979FF',         # Electric Blue (Technology/Core)
    'pink': '#FF9100',         # Neon Saffron (Priority/Strategy)
    'gold': '#00E676',         # Signal Green (Success/Activity)
    'grey': '#9E9E9E',         # Muted Text
    'tile_empty': '#1A1A1A',   # Empty Tile
    'border': '#333333'        # Subtle Border
}

font_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

.stApp {{ background-color: {COLOR_MAP['bg']}; }}

/* Global Typography */
html, body, [class*="css"], h1, h2, h3, h4, .stMarkdown, .stMetricLabel, .stCaption {{
    font-family: 'Outfit', sans-serif !important;
}}

h1 {{ color: #FFFFFF !important; font-weight: 700; letter-spacing: -1px; font-size: 2.5rem !important; }}
h2, h3 {{ color: #FFFFFF !important; font-weight: 600; }}
p, li {{ color: {COLOR_MAP['grey']} !important; line-height: 1.6; }}
strong {{ color: {COLOR_MAP['cyan']} !important; font-weight: 600; }}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {{ gap: 24px; border-bottom: 1px solid #333; }}
.stTabs [data-baseweb="tab"] {{ background-color: transparent; border: none; color: #888; }}
.stTabs [aria-selected="true"] {{ color: {COLOR_MAP['cyan']} !important; border-bottom: 2px solid {COLOR_MAP['cyan']} !important; }}

/* --- FORCE DARK SIDEBAR --- */
section[data-testid="stSidebar"] {{
    background-color: #050505 !important;
    border-right: 1px solid #222 !important;
}}
div[data-testid="stSidebarNav"] {{
    background-color: #050505 !important;
}}

/* --- TEAM CARD STYLING --- */
.team-card {{
    background-color: #0A0A0A;
    border: 1px solid #333;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    height: 100%;
    min-height: 320px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}}
.team-card:hover {{ 
    border-color: {COLOR_MAP['cyan']}; 
    box-shadow: 0 0 15px rgba(41, 121, 255, 0.2);
    transform: translateY(-5px); 
}}
.role-text {{ color: {COLOR_MAP['cyan']} !important; font-size: 0.9rem; font-weight: 700; margin-top: 10px; letter-spacing: 1px; text-transform: uppercase; }}
.inst-text {{ color: #888 !important; font-size: 0.85rem; font-style: italic; margin-top: 5px; }}

/* --- TECH PILLS --- */
.tech-container {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }}
.tech-pill {{
    background-color: #111;
    border: 1px solid #333;
    color: #EEE;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}}

/* --- PHILOSOPHY BOX --- */
.philo-box {{
    background: linear-gradient(90deg, #0A0A0A 0%, #111 100%);
    border-left: 4px solid {COLOR_MAP['pink']};
    padding: 20px;
    border-radius: 0 10px 10px 0;
    margin-bottom: 20px;
}}
</style>
"""
st.markdown(font_css, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=100)
    st.title("Navigation")
    st.info("Select a module above.")
    
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

# --- DATA LOADER (Cached) ---
@st.cache_data
def load_home_data():
    try:
        con = duckdb.connect('database/analytics.db', read_only=True)
        nat = con.execute("SELECT * FROM national_daily").fetchdf()
        sta = con.execute("SELECT * FROM state_daily").fetchdf()
        dis = con.execute("SELECT date, state, district, total_transactions FROM district_daily").fetchdf()
        con.close()
        for df in [nat, sta, dis]:
            if not df.empty: df['date'] = pd.to_datetime(df['date'])
        if not sta.empty: sta['state'] = sta['state'].str.title()
        if not dis.empty: dis['state'] = dis['state'].str.title(); dis['district'] = dis['district'].str.title()
        return nat, sta, dis
    except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_nat, df_sta, df_dis = load_home_data()

# --- HELPER: GITHUB WAFFLE CHART ---
def plot_github_waffle(df, title_suffix=""):
    start_date = pd.Timestamp("2025-02-24") 
    end_date = pd.Timestamp("2026-01-04")
    full_date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    skeleton = pd.DataFrame({'date': full_date_range})
    
    if not df.empty:
        df = df[(df['date'] >= "2025-03-01") & (df['date'] <= "2025-12-31")]
        data_grouped = df.groupby('date')['total_transactions'].sum().reset_index()
        merged = skeleton.merge(data_grouped, on='date', how='left').fillna(0)
    else:
        merged = skeleton; merged['total_transactions'] = 0

    merged['WeekIndex'] = (merged['date'] - start_date).dt.days // 7
    merged['DayOfWeek'] = merged['date'].dt.dayofweek
    merged['Y_Coord'] = 6 - merged['DayOfWeek'] 
    merged['Text'] = merged['date'].dt.strftime('%d %b') + ": " + merged['total_transactions'].astype(int).astype(str) + " Operations "

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=merged['WeekIndex'], y=merged['Y_Coord'], mode='markers',
        marker=dict(
            symbol='square', size=12, color=merged['total_transactions'],
            # Tricolor Scale: Dark -> Green (Success/Activity)
            colorscale=[[0.0, COLOR_MAP['tile_empty']], [0.00001, '#004d40'], [1.0, COLOR_MAP['gold']]],
            line=dict(color=COLOR_MAP['bg'], width=1), showscale=False
        ),
        text=merged['Text'], hoverinfo='text'
    ))
    fig.update_layout(
        title=f"Activity Matrix {title_suffix}", title_font=dict(color=COLOR_MAP['grey'], size=14, family='Outfit'),
        paper_bgcolor=COLOR_MAP['bg'], plot_bgcolor=COLOR_MAP['bg'], height=180, margin=dict(t=40, l=40, b=20, r=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True)
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 1. HERO SECTION
# ==========================================
st.title("Identity Ops: Neural Center")
st.markdown(f"""
<div style="font-size: 1.2rem; color: #A0A0A0; max-width: 800px; margin-bottom: 30px;">
    Analyzing the heartbeat of the <strong>world's largest digital identity framework</strong>. 
    This dashboard transforms a billion static data points into a living, breathing narrative of 
    <span style="color:{COLOR_MAP['cyan']}">Access</span>, <span style="color:{COLOR_MAP['pink']}">Inclusion</span>, and <span style="color:{COLOR_MAP['gold']}">Efficiency</span>.
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA CALENDAR
# ==========================================
st.markdown("###  Aadhaar Data Calendar (2025)")
tab_nat, tab_sta, tab_dist = st.tabs(["🇮🇳 National View", "🏛️ State Mosaic", "🏙️ District Lens"])

with tab_nat: plot_github_waffle(df_nat, "(All India)")
with tab_sta:
    if not df_sta.empty:
        s = st.selectbox("Select State:", sorted(df_sta['state'].unique()))
        plot_github_waffle(df_sta[df_sta['state'] == s], f"({s})")
with tab_dist:
    if not df_dis.empty:
        c1, c2 = st.columns(2)
        s_state = c1.selectbox("Filter State:", sorted(df_dis['state'].unique()), key="ds")
        s_dist = c2.selectbox("Select District:", sorted(df_dis[df_dis['state']==s_state]['district'].unique()), key="dd")
        plot_github_waffle(df_dis[(df_dis['state']==s_state)&(df_dis['district']==s_dist)], f"({s_dist})")

st.markdown("---")

# ==========================================
# 3. PHILOSOPHY & TECH STACK
# ==========================================
col_phil, col_tech = st.columns([1.5, 1])

with col_phil:
    st.header(" Core Philosophy")
    st.markdown("""
    <div class="philo-box">
        <strong>1. Beyond Aggregation:</strong> We don't just sum up numbers. We deconstruct them into granular signals (Pincodes & Days) to find the truth.<br><br>
        <strong>2. The Last Mile First:</strong> Our algorithms prioritize the "Invisible" users—remote villages and excluded children—over high-volume metro cities.<br><br>
        <strong>3. Probabilistic, Not Deterministic:</strong> We use statistical modeling (Z-Scores, Monte Carlo) to embrace the uncertainty of field operations rather than setting rigid, unfair targets.
    </div>
    """, unsafe_allow_html=True)

with col_tech:
    st.header(" Tech Stack")
    st.markdown(f"""
    <div class="tech-container">
        <span class="tech-pill" style="border-color:{COLOR_MAP['cyan']}; color:{COLOR_MAP['cyan']}">Python 3.9</span>
        <span class="tech-pill" style="border-color:{COLOR_MAP['pink']}; color:{COLOR_MAP['pink']}">Streamlit</span>
        <span class="tech-pill" style="border-color:{COLOR_MAP['gold']}; color:{COLOR_MAP['gold']}">DuckDB (OLAP)</span>
        <span class="tech-pill" style="border-color:{COLOR_MAP['cyan']}; color:{COLOR_MAP['cyan']}">Plotly Express</span>
        <span class="tech-pill" style="color:#FFF">Scikit-Learn</span>
        <span class="tech-pill" style="color:#FFF">Folium Geospatial</span>
        <span class="tech-pill" style="color:#FFF">Pandas / NumPy</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Built for high-performance, in-memory analytics without external server dependencies.")

st.markdown("---")

# ==========================================
# 4. MEET THE ARCHITECTS
# ==========================================
st.header(" Meet the Architects")

# Avatar URLs
harsh_url = "https://api.dicebear.com/9.x/notionists/svg?seed=Alexander"
ashu_url = "https://api.dicebear.com/9.x/lorelei/svg?seed=Nolan"

col_team1, col_team2 = st.columns(2)

with col_team1:
    st.markdown(f"""
    <div class="team-card">
        <img src="{harsh_url}" style="width:120px; height:120px; border-radius:50%; border:3px solid #333; margin-bottom:15px;">
        <h3 style="margin:0; color:white; font-size:1.4rem;">Harsh N. Patil</h3>
        <div class="role-text" style="color:{COLOR_MAP['pink']} !important">Team Lead & Strategist</div>
        <div class="inst-text">BS in Data Science, IIT Madras</div>
    </div>
    """, unsafe_allow_html=True)

with col_team2:
    st.markdown(f"""
    <div class="team-card">
        <img src="{ashu_url}" style="width:120px; height:120px; border-radius:50%; border:3px solid #333; margin-bottom:15px;">
        <h3 style="margin:0; color:white; font-size:1.4rem;">Ashitosh K. Jagtap</h3>
        <div class="role-text" style="color:{COLOR_MAP['cyan']} !important">Full Stack Developer</div>
        <div class="inst-text">BS in Data Science, IIT Madras</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)