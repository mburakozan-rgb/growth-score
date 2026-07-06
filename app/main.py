import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from typing import Optional
import json

from app.schema import AnalysisRequest, CompanyEvaluation
from app.database import init_db, get_companies, get_company_trends, get_market_comparison, save_evaluation
from app.telemetry import gather_telemetry
from app.agent import run_evaluation_agent

app = FastAPI(title="AI-Age Growth Intelligence Platform")

# Ensure database is initialized on startup
init_db()

# Setup templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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
