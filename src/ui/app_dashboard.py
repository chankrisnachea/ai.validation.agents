# app_dashboard.py
import streamlit as st
import json
from agents.orchestrator_agent import orchestrate
from utils.file_utils import get_data_path

st.set_page_config(page_title="Agentic AI Validation System", layout="wide")
st.title("🤖 Agentic AI Validation System")

st.markdown("""
🧭 Guided Agentic Flow

Each intelligent agent plays a role in transforming a platform requirement into quality insights.
Click each agent below to interact with its part of the validation pipeline.
""")

# Upload Requirements File
uploaded_requirements = st.file_uploader("📂 Upload Requirement JSON", type=["json"])

# Selection method for planner agent
planner_method = st.radio("🧠 Select Planner Strategy", ["Rule-based applicability", "LLM-based applicability"])
use_llm = planner_method == "LLM-based applicability"

if uploaded_requirements:
    st.markdown("### 📄 Uploaded Requirements Preview")
    uploaded_content = json.load(uploaded_requirements)
    st.json(uploaded_content)
    uploaded_requirements.seek(0)  # Reset pointer for reuse in orchestration

#Semantic Query
query = st.text_input("🔍 Enter Semantic Query (optional)", placeholder="e.g., power test failures")

#Initialize session state if not already
if "orchestrator_ran" not in st.session_state:
    st.session_state["orchestrator_ran"] = False

#Run Orchestration Button
if st.button("🚀 Run Orchestration"):
    if uploaded_requirements:
        with open(get_data_path("requirements.json"), "wb") as f:
            f.write(uploaded_requirements.read())
            uploaded_requirements.seek(0)  # Reset pointer for reuse in orchestration
    try:
        planner_output, execution_df, report_summary = orchestrate(get_data_path("requirements.json"), use_llm=use_llm, query=query)
        st.session_state['planner_output'] = planner_output
        st.session_state['execution_df'] = execution_df
        st.session_state['report_summary'] = report_summary
        st.session_state['orchestrator_ran'] = True
        st.success("✅ Orchestration completed!")
    except Exception as e:
        st.session_state['orchestrator_ran'] = False
        st.error(f"❌ Orchestration failed: {e}")
else:
    st.warning("⚠️ Please upload requirements.json first.")

#Agent Expander
st.markdown("---")
with st.expander("🧠 Planner Agent Output"):
    if st.session_state.get('orchestrator_ran') and 'planner_output' in st.session_state:
        st.json(st.session_state['planner_output'])
        st.markdown("Planner Agent selected applicable test cases based on the requirement's applicability flags.")
    else:
        st.info("Run Orchestrator to see Planner output.")

with st.expander("⚙️ Executor Agent Output"):
    if st.session_state.get('orchestrator_ran') and 'execution_df' in st.session_state:
        st.dataframe(st.session_state['execution_df'])
        st.markdown("Executor Agent simulated test execution outcomes for selected tests.")
    else:
        st.info("Run Orchestrator to see Executor output.")

with st.expander("📊 Reporter Agent Output"):
    if st.session_state.get('orchestrator_ran') and 'report_summary' in st.session_state:
        st.markdown("### 📈 Summary")
        st.json(st.session_state['report_summary'][0])
        st.markdown("### 📂 Domain Breakdown")
        st.dataframe(st.session_state['report_summary'][1])
        st.markdown("### 🖼️ Validation Summary Chart")
        st.image(
            f"data:image/png;base64,{st.session_state['report_summary'][3]}",
            caption="Validation Summary Chart")
        st.markdown("Reporter Agent analyzed results and generated key insights.")
    else:
        st.info("Run Orchestrator to see Reporter output.")

st.markdown("""
            🗣️ Agent Personality Prompts
            + Orchestrator: "I'm the conductor of this validation symphony. Ready to activate the agents."
            
            + Planner Agent: "I choose the right tests for the right needs — no more, no less."
            
            + Executor Agent: "Give me a test plan, and I’ll give you results. Fast and clean."
            
            + Reporter Agent: "I turn numbers into insights — dashboards, heatmaps, and all."
            """)