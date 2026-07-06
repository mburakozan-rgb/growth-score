# Requirements: UC-1 Automated Multi-Pillar Company Scan

## 1. Introduction
This document defines the technical specifications and requirements for **UC-1: Automated Multi-Pillar Company Scan**. 
The goal of UC-1 is to allow **Strategy Consultants** to request a rapid, automated evaluation of a target company's growth capabilities against the Eight Pillars of Growth in the Age of AI. The system runs an automated telemetry scan, initiates an AI-agent research process, streams thoughts and status in real-time, and saves a structured report in the database.

---

## 2. User Interface (Frontend) Requirements

### 2.1 User Inputs
- **Company Name Input**:
  - Element: Text input (`#companyInput`).
  - Validation: Required, non-empty, alphanumeric and common characters allowed.
  - Placeholder: `"Enter Company Name (e.g. Stripe)"`.
- **Custom Context Textarea**:
  - Element: Textarea (`#contextInput`).
  - Validation: Optional.
  - Purpose: Allows users to input raw context (articles, notes, job descriptions, or PRs) to assist the agent in its research.
  - Placeholder: `"Optional: Paste recent articles, context notes, or PRs for continuous learning update..."`.

### 2.2 Trigger Action
- **Evaluate Brand Button**:
  - Element: Button (`#analyzeBtn`).
  - Behavior:
    - On click, validates inputs. If invalid, displays alert.
    - If valid, disables the button, changes label to `"Evaluating..."`, and adds a loading spinner.
    - Shows the **Terminal Console Panel** (`#terminalPanel`).
    - Establishes a Server-Sent Events (SSE) connection to the backend stream.
    - Re-enables the button once the stream ends (either on `result`, `error`, or connection closure).

### 2.3 Live Streaming Terminal Console
- **Console Panel**:
  - Element: `#terminalPanel` (initially hidden, flex-column on trigger).
  - Status Indicator: `#terminalStatus` (e.g., `"Running..."`, `"Complete"`, `"Failed"`).
  - Output Area: `#terminalLogs`.
  - Behavior:
    - Appends incoming log text as individual lines.
    - Autoscrolls to the bottom when new logs arrive.
    - Color-codes messages:
      - System logs: Green (`class="terminal-log-system"`).
      - Agent thoughts: Muted grey/italic (`class="terminal-log-thought"`).
      - Regular status logs: Light blue.

### 2.4 Results Dashboard Presentation
Upon receiving the final `result` event containing the `CompanyEvaluation` payload, the UI must render the following:
- **Hero Panel**:
  - Displays company name, industry, and overall score out of 10.
  - Displays the overall synthesis/summary paragraph.
  - Renders the overall score badge colored based on score ranges:
    - `>= 8.0`: High/Success (Emerald Green)
    - `5.0 - 7.9`: Mid/Warning (Amber Orange)
    - `< 5.0`: Low/Danger (Crimson Red)
- **Telemetry Indicators**:
  - Displays specific cards for:
    - Domain resolved.
    - AI Crawler block status (GPTBot, PerplexityBot).
    - Marketing tech stack tools (comma-separated list).
    - Simulated AEO citations index.
- **Pillar Score Grid**:
  - Renders 8 separate cards, one for each pillar (labeled Pillar 1 through 8).
  - Each card shows:
    - Pillar Number & Title.
    - Interactive Progress Bar representing score out of 10.
    - Score label (e.g., `8.2/10`).
  - Interaction: Clicking a card opens a modal overlay (`#pillarModal`) displaying the detailed qualitative assessment narrative (`analysis`) and the `confidence` score.
- **Opportunities & Challenges Columns**:
  - Side-by-side lists outlining the top growth opportunities (minimum 3) and biggest challenges (minimum 3).
- **Discovered Best Practices Section**:
  - Renders cards for any state-of-the-art benchmarks identified.

---

## 3. API Contracts (REST & SSE)

### 3.1 Evaluation Stream Endpoint
- **URL**: `/api/evaluate/stream`
- **Method**: `GET`
- **Query Parameters**:
  - `company_name` (string, required): The target company name.
  - `custom_context` (string, optional): Extra research material provided by the user.
- **Protocol**: Server-Sent Events (SSE)
- **Content-Type**: `text/event-stream`

### 3.2 SSE Event Message Formats
The backend streams messages using the following event types:

1. **`event: log`** (Status Updates & Agent Thoughts)
   ```json
   "data": "SYSTEM: Telemetry scan complete. Domain: stripe.com"
   ```
2. **`event: telemetry`** (Parsed Telemetry Data Contract)
   Matches `TelemetryData` schema:
   ```json
   {
     "domain": "stripe.com",
     "robots_txt_bot_block_status": {"GPTBot": "allowed", "PerplexityBot": "allowed"},
     "marketing_tech_stack": ["Google Tag Manager", "Google Analytics 4"],
     "app_rating": null,
     "app_rating_count": null,
     "api_docs_found": true,
     "aeo_visibility_citations": 75
   }
   ```
