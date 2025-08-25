import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🔍 LangGraph State Monitor")
st.write("Workflow State Visualization")

# Sample data
data = {
    'Step': [1, 2, 3, 4, 5, 6],
    'Step_Name': ['Start', 'Fetch Stock', 'Fetch News', 'Analyze Stock', 'Analyze News', 'Final'],
    'Progress': [0, 20, 40, 60, 80, 100],
    'Status': ['Init', 'Stock Data', 'News Data', 'Stock Analysis', 'News Analysis', 'Complete']
}

df = pd.DataFrame(data)

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Steps", 6)
with col2:
    st.metric("Symbol", "AAPL") 
with col3:
    st.metric("Status", "Complete")

# Progress Chart
st.subheader("📈 Progress")
fig = px.line(df, x='Step', y='Progress', title='Workflow Progress')
st.plotly_chart(fig, use_container_width=True)

# Bar Chart  
st.subheader("📊 Steps")
fig2 = px.bar(df, x='Step_Name', y='Progress', title='Step Progress')
st.plotly_chart(fig2, use_container_width=True)

# Data Table
st.subheader("📋 Details")
st.dataframe(df)

st.success("✅ State Monitor Working!")
