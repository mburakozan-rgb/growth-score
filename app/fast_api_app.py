# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import os
import json
from collections.abc import AsyncIterator
from typing import Optional

import google.auth
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.cloud import logging as google_cloud_logging
from sse_starlette.sse import EventSourceResponse

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

from app.schema import AnalysisRequest, CompanyEvaluation
from app.database import init_db, get_companies, get_company_trends, get_market_comparison, save_evaluation
from app.telemetry import gather_telemetry
from app.agent import run_evaluation_agent
setup_telemetry()
try:
    _, project_id = google.auth.default()
except Exception:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "ninth-osprey-499700-h2")

# Setup Google Cloud Logging client safely
try:
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger("growth-intel-agent")
except Exception:
    import logging
    logger = logging.getLogger("growth-intel-agent")

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure database is initialized on module load
init_db()

# Setup templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=False,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=False,
    lifespan=lifespan,
)
app.title = "AI-Age Growth Intelligence Platform"
app.description = "API for interacting with the Growth Intelligence Platform"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the dashboard Single Page Application."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/companies")
async def api_get_companies():
    """Returns all unique companies in the database."""
    try:
        return get_companies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies/{company_name}/trends")
async def api_get_trends(company_name: str):
    """Returns historical evaluation logs for a given company."""
    try:
        return get_company_trends(company_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/comparison")
async def api_market_comparison():
    """Returns latest evaluation scores for all companies and averages."""
    try:
        return get_market_comparison()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/evaluate/stream")
async def evaluate_stream(company_name: str, custom_context: Optional[str] = None):
    """Triggers telemetry and agent research, streaming thoughts and saving results via SSE."""
    async def event_generator():
        try:
            yield {"event": "log", "data": "SYSTEM: Initiating automated API telemetry scan..."}
            
            # 1. Run Telemetry
            telemetry_data = await gather_telemetry(company_name)
            yield {"event": "telemetry", "data": telemetry_data.json()}
            yield {"event": "log", "data": f"SYSTEM: Telemetry scan complete. Domain: {telemetry_data.domain}"}
            yield {"event": "log", "data": f"SYSTEM: Marketing stack tools: {', '.join(telemetry_data.marketing_tech_stack) or 'None'}"}
            yield {"event": "log", "data": f"SYSTEM: AEO citations index: {telemetry_data.aeo_visibility_citations or 'N/A'}"}
            
            # 2. Get past evaluations as context
            trends = get_company_trends(company_name)
            prev_summary = None
            if trends:
                yield {"event": "log", "data": f"SYSTEM: Past evaluations found. Loading {len(trends)} historical records for context..."}
                latest = trends[-1]
                prev_summary = f"Last Overall Score: {latest['overall_score']}\nSummary: {latest['summary']}\n"
                for p in latest["pillars"]:
                    prev_summary += f"Pillar {p['pillar_number']}: {p['score']}\n"
            else:
                yield {"event": "log", "data": "SYSTEM: No previous history found for this company. Starting fresh baseline evaluation."}

            # 3. Stream thoughts from the Antigravity Agent
            async for chunk in run_evaluation_agent(company_name, telemetry_data, prev_summary, custom_context):
                if chunk.startswith("RESULT:"):
                    json_str = chunk[7:].strip()
                    try:
                        eval_dict = json.loads(json_str)
                        eval_obj = CompanyEvaluation(**eval_dict)
                        save_evaluation(eval_obj)
                        yield {"event": "result", "data": json_str}
                    except Exception as e:
                        yield {"event": "error", "data": f"SYSTEM ERROR: Failed schema validation: {str(e)}"}
                elif chunk.startswith("ERROR:"):
                    yield {"event": "error", "data": chunk[6:]}
                else:
                    yield {"event": "log", "data": chunk}
                    
        except Exception as e:
            yield {"event": "error", "data": f"SYSTEM PANIC: {str(e)}"}
            
    return EventSourceResponse(event_generator())


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    try:
        logger.log_struct(feedback.model_dump(), severity="INFO")
    except Exception:
        # Fallback if logger doesn't support log_struct
        import logging
        logging.info(f"Feedback received: {feedback.model_dump()}")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
