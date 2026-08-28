# Agentic AI RAG System

A simple two-agent RAG system built with **LangGraph**.

The system consists of:

* **Report Generator Agent** — receives the user's question and produces the final response.
* **Data Retrieval Agent** — retrieves relevant information from `knowledge_base.txt`.
* **`multiple_keyword_search` tool** — performs local fuzzy keyword retrieval over `knowledge_base.txt` and returns ranked, relevant text chunks.

The project demonstrates multi-agent orchestration, custom RAG retrieval, tool calling, and prompt design.

The current implementation is a runnable workflow: LangGraph coordinates the agents, the configured LLM provider handles tool calls and synthesis, and the retrieval tool searches the local knowledge base.

Tool-call routing follows each agent's own state memory so report and retrieval tool calls reach the correct next node.

---

## System Architecture and Flowchart

The system uses two agents in sequence. The Report Generator starts with the user question and the Data Retriever supplies the evidence needed to produce a grounded final response.

### Report Generator Agent

The Report Generator is the orchestration and answer-synthesis agent. It evaluates the question, can answer simple requests without a retrieval handoff, and uses `helper_search_data` when it needs supporting evidence. For ambiguous policy questions, its prompt directs it to request a broad discovery search before answering or asking a focused clarification question. A retrieval tool call routes directly to the Data Retriever subgraph; when that agent returns, the Report Generator receives the retrieval summary and raw context, then produces the final user-facing answer.

### Data Retriever Agent

The Data Retriever receives the original question and the Report Generator's retrieval request. It expands the request into a focused keyword list and calls `helper_keyword_search`, which routes to the custom `multiple_keyword_search` tool. The tool returns ranked text chunks from the local knowledge base. The Data Retriever reviews the returned evidence and can request another search when it considers the evidence insufficient. When it has finished, it returns both a concise retrieval summary and deduplicated raw chunks to the Report Generator through the shared state.

![System Flowchart](./assets/flowchart.png)

---

## Graph Engineer 

LangGraph is used to control the workflow between the two agents.

The retrieval process can loop when the Data Retrieval Agent determines that more information is required. Once sufficient evidence has been retrieved, the result is returned to the Report Generator to generate the final response.

![LangGraph Design](./assets/graph_design.png)

---

## State Artifacts

| Field | Stores | Written by | Read by / purpose |
| --- | --- | --- | --- |
| `query` | User question | `main.py` / `run_and_log.py` | Both agents use it to retrieve and answer. |
| `conversation` | Shared conversation list | Entry points initialize it | Reserved shared context; not updated by the current nodes. |
| `summary_agent_state_memory` | Report Agent messages and retrieval return message | Report Generator; Data Retriever appends the return `ToolMessage` | Data Retriever finds the Report Agent's latest tool request; Report Generator receives its returned evidence. |
| `final_report` | Final user-facing answer | Report Generator | `main.py` and `run_and_log.py` display or save it. |
| `search_agent_state_memory` | Retriever messages and local-search tool results | Data Retriever and `search_tool` | `search_tool` finds the latest keyword tool call; Data Retriever reviews prior results. |
| `retrieved_context` | Retriever's short evidence summary | Data Retriever | 	Report Generator grounds its summary on these chunks; Saved in the Markdown run log. |
| `retrieved_context_raw` | Deduplicated raw knowledge-base chunks | Data Retriever | Report Generator grounds its answer on these chunks; the run log preserves them. |
| `search_attempts` | Number of local searches | `search_tool` increments it | Recorded in state; not currently used for routing. |
| `max_search_attempts` | Intended search limit | Entry points initialize it | Reserved configuration; not currently enforced. |

---

## Ideal Graph Design

In a real-world implementation, I would likely prefer a **grep-based / file-based RAG approach** for this use case. Recent research suggests that it can outperform traditional vector retrieval in several scenarios, especially when the searchable knowledge base is relatively small and well-structured.

