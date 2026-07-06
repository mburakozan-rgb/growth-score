import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.telemetry import gather_telemetry
from app.agent import run_evaluation_agent
from app.schema import CompanyEvaluation

async def main():
    print("--- STARTING AGENT DRY-RUN VERIFICATION ---")
    company_name = "Back Market"
    print(f"1. Gathering telemetry for {company_name}...")
    telemetry_data = await gather_telemetry(company_name)
    print(f"   Telemetry: {telemetry_data.json()}\n")
    
    print(f"2. Executing Antigravity Agent for {company_name}...")
    result_json = None
    
    async for chunk in run_evaluation_agent(
        company_name=company_name,
        telemetry_data=telemetry_data,
        previous_evals_summary="Previous overall score: 7.8. Strong product, but Content strategy was SEO-first and not optimized for AEO.",
        custom_context="They recently updated their robots.txt to allow Perplexity and GPTBot, and rolled out detailed schema tags."
    ):
        if chunk.startswith("RESULT:"):
            result_json = chunk[7:].strip()
            print("\n[RESULT RECEIVED]")
        elif chunk.startswith("ERROR:"):
            print(f"\n[ERROR RECEIVED] {chunk}")
        elif chunk.startswith("STATUS:"):
            print(f"\n[STATUS] {chunk}")
        else:
            # Print agent thoughts
            print(chunk, end="", flush=True)
            
    if result_json:
        print("\n\n3. Verifying Result Schema...")
        try:
            import json
            data = json.loads(result_json)
            # Parse into Pydantic
            eval_obj = CompanyEvaluation(**data)
            print("✓ Success! Schema verified.")
            print(f"Company: {eval_obj.company_name}")
            print(f"Industry: {eval_obj.industry}")
            print(f"Overall Score: {eval_obj.overall_score}")
            print(f"Pillars Count: {len(eval_obj.pillars)}")
            print(f"Opportunities: {eval_obj.biggest_opportunities}")
            print(f"Challenges: {eval_obj.biggest_challenges}")
            print(f"Discovered Best Practices: {len(eval_obj.discovered_best_practices)}")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
    else:
        print("\n✗ Failed: No RESULT found in agent output.")
        
if __name__ == "__main__":
    asyncio.run(main())
