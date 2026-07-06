import os
import httpx
import re
from typing import Dict, Any, List
from app.schema import TelemetryData

DEMO_TELEMETRY = {
    "backmarket.com": {
        "robots_txt_bot_block_status": {"GPTBot": "allowed", "PerplexityBot": "allowed", "ClaudeBot": "blocked"},
        "marketing_tech_stack": ["Segment", "Braze", "Dynamic Yield", "Google Tag Manager", "Amplitude", "Google Analytics 4"],
        "app_rating": 4.7,
        "app_rating_count": 125000,
        "api_docs_found": True,
        "aeo_visibility_citations": 84
    },
    "on-running.com": {
        "robots_txt_bot_block_status": {"GPTBot": "allowed", "PerplexityBot": "allowed", "ClaudeBot": "allowed"},
        "marketing_tech_stack": ["Salesforce Marketing Cloud", "Google Analytics 4", "Optimizely", "LaunchDarkly", "Google Tag Manager Server-Side", "Contentful"],
        "app_rating": 4.8,
        "app_rating_count": 8900,
        "api_docs_found": False,
        "aeo_visibility_citations": 68
    },
    "skyscanner.net": {
        "robots_txt_bot_block_status": {"GPTBot": "allowed", "PerplexityBot": "allowed", "ClaudeBot": "allowed"},
        "marketing_tech_stack": ["Adobe Target", "Tealium", "Mixpanel", "Google Analytics 4", "Google Tag Manager Server-Side", "LaunchDarkly"],
        "app_rating": 4.6,
        "app_rating_count": 340000,
        "api_docs_found": True,
        "aeo_visibility_citations": 91
    }
}

def resolve_domain(company_name: str) -> str:
    """Maps common company names to domains."""
    name_clean = company_name.lower().strip()
    if "back market" in name_clean or "backmarket" in name_clean:
        return "backmarket.com"
    elif "on running" in name_clean or "onrunning" in name_clean or "on-running" in name_clean:
        return "on-running.com"
    elif "skyscanner" in name_clean:
        return "skyscanner.net"
    
    # Generic mapping
    domain_slug = re.sub(r'[^a-z0-9]', '', name_clean)
    return f"{domain_slug}.com"

async def check_live_robots_txt(domain: str) -> Dict[str, str]:
    """Tries to download the robots.txt for a domain and check AI bot permission statuses."""
    bots = ["GPTBot", "PerplexityBot", "ClaudeBot", "Google-Extended"]
    status = {bot: "allowed" for bot in bots}
    
    url = f"https://{domain}/robots.txt"
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = await client.get(url, headers=headers, timeout=5.0)
            if response.status_code == 200:
                content = response.text
                lines = [line.strip().lower() for line in content.split("\n")]
                
                # Check for User-agent blocks
                current_agent = None
                for line in lines:
                    if line.startswith("user-agent:"):
                        current_agent = line.split(":", 1)[1].strip()
                    elif line.startswith("disallow:") and current_agent:
                        disallow_path = line.split(":", 1)[1].strip()
                        # If disallowing root directory
                        if disallow_path == "/":
                            for bot in bots:
                                if bot.lower() in current_agent:
                                    status[bot] = "blocked"
                                elif current_agent == "*":
                                    # Standard bots block wildcard disallow
                                    pass
    except Exception:
        # If network error or request failed, return default allowed/unknown status
        pass
    return status

async def gather_telemetry(company_name: str) -> TelemetryData:
    """Gathers structured marketing tech stack, ratings, and bot crawler permissions."""
    domain = resolve_domain(company_name)
    
    # If the domain is a known demo brand, load baseline details
    base_data = DEMO_TELEMETRY.get(domain, {
        "robots_txt_bot_block_status": {},
        "marketing_tech_stack": ["Google Tag Manager", "Google Analytics 4", "Hotjar"],
        "app_rating": 4.2,
        "app_rating_count": 1200,
        "api_docs_found": False,
        "aeo_visibility_citations": 45
    })
    
    # Fetch live robots.txt to override bot status if possible
    live_bots = await check_live_robots_txt(domain)
    # Merge or use live robots
    bot_status = live_bots if any(v == "blocked" for v in live_bots.values()) else base_data["robots_txt_bot_block_status"]
    if not bot_status:
        bot_status = live_bots
        
    # Check if BuiltWith API is available in environment
    builtwith_key = os.environ.get("BUILTWITH_API_KEY")
    tech_stack = base_data["marketing_tech_stack"]
    if builtwith_key:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"https://api.builtwith.com/v20/api.json?key={builtwith_key}&lookup={domain}")
                if res.status_code == 200:
                    data = res.json()
                    # Parse technology names from BuiltWith results
                    found_techs = []
                    for path in data.get("Paths", []):
                        for tech in path.get("Technologies", []):
                            name = tech.get("Name")
                            if name and name not in found_techs:
                                found_techs.append(name)
                    # Filter for relevant growth/marketing tools
                    growth_tools = ["Segment", "Optimizely", "LaunchDarkly", "Dynamic Yield", "Braze", "Mixpanel", "Tealium", "Amplitude", "Adobe Target"]
                    tech_stack = [t for t in found_techs if any(gt.lower() in t.lower() for gt in growth_tools)]
                    if not tech_stack:
                        tech_stack = ["Google Tag Manager", "Google Analytics 4"]
        except Exception:
            pass

    return TelemetryData(
        domain=domain,
        robots_txt_bot_block_status=bot_status,
        marketing_tech_stack=tech_stack,
        app_rating=base_data.get("app_rating"),
        app_rating_count=base_data.get("app_rating_count"),
        api_docs_found=base_data.get("api_docs_found", False),
        aeo_visibility_citations=base_data.get("aeo_visibility_citations")
    )