Even when using a vector database, I believe each vector store should remain **small and domain-specific**. Instead of placing all knowledge into one large index, the data should be separated by category or domain, with the agent selecting the appropriate retrieval tool when needed. This reduces unnecessary search space, retrieval latency, and irrelevant context.

However, since this is an assignment, I kept this as an **ideal design** and implemented only the retrieval approach required by the assignment.
![Ideal Design](./assets/ideal_design.png)

---

## Planned Retrieval Approach

The system uses a lightweight custom RAG mechanism instead of a vector database.

The Data Retrieval Agent:

1. Interprets the user's question.
2. Generates or expands relevant search keywords.
3. Calls `multiple_keyword_search`.
4. Reviews the retrieved snippets.
5. Performs another search if the available evidence is insufficient.
6. Returns relevant raw snippets to the Report Generator.

The retrieval tool searches sections inside `knowledge_base.txt`, ranks matching sections, removes duplicate results, and passes unique raw retrieval artifacts to the summary agent alongside the retrieval summary.

If no supporting information is available, the system avoids generating unsupported facts.

---

## Retrieval Design

`multiple_keyword_search` is a custom local retrieval tool designed for this assignment: on each tool call, it loads `knowledge_base.txt`, splits the file into chunks using `---`, and compares up to five normalized search keywords with every chunk using RapidFuzz `partial_ratio`. A chunk is retained when at least one keyword reaches the similarity threshold of `70`; results are then reranked by the number of matched keywords and their average similarity score, deduplicated by chunk content, and limited to the top 10 results. Each returned chunk preserves its source section and matched keywords so the agents can ground the final answer in the retrieved evidence. Loading and scanning the text file for every query keeps the implementation simple and aligned with the assignment, but a production system would normally cache or index the knowledge base rather than reload it on every search.

---

## Planned Reliability & Safety Handling

- **Ambiguous queries:** The agent asks a clarifying question when the user's intent is unclear.
- **No relevant information:** If no supporting evidence is found, the agent clearly states that the knowledge base does not contain enough information.
- **Out-of-scope queries:** Questions unrelated to the configured knowledge domain are politely declined.
- **System or retrieval errors:** If an error occurs, the system returns an error code and informs the user that the requested information could not be retrieved.
- **Tool-use limit (Not implemented yet):** When `search_attempts` exceeds `max_search_attempts`, the intended behavior is to stop the workflow, raise a tool-limit error, show a clear error message, and write the error to the Markdown run log.

---

## Project Structure 

```text
.
├── assets/
│   ├── flowchart.png
│   ├── graph_design.png
│   └── ideal_design.png
│
├── result/
│   ├── normal.md
│   ├── multi_section.md
│   ├── ambiguity.md
│   ├── ambiguity_2.md
│   ├── unsupported_but_in_domain.md
│   └── out_of_scope.md
│
├── screenshots/
│   ├── normal.png
│   ├── multi_section.png
│   ├── ambiguity.png
│   ├── ambiguity_2.png
│   ├── unsupported_but_in_domain.png
│   └── out_of_scope.png
│
├── src/
│   ├── agents/
│   │   ├── report_generator.py
│   │   └── data_retriever.py
│   ├── tools/
│       └── multiple_keyword_search.py
│   ├── graph.py
│   ├── main.py
│   ├── run_and_log.py
│   └── state.py
│
├── knowledge_base.txt
├── requirements.txt
├── .env.example
└── README.md
```

---

## System Map

| System part | What it does | Key files |
| --- | --- | --- |
| Answer generation | Interprets the question, requests evidence when needed, and produces the final response. | [`report_generator.py`](./src/agents/report_generator.py) |
| Information retrieval | Expands the retrieval request, reviews search results, and returns evidence to the answer generator. | [`data_retriever.py`](./src/agents/data_retriever.py) |
| Workflow | Connects the answer and retrieval steps in a LangGraph flow. | [`graph.py`](./src/graph.py) |
| Local search | Finds, ranks, and deduplicates relevant text chunks. | [`multiple_keyword_search.py`](./src/tools/multiple_keyword_search.py) |
| Knowledge source | Stores the policy sections searched by the retrieval tool. | [`knowledge_base.txt`](./knowledge_base.txt) |
| Run evidence | Preserves representative runs, including input, output, and retrieval context. | [`result/`](./result/) |

