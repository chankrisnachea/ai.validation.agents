# 🧠 AI Validation Agents (Agentic AI Validation System)

**AI Validation Agents** is an open-source framework that implements the Agentic AI Validation System — a modular, multi-agent architecture for orchestrating validation workflows using autonomous AI agents that collaboratively plan, execute, and analyze tests in an intelligent and modular fashion.

This project introduces a flexible, agent-based architecture that leverages large language models (LLMs), automation tools, and structured coordination to streamline system testing at scale—enhancing efficiency, consistency, and insight-driven decision-making.

**We’re building an AI Validation Agents that owns the validation lifecycle.**

The system is composed of specialized agents that:
- Act with autonomy and initiative  
- Collaborate like a high-performing virtual team  
- Continuously learn and adapt based on outcomes and feedback

---

## 🧩 Architecture Overview

### 🧱 Core Agents

#### 🧠 Orchestrator Agent
- Interfaces with users to receive prompts or validation requirements
- Orchestrates and delegates tasks to other specialized agents
- Synthesizes results and manages the overall validation workflow
- Renders results in a user-friendly format via Streamlit UI

#### 🧠 Planner Agent
- Selects test cases based on product requirements and applicability logic
- Plans HW/SW configurations
- Interfaces with external requirement and test case sources
- Outputs a structured validation plan

#### ⚙️ Executor Agent
- Executes test flows (mocked or real)
- Manages scheduling and system state
- Interfaces with test automation and results management components
- Returns execution results as structured data

#### 📊 Reporter Agent
- Analyzes test outcomes, generates visual summaries, and flags regressions
- Provides semantic search over test results (via embedding + FAISS)
- Outputs summary charts, dashboards, and defect hotspots

#### 🧑‍⚖️ Citation Agent 
- Evaluates LLM responses from the Planner Agent based on requirements and retrieved context
- Supports multiple planner responses (batch evaluation)
- Outputs citations to enhance transparency and traceability

---

## 🔁 Agent Workflow

```
                  
                                         User  
                                           ^                              
                Prompt/Upload product req  │
                                           │ Response
                                           ▼
                                  ┌────────────────────┐         
                   ┌─────────────>│ Ochestrator Agent  │<─────────┐ 
                   │              └────────────────────┘          │                      
          ┌────────────────────┐           ^                      │
          │  Citation Agent    │           │                      │
          └────────┬───────────┘           │                      │
        Evaluate LLM response    Orchestrates workflows           │
                   │          Delegates tasks to other agents     │
                   │                       │                      │
                   ▼                       ▼                      ▼
          ┌────────────────────┐ ┌────────────────────┐  ┌────────────────────┐
          │  Planner Agent     │ │  Executor Agent    │  │  Reporter Agent    │
          └────────┬───────────┘ └────────┬───────────┘  └────────┬───────────┘
        Generates test plans      Executes test plans     Analyzes test results
        based on rules/LLMs       Manages results         Suggets trends
                                  and issues debug        Generates insights
             
```

---

## ✅ Features

- 🤖 **Agentic Architecture**
  - Orchestrator Agent: Coordinates agent workflows and chat-based UI
  - Planner Agent: Selects test cases based on rule or LLM logic
  - Citation Agent: Evaluates LLM output based on the requirements and RAG context
  - Executor Agent: Simulates test execution and generates pass/fail data
  - Reporter Agent: Generates validation summary, charts, and insights
  
- 🧠 **LLM-Powered Planning**
  - Supports both rule-based and embedding+LLM-based applicability logic
  - Integrates Retrieval-Augmented Generation (RAG) to ground LLM with internal knowledge base
  - Embedding models: `bge-base-en-v1.5-int8-ov` (OpenVINO-optimized models) or `MiniLM`
  - LLMs: Mistral or Ollama-compatible models

- 💬 **Chat UI (Streamlit)**
  - Interactive multi-turn chat flow simulates agent conversations
  - Dynamically updates state, outputs charts, reports, and test results

- 📊 **Mock Validation Plan and Results**
  - Inputs and outputs are based on realistic mock samples of requirements and test case data

---

## 📁 Project Structure

```
.
├── config/                         # Configuration files
├── data/                           # Sample input/output files
│   ├── requirements.json
│   ├── tcd_baseline.json
│   └── sample_validation_plan.json
├── docs/                           # Internal documentation (used for RAG)
│   └── internal_guides/            # The more relevant internal documents, the better for RAG context
├── rag_index/                      # Persisted vector index from RAG ingestion
├── src/                            # Core logic (modularized)
│   ├── agents/                     # Core AI agents
│   │   ├── __init__.py
│   │   ├── citation_agent.py
│   │   ├── executor_agent.py
│   │   ├── orchestrator_agent.py
│   │   ├── planner_agent.py
│   │   └── reporter_agent.py
│   ├── api/                        # Future FastAPI server for agent APIs
│   ├── rag/                        # RAG folder
│   │   ├── __init__.py             
│   │   ├── rag_pipeline.py         # Rag Pipeline
│   ├── ui/                         # Streamlit UIs
│   │   ├── __init__.py             
│   │   ├── app_chat.py             # Conversational interface
│   │   └── app_dashboard.py        # Legacy
│   └── utils/                      # Shared helpers/utilities
│       └── __init__.py
│       └── extract_metadata.py
│       └── file_utils.py       
│       └── xlsx_to_json_coverter.py    
├── .gitignore                       
├── LICENSE                      
├── README.md                       
├── requirements.txt                # Python dependencies
└── run_app.py                      # Python wrapper to run the Streamlit app
```
---

