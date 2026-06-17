import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Plastics Pollution Explorer",
    page_icon="🌊", layout="wide",
    initial_sidebar_state="expanded",
)

from filters import load_data, apply_filters, get_kpi_stats, get_country_totals, get_top_polluters
from charts import (
    chart_pie, chart_histogram, chart_line, chart_bar,
    chart_box, chart_scatter, chart_heatmap, chart_area,
    chart_countplot, chart_violin, chart_top_companies,
    chart_volunteers, chart_plastic_compare, chart_country_pie,
    chart_events, chart_efficiency, chart_nested_donut,
)
from image_cards import make_info_cards

# ════════════════════════════════════════════════════════════════
#  GLOBAL CSS — Sky-blue theme
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html,body,[class*="css"],.stApp{
  font-family:'Inter',sans-serif!important;
  background:#F0F8FF!important;
  color:#0A1628!important;
}
.main .block-container{
  background:transparent!important;
  padding:1.2rem 2.5rem 4rem!important;
  max-width:1500px!important;
}

/* ── SIDEBAR ──────────────────────────────────────────────────── */
[data-testid="stSidebar"]{
  background:#FFFFFF!important;
  border-right:2px solid #BFD7ED!important;
}
[data-testid="stSidebar"] *{ color:#0A1628!important; }
[data-testid="stSidebar"] [data-baseweb="select"]>div,
[data-testid="stSidebar"] [data-baseweb="input"] input{
  background:#F0F8FF!important;
  border:1.5px solid #90C4E4!important;
  border-radius:9px!important;
  color:#0A1628!important;
}
[data-testid="stSidebar"] [data-baseweb="tag"]{
  background:rgba(0,119,182,0.12)!important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span{
  color:#0077B6!important; font-weight:600!important;
}

/* ── BUTTONS ─────────────────────────────────────────────────── */
.stButton>button{
  background:linear-gradient(135deg,#0077B6,#00B4D8)!important;
  color:#fff!important; border:none!important;
  border-radius:11px!important; font-weight:700!important;
  font-size:13px!important; padding:10px 0!important;
  width:100%!important;
  box-shadow:0 4px 14px rgba(0,119,182,0.28)!important;
  transition:all 0.2s!important;
}
.stButton>button:hover{
  filter:brightness(1.1)!important;
  transform:translateY(-2px)!important;
}
.stDownloadButton>button{
  background:#0077B6!important; color:#fff!important;
  border:none!important; border-radius:10px!important;
  font-weight:600!important; font-size:13px!important;
  padding:9px 0!important; width:100%!important;
}

/* ── HERO ────────────────────────────────────────────────────── */
.hero{
  background:linear-gradient(135deg,#012A4A 0%,#01497C 50%,#014F86 100%);
  border-radius:22px; padding:44px 52px 40px;
  margin-bottom:28px; position:relative; overflow:hidden;
  box-shadow:0 10px 42px rgba(0,40,90,0.22);
}
.hero::after{
  content:'🌊'; position:absolute; right:52px; top:50%;
  transform:translateY(-50%); font-size:100px; opacity:0.08;
}
.hero-eyebrow{
  font-family:'Space Mono',monospace; font-size:10px;
  letter-spacing:3px; color:rgba(72,202,228,0.90);
  text-transform:uppercase; margin-bottom:14px;
}
.hero-title{
  font-size:46px; font-weight:800; line-height:1.12;
  margin:0 0 12px;
  color:#FFFFFF;
  text-shadow:0 2px 18px rgba(0,0,0,0.40);
}
.hero-title em{
  color:#48CAE4; font-style:normal;
  text-shadow:0 0 28px rgba(72,202,228,0.55);
}
.hero-sub{
  font-size:15px; color:rgba(255,255,255,0.78);
  line-height:1.7; max-width:620px;
}
.hero-sub strong{ color:#FFFFFF; }
.hero-chips{ display:flex; gap:8px; flex-wrap:wrap; margin-top:22px; }
.hero-chip{
  background:rgba(255,255,255,0.10);
  border:1px solid rgba(255,255,255,0.22);
  border-radius:30px; padding:5px 15px;
  font-size:11px; color:rgba(255,255,255,0.88); font-weight:500;
}

/* ── KPI CARDS ───────────────────────────────────────────────── */
.kpi-row{ display:flex; gap:14px; margin-bottom:24px; flex-wrap:wrap; }
.kpi-card{
  flex:1; min-width:130px; background:#FFFFFF;
  border-radius:18px; padding:18px 16px 14px;
  border:1.5px solid #BFD7ED;
  box-shadow:0 2px 14px rgba(0,80,160,0.07);
  position:relative; overflow:hidden;
  transition:transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover{
  transform:translateY(-3px);
  box-shadow:0 8px 28px rgba(0,80,160,0.12);
}
.kpi-bar{
  position:absolute; top:0; left:0; right:0;
  height:3px; background:var(--kc);
  border-radius:18px 18px 0 0;
}
.kpi-icon{ font-size:22px; display:block; margin-bottom:7px; }
.kpi-val{
  font-family:'Space Mono',monospace;
  font-size:19px; font-weight:700; color:var(--kc);
  display:block; margin-bottom:5px;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.kpi-label{
  font-size:9.5px; font-weight:700;
  letter-spacing:1.5px; text-transform:uppercase; color:#8A8A8A;
}

/* ── METRICS ROW ─────────────────────────────────────────────── */
[data-testid="stMetric"]{
  background:#FFFFFF; border:1.5px solid #BFD7ED;
  border-radius:14px; padding:14px 18px!important;
  box-shadow:0 1px 8px rgba(0,80,160,0.06);
}
[data-testid="stMetricLabel"]{ font-size:11px!important; color:#8A8A8A!important; font-weight:700!important; }
[data-testid="stMetricValue"]{ font-family:'Space Mono',monospace!important; color:#0077B6!important; }
[data-testid="stMetricDelta"]{ font-size:11px!important; }

/* ── TABS ────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"]{
  background:#FFFFFF; border-radius:14px; padding:5px;
  border:1.5px solid #BFD7ED; gap:4px;
}
[data-testid="stTabs"] [role="tab"]{
  border-radius:10px!important; font-weight:600!important;
  font-size:13px!important; color:#4A6FA5!important;
  padding:7px 18px!important; transition:all 0.18s!important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{
  background:#0077B6!important; color:#FFFFFF!important;
  box-shadow:0 3px 10px rgba(0,119,182,0.28)!important;
}

/* ── EXPANDERS ───────────────────────────────────────────────── */
[data-testid="stExpander"]{
  background:#FFFFFF!important;
  border:1.5px solid #BFD7ED!important;
  border-radius:14px!important;
  box-shadow:0 1px 8px rgba(0,80,160,0.05)!important;
  margin-bottom:8px!important;
}
[data-testid="stExpander"] summary{
  font-weight:700!important; color:#0077B6!important;
  font-size:14px!important; padding:12px 16px!important;
}
[data-testid="stExpander"] summary:hover{
  background:#F0F8FF!important; border-radius:12px!important;
}
details[data-testid="stExpander"] > summary > span{
  color:#0077B6!important; font-weight:700!important;
}

/* ── SECTION HEADERS ─────────────────────────────────────────── */
.sec-wrap{
  display:flex; align-items:center; gap:12px;
  margin:24px 0 10px; padding-bottom:10px;
  border-bottom:2px solid #BFD7ED; flex-wrap:wrap;
}
.sec-badge{
  font-family:'Space Mono',monospace;
  font-size:10px; font-weight:700;
  background:#0077B6; color:#fff;
  border-radius:7px; padding:3px 11px; letter-spacing:0.8px;
}
.sec-title{ font-size:15px; font-weight:800; color:#0A1628; }
.chip{ font-size:9px; font-weight:700; padding:2px 9px; border-radius:20px; letter-spacing:0.3px; }
.cg{ background:#E1F5FE; color:#0077B6; border:1.5px solid #81D4FA; }
.cr{ background:#FFEBEE; color:#C62828; border:1.5px solid #EF9A9A; }
.cb{ background:#E8EAF6; color:#1565C0; border:1.5px solid #9FA8DA; }
.co{ background:#FFF3E0; color:#E65100; border:1.5px solid #FFCC80; }
.cp{ background:#F3E5F5; color:#7B2FBE; border:1.5px solid #CE93D8; }
.ct{ background:#E0F7FA; color:#0096C7; border:1.5px solid #80DEEA; }

/* ── CALLOUTS ────────────────────────────────────────────────── */
.insight{
  background:#FFFFFF; border-radius:12px;
  border:1.5px solid #BFD7ED;
  border-left:4px solid #0096C7;
  padding:11px 16px; margin:8px 0 4px;
  font-size:13.5px; color:#0A1628; line-height:1.65;
  box-shadow:0 1px 8px rgba(0,80,160,0.04);
}
.insight strong{ color:#0077B6; }
.note{
  background:#FFF8E1; border-radius:11px;
  border:1.5px solid #FFB300;
  border-left:4px solid #FFB300;
  padding:10px 16px; margin:8px 0;
  font-size:13px; color:#3E2800; line-height:1.6;
}

/* ── INFO CARDS ──────────────────────────────────────────────── */
.info-card{
  background:#FFFFFF; border-radius:16px;
  border:1.5px solid #BFD7ED;
  overflow:hidden;
  box-shadow:0 3px 14px rgba(0,80,160,0.08);
  transition:transform 0.2s;
}
.info-card:hover{ transform:translateY(-3px); }
.info-card img{ width:100%; display:block; border-radius:14px 14px 0 0; }
.info-body{ padding:10px 13px 12px; }
.info-title{ font-size:12px; font-weight:700; color:#0A1628; margin-bottom:2px; }
.info-sub{ font-size:11px; color:#4A6FA5; line-height:1.45; }

/* ── STAT PILLS ──────────────────────────────────────────────── */
.stat-row{ display:flex; gap:12px; flex-wrap:wrap; margin:10px 0 18px; }
.stat-pill{
  flex:1; min-width:130px; background:#FFFFFF;
  border-radius:13px; border:1.5px solid #BFD7ED;
  padding:13px 14px; text-align:center;
  box-shadow:0 1px 8px rgba(0,80,160,0.05);
}
.sp-val{
  font-family:'Space Mono',monospace;
  font-size:16px; font-weight:700; color:#0077B6;
  display:block; margin-bottom:3px;
}
.sp-lab{ font-size:10px; color:#8A8A8A; font-weight:600; }

/* ── CHART FRAMES ────────────────────────────────────────────── */
[data-testid="stImage"] img{
  border-radius:14px!important; width:100%!important;
  border:1.5px solid #BFD7ED!important;
  box-shadow:0 3px 12px rgba(0,80,160,0.07)!important;
}

/* ── DATAFRAME ───────────────────────────────────────────────── */
[data-testid="stDataFrame"]{
  border:1.5px solid #BFD7ED!important;
  border-radius:14px!important; overflow:hidden;
}

/* ── DIVIDER ─────────────────────────────────────────────────── */
.divider{
  height:3px; border:none; border-radius:3px;
  background:linear-gradient(90deg,#0096C7,#48CAE4,#ADE8F4);
  margin:6px 0 26px;
}

/* ── FOOTER ──────────────────────────────────────────────────── */
.footer-strip{
  background:linear-gradient(135deg,#012A4A,#01497C);
  border-radius:16px; padding:20px 32px;
  text-align:center; margin-top:40px;
}
.footer-strip p{
  font-family:'Space Mono',monospace; font-size:11px;
  color:rgba(255,255,255,0.45); letter-spacing:1px; margin:0;
}
.footer-strip span{ color:#48CAE4; }

/* SCROLLBAR */
::-webkit-scrollbar{ width:5px; height:5px; }
::-webkit-scrollbar-track{ background:#F0F8FF; }
::-webkit-scrollbar-thumb{ background:#90C4E4; border-radius:3px; }
::-webkit-scrollbar-thumb:hover{ background:#0077B6; }
</style>
""", unsafe_allow_html=True)


# ── DATA ─────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data("data/plastics.csv")

@st.cache_data
def get_cards():
    return make_info_cards()

df_raw      = get_data()
info_cards  = get_cards()
all_years     = sorted(df_raw["year"].unique().tolist())
all_countries = sorted(df_raw["country"].dropna().unique().tolist())
plastic_cols  = {"HDPE":"hdpe","LDPE":"ldpe","Other":"o","PET":"pet",
                 "PP":"pp","PS":"ps","PVC":"pvc","Empty":"empty"}


# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 4px 16px;text-align:center;
                border-bottom:2px solid #BFD7ED;margin-bottom:14px;'>
      <div style='font-size:30px;margin-bottom:5px;'>🌊</div>
      <div style='font-family:Space Mono,monospace;font-size:10px;font-weight:700;
                  letter-spacing:2.5px;color:#0096C7;text-transform:uppercase;'>
        Control Panel</div>
    </div>""", unsafe_allow_html=True)

    def sb_lbl(t):
        st.markdown(f"<p style='font-size:10px;font-weight:700;letter-spacing:1.5px;"
                    f"text-transform:uppercase;color:#8A8A8A;margin:12px 0 5px;'>{t}</p>",
                    unsafe_allow_html=True)

    sb_lbl("📅 Year")
    sel_years = st.multiselect("yr", options=all_years, default=all_years, label_visibility="collapsed")

    sb_lbl("🌍 Country")
    sel_countries = st.multiselect("cn", options=all_countries, default=all_countries, label_visibility="collapsed")

    sb_lbl("♻️ Plastic Count Range")
    mn,mx = int(df_raw["grand_total"].min()), int(df_raw["grand_total"].max())
    gt_range = st.slider("gt", min_value=mn, max_value=mx, value=(mn,mx), step=5, label_visibility="collapsed")
    st.caption(f"**{gt_range[0]:,}** → **{gt_range[1]:,}** items")

    sb_lbl("🙋 Volunteers Range")
    mnv,mxv = int(df_raw["volunteers"].min()), int(df_raw["volunteers"].max())
    vol_range = st.slider("vr", min_value=mnv, max_value=mxv, value=(mnv,mxv), step=100, label_visibility="collapsed")
    st.caption(f"**{vol_range[0]:,}** → **{vol_range[1]:,}**")

    sb_lbl("🧪 Plastic Type Focus")
    focus = st.selectbox("ft", options=["All"]+list(plastic_cols.keys()), label_visibility="collapsed")

    sb_lbl("📊 Top N (charts)")
    top_n = st.slider("tn", min_value=5, max_value=20, value=10, step=1, label_visibility="collapsed")
    st.caption(f"Showing top **{top_n}**")

    sb_lbl("🔎 Search")
    search_kw = st.text_input("sk", placeholder="Company or country…", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⟳  Reset All Filters"):
        st.rerun()


# ── APPLY FILTERS ─────────────────────────────────────────────────
df = apply_filters(df_raw,
    selected_years=sel_years or all_years,
    selected_countries=sel_countries or all_countries,
    grand_total_range=gt_range,
    search_keyword=search_kw,
)
df = df[(df["volunteers"]>=vol_range[0]) & (df["volunteers"]<=vol_range[1])]
real_df = df[df["parent_company"]!="Grand Total"]


# ── HELPERS ───────────────────────────────────────────────────────
def sec(n, title, chips):
    ch = "".join(f"<span class='chip {c}'>{t}</span>" for t,c in chips)
    st.markdown(f"<div class='sec-wrap'>"
                f"<span class='sec-badge'>0{n}</span>"
                f"<span class='sec-title'>{title}</span>{ch}</div>",
                unsafe_allow_html=True)

def row2(fn1, fn2, gap="medium"):
    c1,c2 = st.columns(2, gap=gap)
    with c1: st.pyplot(fn1, use_container_width=True)
    with c2: st.pyplot(fn2, use_container_width=True)


# ════════════════════════════════════════════════════════════════
#  HERO
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class='hero'>
  <p class='hero-eyebrow'>◈ Break Free From Plastic · Global Brand Audit</p>
  <h1 class='hero-title'>Plastics Pollution <em>Explorer</em></h1>
  <p class='hero-sub'>
    Analyzing plastic waste across <strong>69 countries</strong> ·
    <strong>13,380 records</strong> · <strong>10,000+ corporate sources</strong>.<br>
    Use the sidebar filters — every chart updates instantly.
  </p>
  <div class='hero-chips'>
    <span class='hero-chip'>🗓 2019–2020</span>
    <span class='hero-chip'>🌏 69 Countries</span>
    <span class='hero-chip'>🏭 10K+ Brands</span>
    <span class='hero-chip'>♻ 7 Plastic Types</span>
    <span class='hero-chip'>📊 17 Charts</span>
    <span class='hero-chip'>🔍 6 Live Filters</span>
    <span class='hero-chip'>📑 6 Tabs</span>
  </div>
</div>""", unsafe_allow_html=True)


# ── INFO CARDS (matplotlib-generated, always works) ───────────────
titles = ["🌊 Ocean Crisis","📋 Brand Audit","🍶 PET #1 Polluter","🙋 Volunteers"]
subs   = ["8M tons enter oceans yearly",
          "Volunteers tag each piece to brands",
          "Single-use bottles dominate waste",
          "Thousands power cleanup campaigns"]
cols4  = st.columns(4, gap="small")
for col, b64, title, sub in zip(cols4, info_cards, titles, subs):
    with col:
        st.markdown(
            f"<div class='info-card'>"
            f"<img src='{b64}' alt='{title}'>"
            f"<div class='info-body'>"
            f"<div class='info-title'>{title}</div>"
            f"<div class='info-sub'>{sub}</div>"
            f"</div></div>",
            unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── KPI CARDS ─────────────────────────────────────────────────────
kpi = get_kpi_stats(df)
if focus != "All":
    ft  = real_df[plastic_cols[focus]].sum()
    fp  = ft/real_df["grand_total"].sum()*100 if real_df["grand_total"].sum()>0 else 0
    st.markdown(f"<div class='insight'>🧪 <strong>Focus: {focus}</strong> — "
                f"<strong>{ft:,.0f}</strong> items collected "
                f"({fp:.1f}% of filtered total)</div>", unsafe_allow_html=True)

kpi_items = [
    ("📋",f"{kpi['total_records']:,}","Records","#0077B6"),
    ("♻️",f"{kpi['total_plastic']:,.0f}","Plastic Items","#E63946"),
    ("📊",f"{kpi['avg_plastic_per_event']:.1f}","Avg / Event","#F57F17"),
    ("🙋",f"{int(kpi['total_volunteers']):,}","Volunteers","#7B2FBE"),
    ("🌍",str(kpi['countries_covered']),"Countries","#00B4D8"),
    ("🏭",f"{kpi['companies_identified']:,}","Companies","#2196F3"),
]
kh = "<div class='kpi-row'>"+"".join(
    f"<div class='kpi-card' style='--kc:{c};'><div class='kpi-bar'></div>"
    f"<span class='kpi-icon'>{i}</span>"
    f"<span class='kpi-val'>{v}</span>"
    f"<span class='kpi-label'>{l}</span></div>"
    for i,v,l,c in kpi_items)+"</div>"
st.markdown(kh, unsafe_allow_html=True)

# Metrics with delta
yr_sums = real_df.groupby("year")["grand_total"].sum()
v19 = int(yr_sums.get(2019,0)); v20 = int(yr_sums.get(2020,0))
top_country = real_df.groupby("country")["grand_total"].sum().idxmax() if len(real_df)>0 else "N/A"
m1,m2,m3,m4 = st.columns(4)
with m1: st.metric("2019 Plastic Items",  f"{v19:,}")
with m2: st.metric("2020 Plastic Items",  f"{v20:,}", delta=f"{v20-v19:+,}")
with m3: st.metric("Top Country",          top_country)
with m4: st.metric("PET Total",           f"{real_df['pet'].sum():,.0f}")

st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "📊  Overview",
    "📈  Trends",
    "🌍  Geography",
    "🔬  Statistics",
    "🏭  Corporate",
    "📋  Data",
])


# ══ TAB 1 — OVERVIEW ═════════════════════════════════════════════
with tab1:
    sec(1,"Plastic Type Overview",[("Pie","cg"),("Histogram","cr"),("Comparison","ct")])
    st.markdown("<div class='note'>💡 <strong>PET bottles</strong> dominate — single-use drink containers from major beverage brands are the #1 plastic found globally.</div>", unsafe_allow_html=True)

    with st.expander("📊 Plastic Type Distribution — Pie Chart & Histogram", expanded=True):
        row2(chart_pie(df), chart_histogram(df))

    with st.expander("📊 2019 vs 2020 Comparison & Nested Type-Year Donut"):
        row2(chart_plastic_compare(df), chart_nested_donut(df))


# ══ TAB 2 — TRENDS ═══════════════════════════════════════════════
with tab2:
    sec(2,"Time Trends",[("Line","cg"),("Area","co"),("Volunteers","cp"),("Events","cb")])
    st.markdown("<div class='insight'>📉 <strong>2020 shows fewer records</strong> — COVID-19 severely disrupted audit campaigns worldwide, cutting both volunteer numbers and events.</div>", unsafe_allow_html=True)

    with st.expander("📈 Plastic Collected Over Time — Line Chart", expanded=True):
        st.pyplot(chart_line(df), use_container_width=True)

    with st.expander("📈 Plastic Types Stacked Over Time — Area Chart"):
        st.pyplot(chart_area(df), use_container_width=True)

    with st.expander("🙋 Volunteer & Event Trends"):
        row2(chart_volunteers(df), chart_events(df))


# ══ TAB 3 — GEOGRAPHY ════════════════════════════════════════════
with tab3:
    sec(3,"Geographic Intelligence",[("Bar","cb"),("Scatter","co"),("Pie","ct"),("Efficiency","cp")])
    st.markdown("<div class='insight'>🌏 <strong>Taiwan, Philippines & Nigeria</strong> lead — strong volunteer networks + high plastic pollution levels in these regions.</div>", unsafe_allow_html=True)

    with st.expander(f"🌍 Top {top_n} Countries by Plastic Collected", expanded=True):
        st.pyplot(chart_bar(df, n=top_n), use_container_width=True)

    with st.expander("🔵 Volunteers vs. Plastic Scatter Plot"):
        st.pyplot(chart_scatter(df), use_container_width=True)

    with st.expander("🌐 Country Share Pie + Efficiency Ranking"):
        row2(chart_country_pie(df), chart_efficiency(df))

    with st.expander("📋 Country Summary Table"):
        cs = real_df.groupby("country").agg(
            Total=("grand_total","sum"), Records=("grand_total","count"),
            Volunteers=("volunteers","sum"), Events=("num_events","sum")
        ).sort_values("Total",ascending=False).reset_index()
        cs.columns=["Country","Total Plastic","Records","Volunteers","Events"]
        st.dataframe(cs, use_container_width=True, height=350)


# ══ TAB 4 — STATISTICS ═══════════════════════════════════════════
with tab4:
    sec(4,"Statistical Deep Dive",[("Box","cr"),("Violin","cp"),("Heatmap","cb")])
    st.markdown("<div class='note'>📦 Most events collect small amounts — a handful of massive campaigns skew the distribution significantly.</div>", unsafe_allow_html=True)

    with st.expander("📦 Box Plot & Violin Plot", expanded=True):
        row2(chart_box(df), chart_violin(df))

    with st.expander("🔥 Feature Correlation Heatmap"):
        st.markdown("<div class='insight'>🔬 <strong>PET strongly correlates with Grand Total</strong> — it's the dominant driver. Events & volunteers show moderate positive correlation with plastic found.</div>", unsafe_allow_html=True)
        st.pyplot(chart_heatmap(df), use_container_width=True)

    with st.expander("📊 Records Count per Year"):
        c1,c2 = st.columns(2, gap="medium")
        with c1: st.pyplot(chart_countplot(df), use_container_width=True)
        with c2:
            desc = real_df[["grand_total","pet","hdpe","volunteers"]].describe().round(1)
            desc.index = ["Count","Mean","Std","Min","25%","Median","75%","Max"]
            desc.columns = ["Total","PET","HDPE","Volunteers"]
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(desc, use_container_width=True, height=310)


# ══ TAB 5 — CORPORATE ════════════════════════════════════════════
with tab5:
    sec(5,"Corporate Accountability ★",[("Bonus","co")])
    st.markdown("<div class='note'>🏭 Excludes 'Unbranded'. <strong>Coca-Cola ranks #1</strong> consistently across all global brand audits.</div>", unsafe_allow_html=True)

    with st.expander(f"🏭 Top {top_n} Corporate Polluters Chart", expanded=True):
        st.pyplot(chart_top_companies(df, n=top_n), use_container_width=True)

    with st.expander("📋 Corporate Data Table"):
        top_df = get_top_polluters(df, n=top_n).reset_index(drop=True)
        top_df.index += 1
        st.dataframe(top_df, use_container_width=True, height=380)

    with st.expander("📊 Top Companies Share Stats"):
        total = real_df["grand_total"].sum()
        top5  = get_top_polluters(df, n=5)
        top5_total = top5["Total Plastic"].sum()
        s1,s2,s3 = st.columns(3)
        with s1: st.metric("Top 5 Share", f"{top5_total/total*100:.1f}%" if total>0 else "N/A")
        with s2: st.metric("#1 Brand", top5.iloc[0]["Company"] if len(top5)>0 else "N/A")
        with s3: st.metric("#1 Brand Items", f"{int(top5.iloc[0]['Total Plastic']):,}" if len(top5)>0 else "N/A")


# ══ TAB 6 — DATA ═════════════════════════════════════════════════
with tab6:
    sec(6,"Raw Data Explorer",[("Table","cg"),("Download","ct"),("Stats","cb")])

    real_show = real_df.rename(columns={
        "country":"Country","year":"Year","parent_company":"Company",
        "grand_total":"Total","num_events":"Events","volunteers":"Volunteers",
        "hdpe":"HDPE","ldpe":"LDPE","o":"Other","pet":"PET",
        "pp":"PP","ps":"PS","pvc":"PVC","empty":"Empty",
    }).reset_index(drop=True)

    g1,g2,g3 = st.columns([2,1,1])
    with g1:
        st.markdown(
            f"<p style='font-family:Space Mono,monospace;font-size:12px;color:#4A6FA5;'>"
            f"Showing <b style='color:#0077B6;'>{len(real_show):,}</b> records after all filters</p>",
            unsafe_allow_html=True)
    with g2:
        st.download_button("⬇ Download CSV",
            data=real_show.to_csv(index=False).encode("utf-8"),
            file_name="plastics_filtered.csv", mime="text/csv",
            use_container_width=True)
    with g3:
        sort_col = st.selectbox("Sort by", options=real_show.columns.tolist(),
            index=list(real_show.columns).index("Total"),
            label_visibility="collapsed")

    with st.expander("📋 Full Data Table", expanded=True):
        st.dataframe(real_show.sort_values(sort_col, ascending=False),
                     use_container_width=True, height=420)

    with st.expander("📈 Summary Statistics"):
        st.dataframe(
            real_show[["Total","Events","Volunteers","PET","HDPE","PP","PS","PVC"]]
            .describe().round(2), use_container_width=True)

    with st.expander("🌍 Country Summary"):
        cs = real_df.groupby("country").agg(
            Total=("grand_total","sum"), Records=("grand_total","count"),
            Volunteers=("volunteers","sum"), Events=("num_events","sum")
        ).sort_values("Total",ascending=False).reset_index()
        cs.columns = ["Country","Total Plastic","Records","Volunteers","Events"]
        st.dataframe(cs, use_container_width=True, height=350)

    with st.expander("🏭 Company Summary"):
        comp = real_df[real_df["parent_company"]!="Unbranded"].groupby("parent_company").agg(
            Total=("grand_total","sum"), Records=("grand_total","count")
        ).sort_values("Total",ascending=False).head(50).reset_index()
        comp.columns = ["Company","Total Plastic","Records"]
        st.dataframe(comp, use_container_width=True, height=350)


# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("""
<div class='footer-strip'>
  <p>🌊 <span>Plastics Pollution Explorer</span>
  &nbsp;·&nbsp; Break Free From Plastic Brand Audit (2019–2020)</p>
</div>""", unsafe_allow_html=True)
