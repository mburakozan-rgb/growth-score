# Gold-Standard Example (good_example.md)

This represents an exemplary core use cases document. It showcases high specificity, clear audience roles, testable criteria, and logical epic cycles.

---

## Initiative Summary
The **AI-Age Growth Capabilities Platform** is an agentic workspace designed for strategy consultants. It automates the research, evaluation, and comparative analysis of a target company across the Eight Pillars of Growth, leveraging a modular ADK 2.0 Graph Workflow and a draft-override editing interface.

---

## Core Use Cases Table

| # | Use Case | Audience | Trigger | End-to-End Experience | Value Delivered | Testable Acceptance Criteria | Cycle Estimate |
|---|---|---|---|---|---|---|---|
| **UC-1** | **Targeted Multi-Pillar Scan** | Strategy Consultant | Entering a company name and selecting a subset of the 8 pillars. | The system starts the graph, runs telemetry, concurrency-runs only the selected pillar sub-agents, and creates a "Draft" audit. | Saves research time by scanning only relevant pillars; sets a baseline report. | 1. User selects subset (e.g. 2 & 3).<br>2. Logs show only those sub-agents run.<br>3. Saved record marks other pillars as 'Unrated'. | 2 weeks |
| **UC-2** | **On-Demand Pillar Deep-Dive** | Strategy Consultant | Clicking "Run Audit" on an unrated pillar in an existing draft. | The graph resumes, executes that single pillar's sub-agent, and inserts the scores/insights back into the draft. | Allows consultants to build reports dynamically as information is gathered. | 1. Unrated card shows a "Run Audit" button.<br>2. Clicking triggers single sub-agent execution. | 2 weeks |

---

## Use Case Details

### UC-1: Targeted Multi-Pillar Scan
* **Audience**: Strategy Consultants.
* **Trigger**: Inputting a company name and ticking check-boxes for specific pillars to audit.
* **Step-by-Step Experience**:
  1. Consultant inputs "Back Market" and selects "Pillar 2" and "Pillar 3".
  2. The system triggers the `Workflow` graph.
  3. The `telemetry_node` runs, storing BuiltWith details in state.
  4. The dynamic scheduler executes `aeo_auditor` and `personalization_auditor` in parallel.
  5. The `merger_node` compiles the partial evaluation.
  6. The `db_save_node` writes the record to SQLite with status `'draft'`.
* **Value Delivered**: Highly efficient execution; saves API tokens and time.
* **Acceptance Criteria**:
  * Graph successfully runs and collects data.
  * DB entry contains scores for selected pillars, and others are null/unrated.
* **Dependencies**: ADK 2.0 Graph Workflow setup.
* **Estimated Cycle**: 2 weeks.