3. **`event: result`** (Final Scoring Schema)
   Matches `CompanyEvaluation` schema:
   ```json
   {
     "company_name": "Stripe",
     "industry": "Fintech / Payment Infrastructure",
     "overall_score": 8.7,
     "summary": "Stripe continues to lead in developer-first payment APIs...",
     "pillars": [
       {
         "pillar_number": 1,
         "pillar_name": "Product & Customer Experience Excellence",
         "score": 9.2,
         "analysis": "Stripe provides a highly habit-forming payments infrastructure...",
         "confidence": 0.95
       }
       // ... other 7 pillars
     ],
     "biggest_opportunities": [
       "Expand AI-driven fraud detection services...",
       "Increase penetration in emerging markets...",
       "Build personalized consumer wallets..."
     ],
     "biggest_challenges": [
       "Intensified regulatory compliance overhead...",
       "Rising transaction margins compression...",
       "Adversarial security exploits target..."
     ],
     "discovered_best_practices": [
       {
         "pillar_number": 8,
         "pillar_name": "Tools & Platforms",
         "description": "Developer API docs structured as a self-onboarding journey.",
         "implementation_details": "Stripe hosts code playgrounds directly in documentation..."
       }
     ]
   }
   ```
4. **`event: error`** (API or Validation Failures)
   ```json
   "data": "SYSTEM ERROR: Failed schema validation: [details]"
   ```

---

## 4. Backend Processing & Telemetry Pipeline

### 4.1 Telemetry Gathering (`app/telemetry.py`)
When triggered, the backend executes the asynchronous function `gather_telemetry(company_name)` which handles:
1. **Domain Resolution**: Converts input names to web domains (e.g. `"Stripe"` -> `"stripe.com"`).
2. **AI Crawler Permissions Inspection**:
   - Fetches the live `robots.txt` file (e.g. `https://stripe.com/robots.txt`).
   - Checks disallowed paths for bots: `GPTBot`, `PerplexityBot`, `ClaudeBot`, `Google-Extended`.
   - Returns a dictionary mapping bot status (e.g., `{"GPTBot": "allowed", "ClaudeBot": "blocked"}`).
3. **Marketing Stack Identification**:
   - Queries BuiltWith API using `BUILTWITH_API_KEY` (if available).
   - Filters technology lists for known tools (Segment, Optimizely, LaunchDarkly, Braze, Mixpanel, Tealium, Adobe Target, Amplitude).
   - If BuiltWith is unavailable, falls back to a default list of baseline analytics trackers.
4. **App & AEO Scoring**:
   - Pulls app ratings and counts if the domain matches known app providers.
   - Generates simulated AEO citations (citations per 100 queries).

---

## 5. Agent Orchestration & Prompting

### 5.1 Agent Setup (`app/agent.py`)
- **Framework**: ADK 2.0 (Agent Development Kit).
- **Core LLM**: Gemini 3.1 Flash Lite (`gemini-3.1-flash-lite`).
- **Tools**:
  - `web_search(query)`: Executes search on Google (via Serper) or DuckDuckGo.
  - `fetch_webpage(url)`: Fetches HTML, strips scripts/styles, and extracts text content (capped at 4000 characters).
- **Context Injection**:
  - Injecting telemetry findings (`robots_txt_bot_block_status`, `marketing_tech_stack`, etc.).
  - Loading past evaluations context for trend assessment.
  - Ingesting benchmark files dynamically loaded from `standards/` directory.

### 5.2 Scoring Guide Rubric (`standards/scoring_guide.md`)
The agent must evaluate against the rubrics defined for the Eight Pillars:
- **Pillar 1**: Product & Customer Experience Excellence
- **Pillar 2**: Content Strategy & Operating System (SEO to AEO)
- **Pillar 3**: Advanced Segmentation & Psychology-Based Personalization
- **Pillar 4**: The Experimentation & Growth Culture
- **Pillar 5**: Growth Loops & Advanced Journey Orchestration
- **Pillar 6**: Distribution Strategy & Channel Orchestration
- **Pillar 7**: Measurement & Attribution
- **Pillar 8**: Tools & Platforms

---

## 6. Database & Persistence (`app/database.py`)

### 6.1 Database Engine
- **Engine**: SQLite.
- **Database File**: `app/growth_capabilities.db`.

### 6.2 Data Mapping & Save Flow
When the agent completes the run and returns a validated `CompanyEvaluation`:
1. The backend parses the JSON data.
2. Inserts a new evaluation log row into the database:
   - Tables updated: `evaluations`, `pillar_scores`, `best_practices`.
3. The entry is recorded with the current ISO timestamp to preserve historical trend analysis logs.