## 🛠️ Installation & Setup

```bash
# Clone the repo
git clone https://github.com/chankrisnachea/ai.validation.agents.git
cd ai.validation.agents

# Create and activate virtual environment (cross-platform)
python -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows (PowerShell):
# .\.venv\Scripts\Activate.ps1
# Or on Windows (cmd.exe):
# .\.venv\Scripts\activate.bat

# Upgrade pip inside the venv (optional but recommended)
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH environment variable
# On macOS/Linux:
export PYTHONPATH=$(pwd)/src

# On Windows (PowerShell):
# setx PYTHONPATH "$(Resolve-Path src)"

# On Windows (cmd.exe):
# setx PYTHONPATH "%cd%\src"
```
---

## 🖥️ Running the App
```bash
# From root directory
# Run rag_pipeline.py first to process the docs in docs/ and build rag context stored in rag_index/ 
$ python src/rag/rag_pipeline.py

# Launch Streamlit app_chat UI 
$ python run_app.py
```

---

## 🧪 Sample Data
Place your input JSON files in the `/data` folder:
- `requirements.json`: Product requirements
- `tcd_baseline.json`: Test case database
- `sample_validation_plan.json`: Output validation plan

---

## 🛣️ Roadmap
- [x] Modular agent architecture
- [x] Rule-based test selection
- [x] Embedding + LLM-based test selection
- [x] Streamlit chat interface
- [x] RAG integration
- [x] Citation agent for traceability response validation
- [ ] External entreprise tool integration (optional)
- [ ] Performance tuning for local LLMs and embeddings
- [ ] REST API via FastAPI
- [ ] Enhanced UI/UX
- [ ] Agent Learning Loop (adaptive planning & prioritization)
- [ ] Human-in-the-Loop Controls (engineers approve, override, fine-tune agent decisions)
- [ ] Deployment: Docker, CI/CD, remote hosting

---

## 🧩 Optional: External Enterprise Tool Integration

This project is designed with enterprise extensibility in mind. While it works standalone for prototyping, it can scale and integrate with internal tools and frameworks commonly found in larger organizations.

Potential integrations include:

- Product Requirement Management Systems
  - Parse or sync requirements from tools like DOORS, Jama, Confluence, or other internal tools
  - Automate requirement-to-test mapping and coverage reporting
- Test Case Management Systems
  - Pull test cases and applicability metadata from Polarion, TestRail, Zephyr, or other internal tools.
  - Push results or test runs back to the system
- Hardware Resource & Lab Managers
  - Interface with internal schedulers or lab inventory systems
  - Automatically allocate or deallocate SKUs, boards, etc.
- Automation Frameworks
  - Integrate with internal CI/CD pipelines, Jenkins-based test orchestrators or other internal tools
  - Orchestrate test automation campaign
- Bug/Defect Tracking Tools
  - Integrate with JIRA, Bugzilla, or other internal tools.
  - Auto-file issues in from failed executions
- Program Dashboards
  - Sync validation metrics into existing business dashboards (e.g., Power BI, Tableau)
  - Export coverage heatmaps, efficiency scores, etc.

Note: These integrations are modular and optional. They are intended to support enterprise-level workflows where internal tools are already in use. Adapter modules can be developed independently and plugged into the agent system.

---

## 👥 Contributors

- Chankrisna Chea (project lead, architect, developer)

---

## 🧠 Disclaimer

This is a personal, independent project showcasing an AI-driven approach to validation workflows.
It is **not affiliated with or representative of any current or former employer.**

---

## 📜 License

Licensed under the **Apache License, Version 2.0.**

See the [LICENSE](./LICENSE) file for full details.

---

## 🔁 Git Workflow for Collaborators

```bash
# Clone the repo (for the first time)
git clone https://github.com/chankrisnachea/ai.validation.agents.git
cd ai.validation.agents

# Create a feature or fix branch
git checkout -b my-feature-branch

# Make changes and commit
git add .
git commit -m "Add new feature or fix bug"

# Push changes to GitHub remote
git push origin my-feature-branch
```
Then, on GitHub:
- Go to the repository
- You'll see a prompt: "Compare & pull request" -> Click it.
- Add a title, description, and create the Pull Request.
---
