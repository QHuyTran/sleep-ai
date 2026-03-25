import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processor import process_health_export
from rag_engine import build_rag_engine
import os

# Page config
st.set_page_config(
    page_title="Sleep AI Dashboard",
    page_icon="🌙",
    layout="wide"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Upload screen
if not st.session_state.data_loaded:
    st.title("🌙 Sleep AI")
    st.subheader("Personalized sleep analysis powered by AI")
    st.write("Upload your Apple Health export to get started.")

    with st.expander("How to export your Apple Health data"):
        st.write("""
        1. Open the **Health app** on your iPhone
        2. Tap your **profile picture** (top right)
        3. Tap **Export All Health Data**
        4. Wait 1-2 minutes for it to prepare
        5. **AirDrop or email** the zip file to your computer
        6. Upload the zip file below
        """)

    uploaded_file = st.file_uploader(
        "Upload export.zip from Apple Health",
        type=['zip', 'xml'],
        help="Your data is processed locally and never stored."
    )

    if uploaded_file:
        with st.spinner("Processing your health data... this may take 1-2 minutes"):
            try:
                file_bytes = uploaded_file.read()
                sleep_df, hrv_df, hr_df = process_health_export(file_bytes)
                st.session_state.sleep_df = sleep_df
                st.session_state.hrv_df = hrv_df
                st.session_state.hr_df = hr_df
                st.session_state.data_loaded = True
                st.success(
                    f"Loaded {len(sleep_df)} nights of sleep data. Redirecting...")
                st.rerun()
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                st.write(
                    "Make sure you're uploading the zip file exported directly from Apple Health.")
    st.stop()

# Data is loaded - retrieve from session state
sleep_df = st.session_state.sleep_df
hrv_df = st.session_state.hrv_df
hr_df = st.session_state.hr_df

# Sidebar
st.sidebar.title("🌙 Sleep AI")
page = st.sidebar.radio("Navigate", ["Dashboard", "AI Analysis"])
days = st.sidebar.slider("Days to display", 7, 90, 30)
if st.sidebar.button("Upload New Data"):
    st.session_state.data_loaded = False
    st.rerun()

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
    st.title("🧠 AI Sleep Analysis")
    st.write("Powered by RAG over sleep science research documents.")

    # Build RAG engine (cached so it only loads once)
    @st.cache_resource
    def load_rag_engine():
        return build_rag_engine()

    with st.spinner("Loading AI engine... (first load takes 1-2 minutes)"):
        engine = load_rag_engine()

    st.success("AI engine ready")
    st.divider()

    # Personalized analysis using real data
    st.subheader("Your Personalized Analysis")

    if st.button("Analyze My Sleep"):
        # Build context from real data
        recent_sleep = sleep_df.tail(7)
        avg_sleep = recent_sleep['total_sleep_hours'].mean()
        avg_deep = recent_sleep['deep_hours'].mean()
        avg_rem = recent_sleep['rem_hours'].mean()
        worst_night = recent_sleep.loc[recent_sleep['total_sleep_hours'].idxmin(
        )]
        best_night = recent_sleep.loc[recent_sleep['total_sleep_hours'].idxmax(
        )]

        recent_hrv = hrv_df.tail(7)
        avg_hrv = recent_hrv['hrv'].mean() if len(recent_hrv) > 0 else None

        # Construct grounded prompt with real numbers
        personal_context = f"""
        The user's sleep data from the last 7 nights:
        - Average total sleep: {avg_sleep:.1f} hours
        - Average deep sleep: {avg_deep:.1f} hours  
        - Average REM sleep: {avg_rem:.1f} hours
        - Worst night: {worst_night['total_sleep_hours']:.1f} hours on {worst_night['date'].strftime('%B %d')}
        - Best night: {best_night['total_sleep_hours']:.1f} hours on {best_night['date'].strftime('%B %d')}
        - Average HRV: {f'{avg_hrv:.0f} ms' if avg_hrv else 'not available'}
        """

        query = f"""
        {personal_context}

        Based on this person's actual sleep data, provide exactly 3 specific and actionable 
        recommendations to improve their sleep quality. For each recommendation:
        1. State the specific action clearly
        2. Explain why it applies to their data specifically
        3. Cite which source document supports this recommendation
        
        Be specific to their numbers — reference their actual averages in your response.
        """

        with st.spinner("Analyzing your sleep data..."):
            response = engine.query(query)

        st.markdown("### Your Recommendations")
        st.write(str(response))

    st.divider()

    # Free-form chat with sleep data context
    st.subheader("Ask Anything About Your Sleep")
    user_question = st.text_input("Ask a question about sleep or your data:",
                                  placeholder="e.g. How can I get more deep sleep?")

    if user_question:
        recent_sleep = sleep_df.tail(7)
        avg_sleep = recent_sleep['total_sleep_hours'].mean()
        avg_deep = recent_sleep['deep_hours'].mean()
        avg_rem = recent_sleep['rem_hours'].mean()
        recent_hrv = hrv_df.tail(7)
        avg_hrv = recent_hrv['hrv'].mean() if len(recent_hrv) > 0 else None

        personalized_question = f"""
      Context about this specific user:
      - Average total sleep last 7 nights: {avg_sleep:.1f} hours
      - Average deep sleep last 7 nights: {avg_deep:.1f} hours
      - Average REM sleep last 7 nights: {avg_rem:.1f} hours
      - Average HRV last 7 nights: {f'{avg_hrv:.0f} ms' if avg_hrv else 'not available'}
      
      User question: {user_question}
      
      Answer specifically for this user using their actual data above.
      Cite your sources.
      """

        with st.spinner("Thinking..."):
            response = engine.query(personalized_question)
        st.markdown("**Answer:**")
        st.write(str(response))
