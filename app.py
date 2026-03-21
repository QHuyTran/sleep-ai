import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Sleep AI Dashboard",
    page_icon="🌙",
    layout="wide"
)

# Load data


@st.cache_data
def load_data():
    sleep = pd.read_csv('sleep_data.csv')
    hrv = pd.read_csv('hrv_data.csv')
    hr = pd.read_csv('heart_rate.csv')
    sleep['date'] = pd.to_datetime(sleep['date'])
    hrv['date'] = pd.to_datetime(hrv['date'])
    hr['date'] = pd.to_datetime(hr['date'])
    return sleep, hrv, hr


sleep_df, hrv_df, hr_df = load_data()

# Sidebar
st.sidebar.title("🌙 Sleep AI")
page = st.sidebar.radio("Navigate", ["Dashboard", "AI Analysis"])
days = st.sidebar.slider("Days to display", 7, 90, 30)

# Filter by selected days
cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
sleep_filtered = sleep_df[sleep_df['date'] >= cutoff]
hrv_filtered = hrv_df[hrv_df['date'] >= cutoff]
hr_filtered = hr_df[hr_df['date'] >= cutoff]

if page == "Dashboard":
    st.title("Your Sleep Dashboard")

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    avg_sleep = sleep_filtered['total_sleep_hours'].mean()
    avg_hrv = hrv_filtered['hrv'].mean()
    avg_hr = hr_filtered['resting_hr'].mean()
    avg_deep = sleep_filtered['deep_hours'].mean()

    col1.metric("Avg Sleep", f"{avg_sleep:.1f} hrs",
                delta=f"{avg_sleep - 8:.1f} vs 8hr target")
    col2.metric("Avg HRV", f"{avg_hrv:.0f} ms")
    col3.metric("Avg Resting HR", f"{avg_hr:.0f} bpm")
    col4.metric("Avg Deep Sleep", f"{avg_deep:.1f} hrs")

    st.divider()

    # Sleep duration chart
    st.subheader("Sleep Duration")
    fig1 = px.bar(sleep_filtered, x='date', y='total_sleep_hours',
                  color_discrete_sequence=['#6366f1'])
    fig1.add_hline(y=8, line_dash="dash", line_color="green",
                   annotation_text="8hr target")
    fig1.update_layout(xaxis_title="Date", yaxis_title="Hours")
    st.plotly_chart(fig1, use_container_width=True)

    # Sleep stages breakdown
    st.subheader("Sleep Stage Breakdown")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Deep', x=sleep_filtered['date'],
                          y=sleep_filtered['deep_hours'], marker_color='#1e3a5f'))
    fig2.add_trace(go.Bar(name='REM', x=sleep_filtered['date'],
                          y=sleep_filtered['rem_hours'], marker_color='#6366f1'))
    fig2.add_trace(go.Bar(name='Core', x=sleep_filtered['date'],
                          y=sleep_filtered['core_hours'], marker_color='#a5b4fc'))
    fig2.update_layout(barmode='stack', xaxis_title="Date",
                       yaxis_title="Hours")
    st.plotly_chart(fig2, use_container_width=True)

    # HRV trend
    st.subheader("Heart Rate Variability (HRV)")
    fig3 = px.line(hrv_filtered, x='date', y='hrv',
                   color_discrete_sequence=['#10b981'])
    fig3.update_layout(xaxis_title="Date", yaxis_title="HRV (ms)")
    st.plotly_chart(fig3, use_container_width=True)

    # Resting HR
    st.subheader("Resting Heart Rate")
    fig4 = px.line(hr_filtered, x='date', y='resting_hr',
                   color_discrete_sequence=['#f43f5e'])
    fig4.update_layout(xaxis_title="Date", yaxis_title="BPM")
    st.plotly_chart(fig4, use_container_width=True)

elif page == "AI Analysis":
    st.title("AI Sleep Analysis")
    st.info("RAG pipeline coming in Day 3. Check back soon.")
