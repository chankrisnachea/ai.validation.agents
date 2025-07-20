# app_chat.py

import streamlit as st
import streamlit.components.v1 as components
import json
from agents.orchestrator_agent import orchestrate_planner, orchestrate_executor, orchestrate_reporter
from agents.citation_agent import evaluate_response
from utils.file_utils import get_data_path

# Function to auto-focus the textarea input
def auto_focus_textarea():
    components.html(
        """
        <script>
            const interval = setInterval(() => {
                const input = window.parent.document.querySelector('textarea');
                if (input) {
                    input.focus();
                    clearInterval(interval);
                }
            }, 100);
        </script>
        """,
        height=0,
    )

st.set_page_config(page_title="Agentic AI Validation System", layout="centered")
st.title("🤖 Agentic AI Validation System")

if "stage" not in st.session_state:
    st.session_state.stage = "init"
    st.session_state.file_uploaded = False
    st.session_state.use_llm = False
    st.session_state.planner_output = None
    st.session_state.execution_df = None
    st.session_state.report_summary = None
    st.session_state.messages = []

# Render previous chat messages
for role, content in st.session_state.messages:
    with st.chat_message(role):
        if isinstance(content, dict):
            if content.get("type") == "json":
                st.json(content["data"])
            elif content.get("type") == "dataframe":
                st.dataframe(content["data"])
        else:
            st.write(str(content))

# Show initial prompt if first run
if st.session_state.stage == "init":
    st.session_state.messages.append(("assistant", "Hello! I'm your AI validation Agent. Upload a requirements file to get started."))
    st.session_state.stage = "awaiting_upload"
    st.rerun()

elif st.session_state.stage == "awaiting_upload":
    uploaded_file = st.file_uploader("Upload the requirements json file", type=["json"])
    if uploaded_file and not st.session_state.file_uploaded:
        with open(get_data_path("requirements.json"), "wb") as f:
            f.write(uploaded_file.read())
        st.session_state.file_uploaded = True

        #Display uploaded requirements
        with open(get_data_path("requirements.json")) as f:
            requirements_data = json.load(f)
        st.session_state.messages.append(("assistant", "✅ Requirements file uploaded successfully!"))
        st.session_state.messages.append(("assistant", "Here are the requirements:"))
        st.session_state.messages.append(("assistant", {"type": "json", "data": requirements_data}))
        st.session_state.stage = "ask_to_plan"
        st.session_state.messages.append(
            ("assistant", "Would you like me to ask the Planner Agent to select test cases?"))
        st.rerun()

elif st.session_state.stage == "ask_to_plan":
    user_input = st.chat_input("yes or no", key="ask_to_plan_input")
    auto_focus_textarea()
    if user_input:
        st.session_state.messages.append(("user", user_input))
        if "yes" in user_input.lower():
            st.session_state.stage = "select_planner"
        else:
            st.session_state.messages.append(("assistant", "Okay, let me know when you're ready to proceed."))
        st.rerun()

elif st.session_state.stage == "select_planner":
    st.session_state.messages.append(("assistant", "🔍 Would you like me to select test cases based on rule-based applicability (1), or use an intelligent LLM-based applicability (2)?"))
    st.session_state.stage = "awaiting_for_planner_option"
    st.rerun()

elif st.session_state.stage == "awaiting_for_planner_option":
    user_input = st.chat_input("Enter 1 or 2", key="select_planner_input")
    auto_focus_textarea()
    if user_input:
        st.session_state.messages.append(("user", user_input))
        if user_input.strip() == "1":
            st.session_state.use_llm = False
            st.session_state.messages.append(("assistant", "⚙️ Running rule-based Planner Agent..."))
        elif user_input.strip() == "2":
            st.session_state.use_llm = True
            st.session_state.messages.append(("assistant", "🧠 Running LLM-based Planner Agent...(it may take a few minutes, please wait)"))
        else:
            st.session_state.messages.append(("assistant", "❌ Invalid input. Please enter 1 or 2."))
            st.rerun()
        st.session_state.stage = "run_planner"
        st.rerun()

