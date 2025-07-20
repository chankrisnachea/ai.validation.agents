# planner_agent.py

import json
import numpy as np
from pathlib import Path
from llama_index.legacy.embeddings import LangchainEmbedding, HuggingFaceEmbedding
from sentence_transformers import SentenceTransformer, util
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore

from agents.citation_agent import evaluate_response
from utils.file_utils import get_data_path

INDEX_DIR = "rag_index"

# === Load RAG Query Engine ===
def load_rag_query_engine():
    print("Loading RAG vector index from:", INDEX_DIR)
    storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    return query_engine

# === Load RAG Context for prompting ===
def get_rag_context():
    print(f"Loading RAG index from {INDEX_DIR}")

    # Use the same local embedding model used during RAG ingestion
    local_embed_model = LangchainEmbedding(
        HuggingFaceEmbeddings(
            model_name="BAAI/bge-base-en-v1.5"
        )
    )
    storage_path = Path(INDEX_DIR)
    if not storage_path.exists():
        print("RAG index not found, Please run rag_pipeline.py to ingest documents.")
        return ""
    vector_store = FaissVectorStore.from_persist_dir(INDEX_DIR)
    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_DIR,
        vector_store=vector_store
    )
    index = load_index_from_storage(storage_context, embed_model=local_embed_model)
    retriever = index.as_retriever(similarity_top_k=3)
    retrieved_nodes = retriever.retrieve("Validation Planning")
    return "\n".join([n.text for n in retrieved_nodes])


# === Embedding Model ===
#try:
#    embedder = SentenceTransformer("OpenVINO/bge-base-en-v1.5-int8-ov") # TODO: To find better embedding model later
#except Exception:
#    print("OpenVINO model not found, falling back to default model.")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# === LLM Setup ===
llm = ChatOllama(model="mistral")  # TODO: Evaluate "llama3" later

system_prompt = SystemMessage(
    content="""
    You are a validation architect planning agent.
    Given a requirement and a list of test cases, identify the most relevant and applicable test cases that would validate the requirement.
    Respond in JSON array format with at least 2 test cases with each test case containing fields: 
    id (e.g., 1111111111 or 2222222222), title, domain (e.g., power_management or connectivity.wifi), validation_category (e.g., CAT2 or CAT3).
    These fields must be derived from the list of test cases.
    """
)

def get_requirement_text(req):
    req_id = req.get("id", "").strip()
    title = req.get("title", "").strip()
    desc = req.get("description", "").strip()
    parts = [f"[{req_id}]" if req_id else "", title, desc]
    return " — ".join(part for part in parts if part)

def rule_based_selection(requirements, test_cases):
    selected = []
    required_applicability = set()
    for req in requirements:
        required_applicability.update(req.get("applicability", []))
    for tc in test_cases:
        if set(tc.get("applicability", [])) & required_applicability:
            selected.append({
                "id": tc["id"],
                "title": tc["title"],
                "domain": tc["domain"],
                "validation_category": tc["validation_category"]
            })
    return selected

def llm_based_selection(req_text, test_cases, rag_context):
    if rag_context:
        req_text_with_rag = f"{req_text}\n\nReference Documents:\n{rag_context}"
    else:
        req_text_with_rag = req_text

    req_embedding = embedder.encode(req_text_with_rag, convert_to_tensor=True)
    test_embeddings = embedder.encode(
        [str(tc.get("title", "")) + " " + str(tc.get("description", "")) for tc in test_cases if isinstance(tc, dict)],
        convert_to_tensor=True
    )
    cosine_scores = util.cos_sim(req_embedding, test_embeddings)[0].cpu().numpy()
    ranked_indices = np.argsort(-cosine_scores)[:5]
    ranked_tests = [test_cases[i] for i in ranked_indices]

    tc_block = "\n".join(f"{tc['id']}: {tc['title']}" for tc in ranked_tests)
    user_prompt = HumanMessage(
        content=f"""
            Requirement:
            {req_text_with_rag}

            Test Cases:
            {tc_block}

            Respond ONLY with a JSON array of the most relevant test IDs (e.g., 2206738500) that validate this requirement.
            No explanation. Each item must include: id, title, domain, validation_category.
        """
    )

    response = llm.invoke([system_prompt, user_prompt])
    raw_output = response.content
    print("\n>> Raw LLM Response:\n", raw_output)

    try:
        parsed = json.loads(raw_output)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return parsed.get("selected_test_case", [])
        else:
            return []
    except Exception as e:
        print("X Failed to parse LLM response:", e)
        return []

def run_planner_agent(validation_plan_path, use_llm=False):
    with open(get_data_path("requirements.json")) as f:
        requirements_data = json.load(f)

    with open(get_data_path("tcd_baseline.json")) as f:
        all_test_cases = json.load(f)

    with open(validation_plan_path) as f:
        validation_plan = json.load(f)

    all_selected = []
    all_citations = []
    rag_context = get_rag_context() if use_llm else ""

    if use_llm:
        for req in requirements_data:
            req_text = get_requirement_text(req)
            selected = llm_based_selection(req_text, all_test_cases, rag_context)
            print("Selected from LLM:", selected)
            all_selected.extend(selected)

            # Evaluate citations
            citation = evaluate_response(req_text, rag_context, json.dumps(selected))
            all_citations.append(citation)
    else:
        all_selected = rule_based_selection(requirements_data, all_test_cases)
        if "citations" in validation_plan:
            del validation_plan["citations"]

    validation_plan["test_catalog"] = all_selected
    print(" Final test_catalog before writing to json: ", validation_plan["test_catalog"])

    if use_llm:
        validation_plan["citations"] = all_citations

    with open(validation_plan_path, "w") as f:
        json.dump(validation_plan, f, indent=4)


    return validation_plan

if __name__ == "__main__":
    rag_engine = load_rag_query_engine()
    response = rag_engine.query("What is NVL?")
    print(response)

    plan = run_planner_agent(get_data_path("sample_validation_plan.json"), use_llm=True)
    print("\n✅ Validation plan updated with selected test cases")
