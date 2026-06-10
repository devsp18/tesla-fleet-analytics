import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.fleet_analysis import *

st.set_page_config(
    page_title="Tesla Fleet Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=DM+Sans:wght@200;300;400;500&display=swap');

:root {
    --bg:        #F7F4EF;
    --bg2:       #F0EDE7;
    --border:    #E2DDD6;
    --text:      #1A1714;
    --muted:     #9A9490;
    --red:       #E31937;
    --red-dim:   rgba(227,25,55,0.08);
    --green:     #1A6B3C;
    --green-dim: rgba(26,107,60,0.08);
    --mono:      'DM Mono', monospace;
    --display:   'Bebas Neue', sans-serif;
    --body:      'DM Sans', sans-serif;
}

* { box-sizing: border-box; }

.stApp {
    background: var(--bg);
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.025'/%3E%3C/svg%3E");
}

section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 1400px; }

/* ── Header ── */
.site-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 28px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 44px;
    animation: fadeUp 0.6s ease both;
}

.header-left {}

.wordmark {
    font-family: var(--display);
    font-size: 13px;
    letter-spacing: 6px;
    color: var(--red);
    margin-bottom: 10px;
}

.display-title {
    font-family: var(--display);
    font-size: 64px;
    letter-spacing: 2px;
    color: var(--text);
    line-height: 0.95;
    margin-bottom: 12px;
}

.header-meta {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.5px;
    font-weight: 300;
}

.header-right {
    text-align: right;
}

.header-stat {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    line-height: 2.2;
}

.header-stat span {
    color: var(--text);
    font-weight: 500;
}

/* ── KPI Strip ── */
.kpi-strip {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    border-top: 2px solid var(--text);
    margin-bottom: 52px;
    animation: fadeUp 0.6s 0.1s ease both;
}

.kpi-cell {
    padding: 20px 0 20px 0;
    border-right: 1px solid var(--border);
    padding-right: 24px;
    padding-left: 4px;
}

.kpi-cell:first-child { padding-left: 0; }
.kpi-cell:last-child { border-right: none; }

.kpi-lbl {
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}

.kpi-num {
    font-family: var(--display);
    font-size: 48px;
    letter-spacing: 1px;
    color: var(--text);
    line-height: 1;
}

.kpi-unit {
    font-family: var(--mono);
    font-size: 14px;
    color: var(--muted);
    font-weight: 300;
}

.kpi-sub {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    margin-top: 6px;
    font-weight: 300;
}

/* ── Section label ── */
.sec-label {
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

/* ── Insight cards ── */
.insight-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 28px;
}

.insight-card {
    background: white;
    border: 1px solid var(--border);
    padding: 20px 22px;
    border-radius: 2px;
}

.insight-card.red { border-top: 2px solid var(--red); }
.insight-card.dark { border-top: 2px solid var(--text); }
.insight-card.green { border-top: 2px solid var(--green); }

.insight-tag {
    font-family: var(--mono);
    font-size: 8px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
}

.insight-num {
    font-family: var(--display);
    font-size: 36px;
    letter-spacing: 1px;
    color: var(--text);
    line-height: 1;
    margin-bottom: 8px;
}

.insight-num.red { color: var(--red); }
.insight-num.green { color: var(--green); }

.insight-desc {
    font-family: var(--body);
    font-size: 12px;
    font-weight: 300;
    color: var(--muted);
    line-height: 1.6;
}

/* ── Market list ── */
.mkt-list { margin-top: 4px; }

.mkt-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 11px 0;
    border-bottom: 1px solid var(--border);
}

.mkt-name {
    font-family: var(--body);
    font-size: 12px;
    font-weight: 300;
    color: var(--text);
}

.mkt-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.mkt-rate {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--text);
    font-weight: 400;
    min-width: 42px;
    text-align: right;
}

.mkt-badge {
    font-family: var(--mono);
    font-size: 8px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 2px;
}

.mkt-badge.top { background: var(--green-dim); color: var(--green); border: 1px solid rgba(26,107,60,0.2); }
.mkt-badge.low { background: var(--red-dim); color: var(--red); border: 1px solid rgba(227,25,55,0.2); }
.mkt-badge.avg { background: var(--bg2); color: var(--muted); border: 1px solid var(--border); }