---

## Knowledge Base

`knowledge_base.txt` is the local source of truth used by the retrieval system.

Example:

```text
[SECTION: International Travel Policy]

Employees travelling internationally must obtain manager approval
before booking flights.

---

[SECTION: Travel Expense Policy]

Approved airfare, accommodation, transportation, and meals may be
reimbursed for approved business travel.

---

[SECTION: Remote Work Policy]

Employees may work remotely for up to two days per week.
```

---

## Setup

### 1. Clone the repository

### 2. Create a virtual environment

### 3. Install dependencies

### 4. Configure environment variables

Copy `.env.example` to `.env` and provide the required API credentials.

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
# Optional: OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

Groq credentials are read from the environment and must not be committed to the repository.

For higher-quality results, the two agent files can be configured to use an
OpenAI API key and a larger OpenAI model instead. Set `OPENAI_API_KEY` in
`.env`, then update both agents to select the OpenAI provider.

---

## Run

```bash
python -m src.main
```

The retrieval tool imports the shared graph state only for type checking, avoiding a runtime circular import during application startup.

`search_tool` accepts LangChain-normalized AI tool calls in `GraphState` and returns the retrieval result as a `ToolMessage`.

Example question:

```text
What is the policy on international travel?
```

## Run with Markdown Logs

To save each run as a Markdown record, including the input, final response,
retrieval-agent responses, and raw retrieved context, run:

```bash
python -m src.run_and_log
```

Logs are saved to the ignored `run_logs/` directory.

---

## Current Test Results

Each scenario has a full Markdown log and a matching screenshot. The log shows
the input, final answer, retrieval-agent response, and raw retrieved context;
the screenshot is a quick visual record of the run.

| Scenario | Input | Response format | Full log | Screenshot |
| --- | --- | --- | --- | --- |
| Normal retrieval | `Do I need manager approval before an international business flight?` | Direct evidence-grounded answer, followed by key policy points. | [normal.md](./result/normal.md) | [View screenshot](./screenshots/normal.png) |
| Multi-section retrieval | `What expenses can I claim for an approved international trip, and what receipts are needed?` | Direct answer with a comparison table of claimable expenses, receipt requirements, and known gaps. | [multi_section.md](./result/multi_section.md) | [View screenshot](./screenshots/multi_section.png) |
| Broad policy query | `What is the travel policy?` | Consolidated policy overview structured by topic, using retrieved domestic and international travel sections. | [ambiguity_2.md](./result/ambiguity_2.md) | [View screenshot](./screenshots/ambiguity_2.png) |
| Ambiguous request without context | `can you serch me the policy?` | Concise clarification request that asks the user to identify the policy domain. | [ambiguity.md](./result/ambiguity.md) | [View screenshot](./screenshots/ambiguity.png) |
| Unsupported but in-domain | `What is the maternity leave policy?` | States that the knowledge base has no reliable maternity-leave policy, then asks for the missing scope and details. | [unsupported_but_in_domain.md](./result/unsupported_but_in_domain.md) | [View screenshot](./screenshots/unsupported_but_in_domain.png) |
| Out of scope | `What is the weather in Bangkok tomorrow?` | States that no weather forecast is available in the current data and asks for clarification rather than inventing an answer. | [out_of_scope.md](./result/out_of_scope.md) | [View screenshot](./screenshots/out_of_scope.png) |

---

## Tech Stack

* Python
* LangGraph
* LangChain
* OpenAI-compatible LLM API
* Local text-based knowledge base
