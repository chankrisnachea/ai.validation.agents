# executor_agent.py
import json
import random
import pandas as pd
from utils.file_utils import get_data_path

def run_executor_agent(planner_output):
    """
    Simulates test execution based on planner output (validation plan).
    Adds simulated results to each test case from the test catalog.
    Returns a pandas DataFrame.
    """
    test_catalog = planner_output.get("test_catalog", [])
    executed_results = []
    for test in test_catalog:
        result = random.choices(["PASS", "FAIL", "SKIPPED"], weights=[0.7, 0.2, 0.1])[0]
        executed_results.append({
            "id": test.get("id", ""),
            "title": test.get("title", ""),
            "domain": test.get("domain", ""),
            "category": test.get("category", ""),
            "result": result
        })

    df = pd.DataFrame(executed_results)
    return df

if __name__ == "__main__":
    from planner_agent import run_planner_agent
    from pprint import pprint

    plan = run_planner_agent(get_data_path("sample_validation_plan.json"))
    df = run_executor_agent(plan)
    pprint(df.to_dict(orient="records"))
