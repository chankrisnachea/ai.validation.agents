# citation_agent.py

import json
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage

# Initialize LLM
llm = ChatOllama(model="mistral")

# System prompt for citation/judge agent
system_prompt = SystemMessage(
    content="""
    You are a validation citation and judgment agent. Your job is to assess whether the response from a Planner Agent is grounded in the provided document context.

    For each response, return a JSON object with:
    - verdict: \"Supported\", \"Partially Supported\", or \"Unsupported\"
    - explanation: Reasoning for the verdict
    - confidence: Score from 0-100
    - citations: Exact sentences or phrases from the context that support the output

    Respond only in valid JSON format.
    """
)

def evaluate_response(query_text, context_text, llm_response):
    """
    Evaluate LLM output using supporting document context.

    Args:
        query_text (str): Original requirement or user query
        context_text (str): Retrieved document snippets (from RAG)
        llm_response (str): Planner Agent response

    Returns:
        dict: Evaluation result with verdict, confidence, explanation, and citations
    """
    prompt = HumanMessage(
        content=f"""
        Query:
        {query_text}

        Context:
        {context_text}

        LLM Response:
        {llm_response}
        """
    )

    response = llm.invoke([system_prompt, prompt])

    try:
        return json.loads(response.content)
    except Exception:
        return {
            "verdict": "Error",
            "confidence": 0,
            "explanation": "Unable to parse model response.",
            "citations": []
        }

def batch_evaluate_responses(requirements, context_text, planner_outputs):
    """
    Evaluate multiple planner responses.

    Args:
        requirements (list[str]): List of requirement texts
        context_text (str): Shared RAG context used in reasoning
        planner_outputs (list[str]): LLM outputs per requirement

    Returns:
        list[dict]: List of judgment results
    """
    results = []
    for req, resp in zip(requirements, planner_outputs):
        result = evaluate_response(req, context_text, resp)
        results.append(result)
    return results


# Example usage
if __name__ == "__main__":
    query = "System must support MS States with WiFi"
    context = "Modern Standby with WiFi is validated by TCID 1111111111."
    response = "Test case 1111111111 validates MS States with WiFi as required."

    result = evaluate_response(query, context, response)
    print(json.dumps(result, indent=2))
