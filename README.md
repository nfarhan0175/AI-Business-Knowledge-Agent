# AI Business & Knowledge Agent

An AI agent that answers business questions about the Olist e-commerce dataset by routing each question to the right tool: a text-to-SQL pipeline for structured database questions, a Pandas-based analysis layer for calculations like growth and percentages, or a RAG pipeline for policy/process questions answered from a business knowledge document.

The project is built around a [LangGraph](https://github.com/langchain-ai/langgraph) state machine that handles routing, tool execution, retries, conversational memory, and error handling in one coherent workflow.

## Project Status

🚧 **Actively under development.** Core pipelines (SQL, analysis, RAG, routing, memory) are implemented and runnable end-to-end from the command line. There is no packaged CLI, API, or UI yet — see [Limitations](#limitations-and-known-gaps) below.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Example Use Cases](#example-use-cases)
- [Setup and Usage](#setup-and-usage)
- [RAG Evaluation](#rag-evaluation)
- [Limitations and Known Gaps](#limitations-and-known-gaps)
- [About This Project](#about-this-project)

---

## Features

### ✅ Completed

- **LangGraph workflow orchestration** — a `StateGraph` with dedicated nodes for memory rewriting, routing, each tool, retries, formatting, and error handling, wired together with conditional edges.
- **LLM-based tool routing** — uses Gemini's native function calling (`google-genai`) to decide between `sql_tool`, `analysis_tool`, and `rag_tool` based on the question, rather than keyword matching.
- **Text-to-SQL pipeline** — generates SQLite queries from natural language, grounded in the database schema introspected live via `PRAGMA table_info`, so the prompt always reflects the actual tables/columns.
- **SQL safety validation** — queries are checked to ensure they start with `SELECT` and contain none of `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `REPLACE`, or `TRUNCATE` before execution.
- **Self-correcting SQL retries** — if a generated query fails, the failed SQL and the database error are sent back to Gemini to produce a corrected query, orchestrated through the graph's retry node (up to 2 attempts).
- **Pandas-based analysis layer** — built on top of the SQL pipeline, with helpers for percentage breakdowns, period-over-period growth, top-N / bottom-N ranking, and automatic detection of the relevant numeric column.
- **RAG pipeline for business knowledge** — a custom sentence-aware chunker (sentence splitting + word-count-based grouping with overlap) processes a business knowledge PDF, embeds chunks with Gemini (`gemini-embedding-001`), and stores them in a persistent **ChromaDB** collection.
- **Grounded RAG answers** — retrieval filters results by a maximum distance threshold, and the answer-generation prompt explicitly instructs the model to answer only from retrieved context and say so if the answer isn't found, rather than guessing.
- **Conversational memory** — a `MemorySaver` checkpointer gives each session a persistent thread, and a dedicated memory node rewrites follow-up questions (e.g. "what about their percentages?") into standalone questions using the prior conversation turns before routing.
- **Centralized error handling** — tool failures and routing failures funnel into a dedicated error node that returns a readable message instead of letting the graph crash.
- **RAG evaluation harness** — a separate evaluation module runs a fixed question set against the RAG pipeline and scores it two ways: expected-keyword matching in the answer, and whether the expected source document was actually retrieved. A second script uses Gemini as an LLM judge to score whether each answer is faithfully grounded in its retrieved context, with results aggregated into a summary report.
- **ETL pipeline for the structured data** — scripts to inspect the raw Olist CSVs, clean and type-convert them (date parsing, missing category handling), and load them into a local SQLite database (`olist.db`) with `customers`, `orders`, `order_items`, `payments`, and `products` tables.

### 🔧 In Progress

- Expanding and stabilizing the RAG evaluation question set (currently a small, fixed set — see [RAG Evaluation](#rag-evaluation)).
- Hardening the SQL retry/error paths for a wider range of malformed or ambiguous questions.
- Consolidating model configuration (the main agent and the evaluation script currently reference different Gemini model names — see [Limitations](#limitations-and-known-gaps)).

### 📋 Planned / Possible Next Steps

*These are natural next steps based on current gaps in the codebase, not a confirmed roadmap.*

- A proper entrypoint — CLI command or a minimal API — instead of the current script-level test loop.
- An automated test suite (the existing `test_database.py` is a manual script, not an automated test).
- Dependency version pinning across the board and a reproducible environment setup (e.g. Docker).
- A larger, more systematic RAG evaluation set with tracked results over time.

---

## Architecture

Every question flows through a single LangGraph state machine:

```
START
  │
  ▼
memory node 
  │              
  ▼
router node 
  │                
  │
  ├──► sql node ───────┐
  ├──► analysis node   ┼
  └──► rag node ───────┘
         │
         ▼ 
  formatter node 
         │
         ▼
        END
```

- **SQL path:** `question → generate SQL (schema-aware prompt) → validate → execute against SQLite → format result`. On failure, the failed query and error message are fed back into a correction prompt before retrying.
- **Analysis path:** reuses the SQL generation/execution step, then loads the result into a Pandas DataFrame for percentage, growth, or top/bottom-N calculations.
- **RAG path:** `question → embed query → similarity search in ChromaDB (distance-filtered) → build context from matched chunks → Gemini answers from that context only`.

---

## Tech Stack

| Area | Tools |
|---|---|
| Orchestration | LangGraph (`StateGraph`, conditional edges, `MemorySaver` checkpointer) |
| LLM / Embeddings | Google Gemini via `google-genai` (`gemini-2.5-flash` for generation/routing, `gemini-embedding-001` for embeddings) |
| Vector store | ChromaDB (persistent, local) |
| Structured data | SQLite (via Python's `sqlite3`), Pandas, NumPy |
| Document processing | `pypdf` for PDF text extraction, a custom sentence/overlap chunker |
| Conversation state | `langchain-core` message types (`HumanMessage`, `AIMessage`) |
| Config | `python-dotenv` |
| Language | Python |

---

## Example Use Cases

These reflect what the router is actually designed to dispatch, based on `tool_router.py`'s tool descriptions:

- **Direct database questions → SQL tool**
  _"What are the top 5 product categories by revenue?"_
  _"How many orders were delivered late?"_

- **Analytical / calculated questions → Analysis tool**
  _"What is the month-over-month revenue growth?"_
  _"What percentage of total revenue does each payment type represent?"_

- **Policy / process / descriptive questions → RAG tool**
  _"Can I get a refund?"_
  _"What happens after a customer places an order?"_
  _"What products does Olist sell?"_

- **Follow-up questions → Memory node rewrites them first**
  _"What about their percentages?"_ (after a top-5-categories question) is rewritten into a standalone question using the prior turn before being routed.

---

## Setup and Usage

### 1. Clone and install dependencies

```bash
git clone https://github.com/nfarhan0175/AI-Business-Knowledge-Agent.git
cd AI-Business-Knowledge-Agent
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Set up environment variables

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_google_gemini_api_key
```

### 3. Add the raw dataset

The dataset scripts expect the [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) CSVs in `data/raw/`:

```
data/raw/olist_customers_dataset.csv
data/raw/olist_order_items_dataset.csv
data/raw/olist_order_payments_dataset.csv
data/raw/olist_orders_dataset.csv
data/raw/olist_products_dataset.csv
```

### 4. Build the structured database

```bash
python -m app.dataset.clean_data
python -m app.dataset.create_database
```

This produces `data/database/olist.db`, used by the SQL and analysis tools.

### 5. Ingest the RAG knowledge document

The business knowledge PDF (`data/documents/olist_business_guide.pdf`) is already included in the repo. Run:

```bash
python -m app.rag.ingest
```

This chunks the PDF, generates embeddings, and populates a local ChromaDB collection at `data/chroma_db/`.

### 6. Run the agent

```bash
python -m app.graph.workflow
```

This currently runs an interactive loop in the terminal (defined under `workflow.py`'s `__main__` block) that prompts for a question, routes it through the graph, and prints the final answer.

---

## RAG Evaluation

The `rag_evaluation/` module runs a fixed set of questions through the RAG pipeline and scores the results two ways:

1. **Keyword matching** — checks whether expected keywords appear in the generated answer.
2. **Retrieval check** — checks whether the expected source document was among the retrieved chunks.
3. **Faithfulness (LLM judge)** — a separate pass asks Gemini to judge whether each answer is actually supported by its retrieved context, returning a grounded/not-grounded flag and a 0–1 score.

The most recent run (`evaluation_summary.json`), on a **10-question set**, produced:

| Metric | Result |
|---|---|
| Questions evaluated | 10 (9 succeeded, 1 failed) |
| Average keyword score | 0.74 |
| Retrieval success rate | 1.0 (10/10 successful runs retrieved the expected source) |

This is a small, manually curated test set meant to sanity-check the pipeline during development — not a statistically robust benchmark. One question in the set intentionally probes the system with information not present in the document (e.g. a fabricated executive detail) to check that the RAG tool correctly declines to answer rather than hallucinating.

---

## Limitations and Known Gaps

- **No dedicated entrypoint yet.** The agent currently runs through a manual test loop in `workflow.py`, not a packaged CLI or API.
- **No automated tests.** `test_database.py` is a manual script of print statements for spot-checking the database, not a pytest suite.
- **Local-only, no deployment.** Everything runs locally against a SQLite file and a local ChromaDB directory; there is no hosted version.
- **No frontend/UI.** Interaction is entirely through the terminal.
- **Dependency pinning is inconsistent** — a few packages in `requirements.txt` are version-pinned, most are not.
- **Model configuration is slightly inconsistent** — the main agent uses `gemini-2.5-flash`, while the faithfulness evaluation script references a different model name; this hasn't been unified yet.
- **Evaluation set is small** (10 questions) and used for development sanity-checking rather than formal benchmarking.

---

## About This Project

This is an independent learning and engineering project built to practice designing an agentic system end-to-end — orchestration with LangGraph, grounded retrieval with RAG, safe text-to-SQL generation, and basic evaluation — rather than to ship a production product. It's a work in progress, and constructive feedback, suggestions, or contributions are genuinely welcome.
