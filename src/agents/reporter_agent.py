# reporter_agent.py
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from utils.file_utils import get_data_path
import faiss
import matplotlib.pyplot as plt
import io
import base64
import streamlit as st

model = SentenceTransformer("all-MiniLM-L6-v2")

def run_reporter_agent(execution_df):
    """
    Analyzes the test execution DataFrame and summarizes results.
    Returns summary statistic, domain breakdown, chart image, and the DataFrame.
    """
    summary = {
        "total": len(execution_df),
        "passed": (execution_df["result"] == "PASS").sum(),
        "failed": (execution_df["result"] == "FAIL").sum(),
        "skipped": (execution_df["result"] == "SKIPPED").sum()
    }

    summary["pass_rate"] = (summary["passed"] / summary["total"]) * 100 if summary["total"] > 0 else 0
    summary["fail_rate"] = (summary["failed"] / summary["total"]) * 100 if summary["total"] > 0 else 0
    summary["skip_rate"] = (summary["skipped"] / summary["total"]) * 100 if summary["total"] > 0 else 0

    domain_summary = execution_df.groupby(["domain", "result"]).size().unstack(fill_value=0)

    descriptions = execution_df["title"].fillna("").tolist()
    embeddings = model.encode(descriptions, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # Generate summary chart
    fig, ax = plt.subplots()
    labels = ["passed", "failed", "skipped"]
    values = [summary[label] for label in labels]
    ax.bar(labels, values, color=['green', 'red', 'gray'])
    ax.set_title("Validation Summary")
    ax.set_ylabel("Number of Tests")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    return summary, domain_summary, execution_df, chart_base64

def semantic_search(index, df, query, k=3):
    query_vector = model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_vector, k)
    matches = []
    for i in I[0]:
        row = df.iloc[i]
        matches.append({
            "id": row["id"],
            "title": row["title"],
            "domain": row["domain"],
            "result": row["result"]
        })
    return matches

if __name__ == "__main__":
    from executor_agent import run_executor_agent
    from planner_agent import run_planner_agent
    from pprint import pprint

    plan = run_planner_agent(get_data_path("sample_validation_plan.json"))
    df = run_executor_agent(plan)
    summary, domain_summary, full_df, chart = run_reporter_agent(df)
    pprint(summary)
    pprint(domain_summary)
    matches = semantic_search(domain_summary, full_df, "power test failures")
    pprint(matches)
