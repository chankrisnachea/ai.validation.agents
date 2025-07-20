# orchestrator_agent.py
import json
import pandas as pd
from agents.planner_agent import run_planner_agent
from agents.executor_agent import run_executor_agent
from agents.reporter_agent import run_reporter_agent, semantic_search
from utils.file_utils import get_data_path

def orchestrate_planner(requirement_path: str, use_llm: bool = False) -> dict:
    """
    Orchestrates the planner agent to select applicable test cases based on requirements.
    Returns a dictionary with planner output.
    """
    planner_output = run_planner_agent(requirement_path, use_llm=use_llm)
    return planner_output

def orchestrate_executor(planner_output: dict) -> pd.DataFrame:
    """
    Orchestrates the executor agent to simulate test execution based on planner output.
    Returns a pandas DataFrame with execution results.
    """
    with open(planner_output) as f:
        planner_output = json.load(f)
    execution_df = run_executor_agent(planner_output)
    return execution_df

def orchestrate_reporter(execution_df: pd.DataFrame, query=None) -> tuple:
    """
    Orchestrates the reporter agent to generate a summary and domain breakdown from execution results.
    Returns a tuple containing:
    - Summary string
    - Domain summary DataFrame
    - Full DataFrame of execution results
    - Base64 encoded chart image
    """
    summary, domain_summary, full_df, chart_base64 = run_reporter_agent(execution_df)
    semantic_results = []
    if query:
        semantic_results = semantic_search(domain_summary, full_df, query)
    return summary, domain_summary, full_df, chart_base64

def orchestrate_citation(requirement_path: str, use_llm: bool = False) -> dict:
    """
    Orchestrates the citation agent to validate planner output against requirements.
    Returns a dictionary with citation results.
    """
    with open(requirement_path) as f:
        requirements_data = json.load(f)

    planner_output = run_planner_agent(requirement_path, use_llm=use_llm)

    if use_llm:
        citations = []
        for req in requirements_data:
            req_text = req.get("requirement_text", "")
            context_text = req.get("context", "")
            llm_response = req.get("llm_response", "")
            evaluation = run_reporter_agent.evaluate_response(req_text, context_text, llm_response)
            citations.append(evaluation)
        planner_output["citations"] = citations

    return planner_output

# Serving app_dashboard.py (legacy)
def orchestrate(requirement_path, use_llm=False, query=None):
    """
    Full orchstration pipeline for Planner -> Executor -> Reporter Agents.
    Args:
        requirement_path:
        use_llm:
        query:

    Returns: (planner_output, execution_df, (summary, domain_df, full_df, chart)
    """
    # Run Planner Agent
    planner_output = run_planner_agent(requirement_path, use_llm=use_llm)

    # Run Executor Agent
    execution_df = run_executor_agent(planner_output)

    # Run Reporter Agent
    summary, domain_summary, full_df, chart_base64 = run_reporter_agent(execution_df)

    #Optionally perform semantic search
    if query:
        semantic_results = semantic_search(domain_summary, full_df, query)

    return planner_output, execution_df, (summary, domain_summary, full_df, chart_base64)

if __name__ == "__main__":
    print("Running Planner Agent...")
    plan, log = orchestrate_planner(get_data_path("requirements.json"), use_llm=True)
    print(f"Planner Output: {len(plan['test_catalog'])} test cases.\n")

    print("Running Executor Agent...")
    execution_df = orchestrate_executor(plan)
    print(f"Executor Output: {len(execution_df)} tests.\n")

    print("Running Reporter Agent...")
    summary, domain_summary, full_df, chart_base64 = orchestrate_reporter(execution_df)
    print("Reporter Output:")
    print(json.dumps(summary, indent=4))