/* ── Finding cards (stats tab) ── */
.stat-block {
    background: white;
    border: 1px solid var(--border);
    padding: 24px;
    border-radius: 2px;
    margin-bottom: 16px;
}

.stat-num {
    font-family: var(--display);
    font-size: 52px;
    color: var(--text);
    letter-spacing: 1px;
    line-height: 1;
}

.stat-lbl {
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
}

.stat-desc {
    font-family: var(--body);
    font-size: 12px;
    font-weight: 300;
    color: var(--muted);
    margin-top: 8px;
    line-height: 1.6;
}

/* ── Sidebar ── */
.sidebar-logo {
    font-family: var(--display);
    font-size: 22px;
    letter-spacing: 4px;
    color: var(--text);
    padding: 16px 0 4px;
}

.sidebar-sub {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1px;
    margin-bottom: 20px;
}

.sidebar-section {
    font-family: var(--mono);
    font-size: 8px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
    margin-top: 4px;
}

.sidebar-info {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    line-height: 2;
    font-weight: 300;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--muted);
    padding: 10px 20px;
    border: none;
    border-bottom: 2px solid transparent;
}

.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    border-bottom: 2px solid var(--text) !important;
    background: transparent !important;
}

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Streamlit widget overrides */
.stSelectbox label, .stMultiSelect label, .stSlider label {
    font-family: var(--mono) !important;
    font-size: 9px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

.stSelectbox > div > div {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    font-family: var(--mono) !important;
    font-size: 11px !important;
    color: var(--text) !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background: var(--text) !important;
    border-radius: 2px !important;
}

hr { border-color: var(--border) !important; }
p, div { color: var(--text); }
/* Fix dropdown menu */
[data-baseweb="popover"] {
    background: #F7F4EF !important;
}

[data-baseweb="menu"] {
    background: #F7F4EF !important;
    border: 1px solid #E2DDD6 !important;
}

[data-baseweb="option"] {
    background: #F7F4EF !important;
    color: #1A1714 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
}

[data-baseweb="option"]:hover {
    background: #EDE9E3 !important;
}

[role="option"] {
    background: #F7F4EF !important;
    color: #1A1714 !important;
}

li[role="option"] {
    background: #F7F4EF !important;
    color: #1A1714 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
}            
</style>
""", unsafe_allow_html=True)

PLOT_CFG = dict(
    template='plotly_white',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Mono, monospace', color='#9A9490', size=10),
)

# ── Data ─────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    demo_df, vehicle_df, market_df = load_data()
    results = run_full_analysis(demo_df, vehicle_df, market_df)
    return demo_df, vehicle_df, market_df, results

demo_df, vehicle_df, market_df, results = load_all_data()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>TESLA</div>
    <div class='sidebar-sub'>Fleet Intelligence Platform</div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("<div class='sidebar-section'>Filters</div>", unsafe_allow_html=True)

    selected_year = st.selectbox(
        "Year",
        options=['All'] + sorted(demo_df['demo_year'].unique().tolist())
    )
    selected_models = st.multiselect(
        "Models",
        options=sorted(demo_df['vehicle_model'].unique().tolist()),
        default=sorted(demo_df['vehicle_model'].unique().tolist()),
    )
    selected_regions = st.multiselect(
        "Regions",
        options=sorted(demo_df['region'].unique().tolist()),
        default=sorted(demo_df['region'].unique().tolist()),
    )
    st.divider()
    st.markdown("""
    <div class='sidebar-info'>
        15,000 demo records<br>
        15 US markets<br>
        5 Tesla models<br>
        2024 — 2025<br>
        Americas fleet
    </div>
    """, unsafe_allow_html=True)

# ── Filter ───────────────────────────────────────────────────
filtered_df = demo_df.copy()
if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['demo_year'] == int(selected_year)]
if selected_models:
    filtered_df = filtered_df[filtered_df['vehicle_model'].isin(selected_models)]
if selected_regions:
    filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]

n_demos    = len(filtered_df)
n_conv     = int(filtered_df['converted'].sum())
conv_rate  = filtered_df['converted'].mean()
revenue    = filtered_df['revenue_generated'].sum()
sat        = filtered_df['satisfaction_score'].mean()
oppty      = results['underperforming']['total_revenue_opportunity']

# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
<div class='site-header'>
    <div class='header-left'>
        <div class='wordmark'>TESLA · FLEET INTELLIGENCE</div>
        <div class='display-title'>MARKETING FLEET<br>PERFORMANCE</div>
        <div class='header-meta'>
            Demo analytics &nbsp;·&nbsp; Conversion intelligence &nbsp;·&nbsp;
            Market performance &nbsp;·&nbsp; Americas &nbsp;·&nbsp; FY 2024–2025
        </div>
    </div>
    <div class='header-right'>
        <div class='header-stat'>RECORDS &nbsp;&nbsp;<span>{n_demos:,}</span></div>
        <div class='header-stat'>CONVERTED &nbsp;<span>{n_conv:,}</span></div>
        <div class='header-stat'>CONV RATE &nbsp;<span>{conv_rate:.1%}</span></div>
        <div class='header-stat'>MARKETS &nbsp;&nbsp;<span>{filtered_df['market'].nunique()}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Strip ────────────────────────────────────────────────
st.markdown(f"""
<div class='kpi-strip'>
    <div class='kpi-cell'>
        <div class='kpi-lbl'>Demo Drives</div>
        <div class='kpi-num'>{n_demos:,}</div>
        <div class='kpi-sub'>Across {filtered_df['market'].nunique()} markets</div>
    </div>
    <div class='kpi-cell'>
        <div class='kpi-lbl'>Conversions</div>
        <div class='kpi-num'>{n_conv:,}</div>
        <div class='kpi-sub'>{conv_rate:.1%} fleet average</div>
    </div>
    <div class='kpi-cell'>
        <div class='kpi-lbl'>Revenue</div>
        <div class='kpi-num'>${revenue/1e6:.1f}<span class='kpi-unit'>M</span></div>
        <div class='kpi-sub'>From converted demos</div>
    </div>
    <div class='kpi-cell'>
        <div class='kpi-lbl'>Satisfaction</div>
        <div class='kpi-num'>{sat:.2f}<span class='kpi-unit'>/5</span></div>
        <div class='kpi-sub'>Avg customer score</div>
    </div>
    <div class='kpi-cell'>
        <div class='kpi-lbl'>Opportunity</div>
        <div class='kpi-num'>${oppty/1e6:.1f}<span class='kpi-unit'>M</span></div>
        <div class='kpi-sub'>Addressable revenue gap</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Market Performance",
    "Vehicle Analytics",
    "Customer Segments",
    "Trends & Timing",
    "Statistical Model"
])