elif st.session_state.stage == "run_planner":
        planner_output = orchestrate_planner(get_data_path("sample_validation_plan.json"), use_llm=st.session_state.use_llm)
        st.session_state.planner_output = planner_output
        st.session_state.messages.append(
            ("assistant",
             f"🧠 Planner Agent selected {len(st.session_state.planner_output['test_catalog'])} test cases."))
        st.session_state.messages.append(("assistant", {"type": "json", "data": st.session_state.planner_output}))

        # Include citation/judgement log if LLM is used
        if st.session_state.use_llm and "citations" in st.session_state.planner_output:
            st.session_state.messages.append(
                ("assistant", "🔍 Citation Judgement Results:"))
            st.session_state.messages.append(
                ("assistant", {"type": "json", "data": st.session_state.planner_output["citations"]}))

        """
            # Use Citation Agent to evaluate planner output
            citation_results = []
            for req in st.session_state.planner_output["requirements"]:
                req_text = req["requirement_text"]
                context_text = req.get("context", "")
                llm_response = req.get("llm_response", "")
                evaluation = orchestrate_reporter.evaluate_response(req_text, context_text, llm_response)
                citation_results.append(evaluation)
            st.session_state.planner_output["citations"] = citation_results
            st.session_state.messages.append(("assistant", {"type": "json", "data": citation_results}))
        """

        st.session_state.messages.append(("assistant", "Would you like me to execute them? (yes/no)"))
        st.session_state.stage = "ask_to_execute"
        st.rerun()

elif st.session_state.stage == "ask_to_execute":
    user_input = st.chat_input("Execute now? yes or no", key="ask_to_execute_input")
    auto_focus_textarea()
    if user_input:
        st.session_state.messages.append(("user", user_input))
        if "yes" in user_input.lower():
            st.session_state.messages.append(("assistant", "⚙️ Executor Agent executing selected test cases..."))
            st.session_state.stage = "run_executor"
        else:
            st.session_state.messages.append(("assistant", "Alright, paused execution."))
        st.rerun()

elif st.session_state.stage == "run_executor":
    execution_df = orchestrate_executor(get_data_path("sample_validation_plan.json"))
    st.session_state.execution_df = execution_df
    st.session_state.messages.append(("assistant", f"⚙️ Executor Agent completed execution on {len(st.session_state.execution_df)} tests."))
    st.session_state.messages.append(("assistant", {"type": "dataframe", "data": execution_df}))
    st.session_state.messages.append(("assistant", "Would you like me to generate the final report? (yes/no)"))
    st.session_state.stage = "ask_to_report"
    st.rerun()

elif st.session_state.stage == "ask_to_report":
    user_input = st.chat_input("Generate report? yes or no", key="ask_to_report_input")
    auto_focus_textarea()
    if user_input:
        st.session_state.messages.append(("user", user_input))
        if "yes" in user_input.lower():
            st.session_state.messages.append(("assistant", "📊 Reporter Agent is generating report..."))
            report_summary = orchestrate_reporter(st.session_state.execution_df)
            st.session_state.report_summary = report_summary
            st.session_state.messages.append(("assistant", "📋 Summary Report"))
            st.session_state.messages.append(("assistant", {"type": "json", "data": report_summary[0]}))
            st.session_state.messages.append(("assistant", "📂 Domain Breakdown"))
            st.session_state.messages.append(("assistant", {"type": "dataframe", "data": report_summary[1]}))
            st.session_state.messages.append(
                ("assistant", "✅ All done! Would you like to start over with a new requirement file? (yes/no)"))
            st.session_state.stage = "done"
        else:
            st.session_state.messages.append(("assistant", "Alright, I'm here if you need me!"))
        st.rerun()

elif st.session_state.stage == "done":
    user_input = st.chat_input("Start over? yes or no", key="restart_input")
    auto_focus_textarea()
    if user_input:
        st.session_state.messages.append(("user", user_input))
        if "yes" in user_input.lower():
            st.session_state.clear()
            st.rerun()
        else:
            st.session_state.messages.append(("assistant", "Thank you for using the Agentic AI Validation System!"))
        st.rerun()