def make_chart(**kwargs):
    d = dict(**PLOT_CFG)
    d.update(kwargs)
    return d

# ── Tab 1: Market Performance ────────────────────────────────
with tab1:
    market_perf = conversion_by_market(filtered_df)
    avg_conv    = market_perf['conversion_rate'].mean()
    weekend     = results['weekend_analysis']
    underperf   = results['underperforming']
    best        = market_perf.iloc[0]
    worst       = market_perf.iloc[-1]

    col_chart, col_list = st.columns([3, 2])

    with col_chart:
        st.markdown("<div class='sec-label'>Conversion Rate by Market</div>", unsafe_allow_html=True)
        bar_colors = [
            '#E31937' if t == 'Needs Attention'
            else '#1A1714' if t == 'High Performer'
            else '#C8C4BE'
            for t in market_perf['performance_tier']
        ]
        fig = go.Figure(go.Bar(
            x=market_perf['market'],
            y=market_perf['conversion_rate'] * 100,
            marker=dict(color=bar_colors, line=dict(width=0)),
            text=[f"{r:.1%}" for r in market_perf['conversion_rate']],
            textposition='outside',
            textfont=dict(size=9, color='#9A9490', family='DM Mono'),
            width=0.55
        ))
        fig.add_hline(
            y=avg_conv * 100,
            line_dash="dot", line_color="#C8C4BE", line_width=1,
            annotation_text=f"avg  {avg_conv:.1%}",
            annotation_font=dict(color='#9A9490', size=9, family='DM Mono')
        )
        fig.update_layout(
            **make_chart(height=360, margin=dict(l=0,r=0,t=30,b=0)),
            xaxis=dict(tickangle=-35, gridcolor='#EDE9E3', color='#C8C4BE',
                      tickfont=dict(size=9, family='DM Mono'), linecolor='#E2DDD6'),
            yaxis=dict(gridcolor='#EDE9E3', color='#C8C4BE', ticksuffix='%',
                      tickfont=dict(size=9, family='DM Mono')),
            showlegend=False, bargap=0.3
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_list:
        st.markdown("<div class='sec-label'>Market Rankings</div>", unsafe_allow_html=True)
        st.markdown("<div class='mkt-list'>", unsafe_allow_html=True)
        for _, row in market_perf.iterrows():
            tier = row['performance_tier']
            badge_cls = 'top' if tier == 'High Performer' else 'low' if tier == 'Needs Attention' else 'avg'
            badge_txt = 'Top' if tier == 'High Performer' else 'Review' if tier == 'Needs Attention' else 'Avg'
            st.markdown(f"""
            <div class='mkt-row'>
                <div class='mkt-name'>{row['market']}</div>
                <div class='mkt-right'>
                    <div class='mkt-rate'>{row['conversion_rate']:.1%}</div>
                    <span class='mkt-badge {badge_cls}'>{badge_txt}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='insight-grid'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class='insight-card red'>
            <div class='insight-tag'>Revenue Opportunity</div>
            <div class='insight-num red'>${underperf['total_revenue_opportunity']/1e6:.1f}M</div>
            <div class='insight-desc'>
                Addressable if {len(underperf['underperforming_markets'])} underperforming
                markets reach fleet average of {underperf['overall_avg_conversion']:.1%}.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='insight-card dark'>
            <div class='insight-tag'>Performance Gap</div>
            <div class='insight-num'>{(best['conversion_rate']-worst['conversion_rate']):.1%}</div>
            <div class='insight-desc'>
                {best['market'].split(',')[0]} leads at {best['conversion_rate']:.1%}.
                {worst['market'].split(',')[0]} trails at {worst['conversion_rate']:.1%}.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='insight-card green'>
            <div class='insight-tag'>Weekend Lift</div>
            <div class='insight-num green'>+{weekend['lift']}%</div>
            <div class='insight-desc'>
                Weekend demos convert at {weekend['weekend_conversion_rate']:.1%}
                vs {weekend['weekday_conversion_rate']:.1%} on weekdays (p &lt; 0.001).
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Tab 2: Vehicle Analytics ─────────────────────────────────
with tab2:
    model_perf = conversion_by_model(filtered_df)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='sec-label'>Conversion Rate by Model</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=model_perf['vehicle_model'],
            y=model_perf['conversion_rate'] * 100,
            name='Conv Rate',
            marker_color='#1A1714',
            marker_line_width=0,
            width=0.4, yaxis='y'
        ))
        fig.add_trace(go.Scatter(
            x=model_perf['vehicle_model'],
            y=model_perf['avg_satisfaction'],
            name='Satisfaction',
            line=dict(color='#E31937', width=1.5),
            marker=dict(size=5, color='#E31937'),
            mode='lines+markers', yaxis='y2'
        ))
        fig.update_layout(
            **make_chart(height=300, margin=dict(l=0,r=40,t=10,b=0)),
            yaxis=dict(title='Conv Rate (%)', gridcolor='#EDE9E3', color='#C8C4BE',
                      ticksuffix='%', tickfont=dict(size=9)),
            yaxis2=dict(title='Satisfaction', overlaying='y', side='right',
                       color='#E31937', range=[3,5.5], tickfont=dict(size=9)),
            legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#9A9490', size=9)),
            xaxis=dict(gridcolor='#EDE9E3', color='#C8C4BE', tickfont=dict(size=10)),
            bargap=0.5
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='sec-label'>Revenue per Demo Drive</div>", unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=model_perf['vehicle_model'],
            y=model_perf['revenue_per_demo'],
            marker=dict(
                color=['#1A1714','#3D3A36','#605C57','#837F7A','#C8C4BE'],
                line=dict(width=0)
            ),
            text=[f"${v:,.0f}" for v in model_perf['revenue_per_demo']],
            textposition='outside',
            textfont=dict(size=9, color='#9A9490', family='DM Mono'),
            width=0.4
        ))
        fig2.update_layout(
            **make_chart(height=300, margin=dict(l=0,r=0,t=10,b=0)),
            yaxis=dict(gridcolor='#EDE9E3', color='#C8C4BE', tickfont=dict(size=9)),
            xaxis=dict(gridcolor='#EDE9E3', color='#C8C4BE', tickfont=dict(size=10)),
            bargap=0.5
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='sec-label' style='margin-top:16px;'>Utilization Distribution by Model</div>", unsafe_allow_html=True)
    fig3 = go.Figure()
    palette = ['#1A1714','#3D3A36','#605C57','#837F7A','#C8C4BE']
    for i, model in enumerate(sorted(vehicle_df['vehicle_model'].unique())):
        d = vehicle_df[vehicle_df['vehicle_model'] == model]
        fig3.add_trace(go.Box(
            y=d['avg_utilization'], name=model,
            marker_color=palette[i], line_color=palette[i],
            boxpoints='outliers',
            fillcolor=f'rgba(26,23,20,{0.03+i*0.02})'
        ))
    fig3.update_layout(
        **make_chart(height=260, margin=dict(l=0,r=0,t=10,b=0)),
        yaxis=dict(title='Utilization Rate', gridcolor='#EDE9E3', color='#C8C4BE',
                  tickformat='.0%', tickfont=dict(size=9)),
        xaxis=dict(gridcolor='rgba(0,0,0,0)', color='#C8C4BE', tickfont=dict(size=10)),
        showlegend=False
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Tab 3: Customer Segments ──────────────────────────────────
with tab3:
    seg_perf     = conversion_by_segment(filtered_df)
    dur          = results['duration_impact']
    dur_bucket   = dur['by_duration_bucket']

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='sec-label'>Conversion by Segment</div>", unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=seg_perf['conversion_pct'],
            y=seg_perf['customer_segment'],
            orientation='h',
            marker=dict(
                color=[palette[i % 5] for i in range(len(seg_perf))],
                line=dict(width=0)
            ),
            text=[f"{v:.1f}%" for v in seg_perf['conversion_pct']],
            textposition='outside',
            textfont=dict(size=9, color='#9A9490', family='DM Mono'),
        ))
        fig.update_layout(
            **make_chart(height=300, margin=dict(l=0,r=40,t=10,b=0)),
            xaxis=dict(title='Conv Rate (%)', gridcolor='#EDE9E3', color='#C8C4BE',
                      tickfont=dict(size=9)),
            yaxis=dict(gridcolor='rgba(0,0,0,0)', color='#605C57',
                      tickfont=dict(size=10, family='DM Mono')),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='sec-label'>Conversion by Drive Duration</div>", unsafe_allow_html=True)
        fig2 = go.Figure(go.Scatter(
            x=dur_bucket['duration_bucket'].astype(str),
            y=dur_bucket['conversion_rate'] * 100,
            mode='lines+markers',
            line=dict(color='#1A1714', width=1.5),
            marker=dict(size=7, color='#1A1714'),
            fill='tozeroy', fillcolor='rgba(26,23,20,0.04)'
        ))
        fig2.update_layout(
            **make_chart(height=300, margin=dict(l=0,r=0,t=10,b=0)),
            xaxis=dict(title='Duration', gridcolor='#EDE9E3', color='#C8C4BE',
                      tickfont=dict(size=10, family='DM Mono')),
            yaxis=dict(title='Conv Rate (%)', gridcolor='#EDE9E3', color='#C8C4BE',
                      ticksuffix='%', tickfont=dict(size=9)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""
    <div class='stat-block' style='margin-top:16px;'>
        <div style='display:grid; grid-template-columns:repeat(4,1fr); gap:32px;'>
            <div>
                <div class='stat-lbl'>Avg — Converted</div>
                <div class='stat-num'>{dur['avg_duration_converted']}<span style='font-family:var(--mono);font-size:18px;color:#9A9490;'>min</span></div>
            </div>
            <div>
                <div class='stat-lbl'>Avg — Not Converted</div>
                <div style='font-family:var(--display);font-size:52px;color:#C8C4BE;letter-spacing:1px;line-height:1;'>{dur['avg_duration_not_converted']}<span style='font-family:var(--mono);font-size:18px;'>min</span></div>
            </div>
            <div>
                <div class='stat-lbl'>Pearson Correlation</div>
                <div style='font-family:var(--display);font-size:52px;color:#1A1714;letter-spacing:1px;line-height:1;'>{dur['correlation']}</div>
            </div>
            <div>
                <div class='stat-lbl'>Significance</div>
                <div style='font-family:var(--display);font-size:52px;color:#E31937;letter-spacing:1px;line-height:1;'>{'<.001' if dur['p_value'] < 0.001 else round(dur['p_value'],3)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Tab 4: Trends & Timing ───────────────────────────────────
with tab4:
    seasonal = results['seasonal_trends']
    monthly  = seasonal['by_month']
    hourly   = results['hourly_analysis']['by_hour']
    wknd     = results['weekend_analysis']

    st.markdown("<div class='sec-label'>Monthly Volume & Conversion Rate</div>", unsafe_allow_html=True)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=monthly['demo_month_name'] + ' ' + monthly['demo_year'].astype(str),
        y=monthly['demos'], name='Demos',
        marker_color='#EDE9E3', marker_line_color='#E2DDD6', marker_line_width=1
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=monthly['demo_month_name'] + ' ' + monthly['demo_year'].astype(str),
        y=monthly['conversion_rate'] * 100, name='Conv Rate',
        line=dict(color='#E31937', width=1.5),
        mode='lines+markers', marker=dict(size=4, color='#E31937')
    ), secondary_y=True)
    fig.update_layout(
        **make_chart(height=320, margin=dict(l=0,r=40,t=10,b=0)),
        xaxis=dict(tickangle=-35, gridcolor='#EDE9E3', color='#C8C4BE',
                  tickfont=dict(size=9, family='DM Mono')),
        yaxis=dict(title='Demos', gridcolor='#EDE9E3', color='#C8C4BE',
                  tickfont=dict(size=9)),
        yaxis2=dict(title='Conv %', color='#E31937', ticksuffix='%',
                   tickfont=dict(size=9)),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#9A9490', size=9)),
        bargap=0.2
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='sec-label'>Conversion by Hour</div>", unsafe_allow_html=True)
        fig2 = go.Figure(go.Scatter(
            x=hourly['hour_of_day'],
            y=hourly['conversion_rate'] * 100,
            mode='lines+markers', fill='tozeroy',
            line=dict(color='#1A1714', width=1.5),
            fillcolor='rgba(26,23,20,0.04)',
            marker=dict(size=5, color='#1A1714')
        ))
        fig2.update_layout(
            **make_chart(height=260, margin=dict(l=0,r=0,t=10,b=0)),
            xaxis=dict(title='Hour', gridcolor='#EDE9E3', color='#C8C4BE',
                      tickvals=list(range(9,20)),
                      ticktext=[f"{h}:00" for h in range(9,20)],
                      tickfont=dict(size=9, family='DM Mono')),
            yaxis=dict(title='Conv %', gridcolor='#EDE9E3', color='#C8C4BE',
                      ticksuffix='%', tickfont=dict(size=9)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("<div class='sec-label'>Weekday vs Weekend</div>", unsafe_allow_html=True)
        fig3 = go.Figure(go.Bar(
            x=['Weekday', 'Weekend'],
            y=[wknd['weekday_conversion_rate']*100, wknd['weekend_conversion_rate']*100],
            marker_color=['#EDE9E3', '#1A1714'],
            marker_line_width=0,
            text=[f"{wknd['weekday_conversion_rate']:.1%}", f"{wknd['weekend_conversion_rate']:.1%}"],
            textposition='outside',
            textfont=dict(size=12, color='#9A9490', family='DM Mono'),
            width=0.3
        ))
        fig3.update_layout(
            **make_chart(height=260, margin=dict(l=0,r=0,t=10,b=40)),
            yaxis=dict(title='Conv %', gridcolor='#EDE9E3', color='#C8C4BE',
                      ticksuffix='%', tickfont=dict(size=9)),
            xaxis=dict(gridcolor='rgba(0,0,0,0)', color='#C8C4BE',
                      tickfont=dict(size=11, family='DM Mono')),
            showlegend=False, bargap=0.6
        )
        st.plotly_chart(fig3, use_container_width=True)

# ── Tab 5: Statistical Model ─────────────────────────────────
with tab5:
    reg      = results['regression_model']
    feat_imp = reg['significant_features'].head(10)
    opp      = results['underperforming']['opportunity_analysis']

    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("<div class='sec-label'>Logistic Regression — Conversion Probability Drivers</div>", unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=feat_imp['coefficient'],
            y=feat_imp['feature'],
            orientation='h',
            marker=dict(
                color=['#1A1714' if x > 0 else '#E31937' for x in feat_imp['coefficient']],
                line=dict(width=0)
            ),
            text=[f"{v:+.3f}" for v in feat_imp['coefficient']],
            textposition='outside',
            textfont=dict(size=9, color='#9A9490', family='DM Mono')
        ))
        fig.add_vline(x=0, line_color='#E2DDD6', line_width=1)
        fig.update_layout(
            **make_chart(height=360, margin=dict(l=0,r=40,t=10,b=0)),
            xaxis=dict(title='Log-Odds Coefficient', gridcolor='#EDE9E3', color='#C8C4BE',
                      tickfont=dict(size=9)),
            yaxis=dict(gridcolor='rgba(0,0,0,0)', color='#605C57',
                      tickfont=dict(size=10, family='DM Mono')),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='sec-label'>Model Stats</div>", unsafe_allow_html=True)
        for lbl, val in [
            ("Pseudo R²", f"{reg['pseudo_r2']}"),
            ("AIC", f"{reg['aic']:,.0f}"),
            ("Predictors", f"{len(reg['significant_features'])}"),
        ]:
            st.markdown(f"""
            <div class='stat-block' style='margin-bottom:12px; padding:18px 20px;'>
                <div class='stat-lbl'>{lbl}</div>
                <div style='font-family:var(--display);font-size:40px;color:var(--text);
                            letter-spacing:1px;line-height:1;'>{val}</div>
            </div>
            """, unsafe_allow_html=True)

    if not opp.empty:
        st.markdown("<div class='sec-label' style='margin-top:20px;'>Revenue Opportunity — Underperforming Markets</div>", unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=opp['market'],
            y=opp['revenue_opportunity'],
            marker=dict(
                color=palette[:len(opp)],
                line=dict(width=0)
            ),
            text=[f"${v:,.0f}" for v in opp['revenue_opportunity']],
            textposition='outside',
            textfont=dict(size=9, color='#9A9490', family='DM Mono'),
            width=0.4
        ))
        fig2.update_layout(
            **make_chart(height=260, margin=dict(l=0,r=0,t=10,b=0)),
            xaxis=dict(gridcolor='#EDE9E3', color='#C8C4BE', tickangle=-10,
                      tickfont=dict(size=10)),
            yaxis=dict(title='Revenue Opportunity ($)', gridcolor='#EDE9E3',
                      color='#C8C4BE', tickfont=dict(size=9)),
            showlegend=False, bargap=0.5
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown(f"""
        <div class='stat-block'>
            <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:32px;'>
                <div>
                    <div class='stat-lbl'>Total Opportunity</div>
                    <div style='font-family:var(--display);font-size:48px;color:#E31937;letter-spacing:1px;line-height:1;'>
                        ${results['underperforming']['total_revenue_opportunity']/1e6:.1f}M
                    </div>
                </div>
                <div>
                    <div class='stat-lbl'>Target Conv Rate</div>
                    <div style='font-family:var(--display);font-size:48px;color:var(--text);letter-spacing:1px;line-height:1;'>
                        {results['underperforming']['overall_avg_conversion']:.1%}
                    </div>
                </div>
                <div>
                    <div class='stat-lbl'>Markets to Improve</div>
                    <div style='font-family:var(--display);font-size:48px;color:var(--text);letter-spacing:1px;line-height:1;'>
                        {len(opp)}
                    </div>
                </div>
            </div>
            <div style='font-family:var(--body);font-size:12px;font-weight:300;color:#9A9490;margin-top:16px;line-height:1.7;border-top:1px solid var(--border);padding-top:14px;'>
                Hypothesis: If Las Vegas, Atlanta, Chicago and Miami reached the fleet average conversion
                rate of {results['underperforming']['overall_avg_conversion']:.1%}, projected incremental
                revenue would be ${results['underperforming']['total_revenue_opportunity']:,.0f}.
                Customer segment targeting and weekend scheduling represent the highest-ROI optimization levers.
            </div>
        </div>
        """, unsafe_allow_html=True)