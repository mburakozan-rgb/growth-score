import os
import sqlite3
import json
from datetime import datetime, timedelta

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "growth_capabilities.db")

PILLARS_METADATA = [
    (1, "Product & Customer Experience Excellence"),
    (2, "Content Strategy & Operating System"),
    (3, "Advanced Segmentation & Psychology Personalization"),
    (4, "Experimentation & Growth Culture"),
    (5, "Growth Loops & Advanced Journey Orchestration"),
    (6, "Distribution Strategy & Channel Orchestration"),
    (7, "Measurement & Attribution"),
    (8, "Tools & Platforms")
]

def seed_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Clean tables if they exist to prevent duplicates
    cursor.execute("DROP TABLE IF EXISTS pillar_scores")
    cursor.execute("DROP TABLE IF EXISTS evaluations")
    cursor.execute("DROP TABLE IF EXISTS companies")
    
    # Re-create tables
    cursor.execute("""
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            industry TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            date TIMESTAMP,
            summary TEXT,
            overall_score REAL,
            opportunities TEXT,
            challenges TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE pillar_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id INTEGER NOT NULL,
            pillar_number INTEGER NOT NULL,
            pillar_name TEXT NOT NULL,
            score REAL NOT NULL,
            analysis TEXT,
            confidence REAL,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
        )
    """)
    
    # 1. Back Market
    cursor.execute(
        "INSERT INTO companies (name, industry, description) VALUES (?, ?, ?)",
        ("Back Market", "E-commerce & Circular Tech", "The leading marketplace for professionally refurbished smartphones, laptops, and electronics.")
    )
    backmarket_id = cursor.lastrowid
    
    # Back Market Timeline
    bm_timeline = [
        # 6 Months Ago
        {
            "offset_days": -180,
            "overall": 7.3,
            "summary": "Back Market has strong fundamental customer experience (Pillar 1) and core product-led referral loops. However, personalization is rules-based and content optimization remains traditional SEO-focused rather than AEO.",
            "opportunities": [
                "Shift search marketing from traditional keywords to AEO optimization.",
                "Introduce server-side conversion tracking to overcome iOS privacy hurdles.",
                "Incorporate psychology-based triggers into email and push notifications."
            ],
            "challenges": [
                "Rising paid acquisition costs on traditional social search channels.",
                "Fragmented user state across mobile and web platforms.",
                "AI web crawlers are currently blocked, limiting potential citations in search engines."
            ],
            "scores": [8.2, 5.8, 6.5, 7.0, 8.4, 7.2, 6.8, 7.0] # 1 to 8
        },
        # 3 Months Ago
        {
            "offset_days": -90,
            "overall": 7.8,
            "summary": "Back Market resolved bot crawler configurations to allow Perplexity and GPTBot. Personalization has transitioned from simple rules to Segment-based behavioral profiles.",
            "opportunities": [
                "Leverage AI content pipelines for multimodal catalog tagging.",
                "Optimize checkout and warranty registration steps into compounding loops.",
                "A/B test personalization models for refurbisher-side interfaces."
            ],
            "challenges": [
                "Maintaining brand tone consistency across multi-regional automated emails.",
                "Attribution mismatch between web catalog visits and mobile app checkout.",
                "Learning velocity is constrained by slower releases in the checkout team."
            ],
            "scores": [8.3, 7.0, 7.2, 7.2, 8.5, 7.6, 7.4, 7.8]
        },
        # Today
        {
            "offset_days": 0,
            "overall": 8.3,
            "summary": "Back Market has reached an advanced maturity level. Content is fully optimized for Answer Engine Optimization (AEO) with high Perplexity share of voice. Multi-touch journey loops are dynamic and compounding, driving down CAC.",
            "opportunities": [
                "Integrate real-time social proof overlays matching customer context.",
                "Publish developer API portal for trade-in integrations on external sites.",
                "Deploy custom AI support agents that handle purchase warranties directly."
            ],
            "challenges": [
                "Increasing competition from OEM-refurbished programs.",
                "Cookie-deprecation affecting remaining client-side pixels.",
                "Scaling testing velocity from dozens to hundreds of simultaneous cohorts."
            ],
            "scores": [8.5, 8.2, 7.8, 7.7, 8.8, 8.1, 8.0, 8.3]
        }
    ]
    
    # 2. On Running
    cursor.execute(
        "INSERT INTO companies (name, industry, description) VALUES (?, ?, ?)",
        ("On Running", "Athletic Apparel & Footwear", "Swiss high-performance running shoes and athletic apparel brand known for innovative CloudTec cushioning.")
    )
    on_id = cursor.lastrowid
    
    on_timeline = [
        # 6 Months Ago
        {
            "offset_days": -180,
            "overall": 6.7,
            "summary": "On Running boasts world-class product design and advocacy (Pillar 1). However, the digital growth ecosystem lags. Experimentation is sparse and personalization is limited to simple post-purchase recommendations.",
            "opportunities": [
                "Implement a unified Customer Data Platform (CDP) for retail and e-commerce.",
                "Launch structured A/B testing on product detail pages.",
                "Create content structured for voice search regarding running gear reviews."
            ],
            "challenges": [
                "Inconsistent personalization across retail store kiosks and online store.",
                "High reliance on third-party retailers limits direct attribution.",
                "Slow site performance on visual-heavy campaign landing pages."
            ],
            "scores": [8.8, 6.0, 5.2, 5.0, 6.2, 6.5, 5.8, 6.0]
        },
        # 3 Months Ago
        {
            "offset_days": -90,
            "overall": 7.1,
            "summary": "On Running integrated LaunchDarkly for experimentation, accelerating testing cycles. Website performance was optimized, and basic schema markup has been rolled out on product pages.",
            "opportunities": [
                "Establish a dynamic loyalty-based referral loop program.",
                "Optimize search strategy for Perplexity/Gemini athletic wear queries.",
                "Deploy server-side GTM to clean up data collection."
            ],
            "challenges": [
                "Inventory discrepancies causing customer experience friction.",
                "Attribution limits due to strict cookie privacy laws in Europe.",
                "Scaling specialized growth engineering hires."
            ],
            "scores": [8.9, 6.5, 6.0, 6.4, 6.5, 7.0, 6.6, 6.8]
        },
        # Today
        {
            "offset_days": 0,
            "overall": 7.6,
            "summary": "On Running has successfully integrated Salesforce Marketing Cloud and server-side tracking. Experiencing strong Product Excellence and growing Experimentation culture, though growth loop mechanics could be more embedded.",
            "opportunities": [
                "Expand circular subscription program (On Cyclon) into a core digital data loop.",
                "Implement emotional personalization based on athlete workout tracking.",
                "Open API for running club integrations."
            ],
            "challenges": [
                "Scaling cross-channel orchestration across international markets.",
                "Attributing offline retail growth to online media spend.",
                "AEO visibility for generic sneaker queries is dominated by large aggregates."
            ],
            "scores": [9.0, 7.2, 6.8, 7.3, 7.0, 7.5, 7.2, 7.4]
        }
    ]
    
    # 3. Skyscanner
    cursor.execute(
        "INSERT INTO companies (name, industry, description) VALUES (?, ?, ?)",
        ("Skyscanner", "Travel Search Metasearch", "A leading global travel search site providing instant online comparison for flights, hotels, and car hire.")
    )
    skyscanner_id = cursor.lastrowid
    
    skyscanner_timeline = [
        # 6 Months Ago
        {
            "offset_days": -180,
            "overall": 8.0,
            "summary": "Skyscanner has a mature testing culture and complex marketing technology stack. Its core flight booking loop is highly optimized. Personalization is dynamic based on past searches.",
            "opportunities": [
                "Transition API endpoints to support direct booking by autonomous AI agents.",
                "Build voice-native search skills to interface with voice assistants.",
                "Incorporate multi-touch attribution to assess video campaign effects."
            ],
            "challenges": [
                "Answer engines bypassing metasearch by serving direct flight data.",
                "Maintaining page speed performance during heavy API searches.",
                "Complex database schemas slowing real-time profile updates."
            ],
            "scores": [8.4, 7.5, 7.8, 8.4, 8.2, 7.8, 8.0, 8.1]
        },
        # 3 Months Ago
        {
            "offset_days": -90,
            "overall": 8.5,
            "summary": "Skyscanner launched advanced developer documentation and API accessibility for AI models. Content is structured to encourage AI citing, improving visibility scores.",
            "opportunities": [
                "Integrate with chat-based AI travel assistants directly via SSE.",
                "Leverage situational personalization (e.g. flight delay status in app).",
                "Deepen server-side attribution tracking."
            ],
            "challenges": [
                "API rate limits and scraper activity mimicking AI bot crawlers.",
                "Managing multi-currency pricing synchronization in real-time.",
                "Privacy-safe tracking limitations on mobile operating systems."
            ],
            "scores": [8.5, 8.2, 8.0, 8.6, 8.5, 8.4, 8.3, 8.5]
        },
        # Today
        {
            "offset_days": 0,
            "overall": 8.9,
            "summary": "Skyscanner represents a gold standard in travel tech growth orchestration. Tech infrastructure is completely integrated, personalization adapts to real-time scenarios, and they are highly optimized for AI-agent search visibility.",
            "opportunities": [
                "Scale conversational booking via external platforms (ChatGPT, Gemini).",
                "Automate personalized itinerary creations driven by travel psychology.",
                "Create first-party travel data loops to feed proprietary prediction engines."
            ],
            "challenges": [
                "Platform dependence on Google search updates.",
                "Managing extreme peak volumes on serverless event pipelines.",
                "Attribution in multi-device travel research sessions."
            ],
            "scores": [8.7, 8.9, 8.5, 8.9, 8.8, 8.8, 8.7, 9.0]
        }
    ]
    
    # Seed evaluations and pillar scores
    for comp_id, timeline in [(backmarket_id, bm_timeline), (on_id, on_timeline), (skyscanner_id, skyscanner_timeline)]:
        for item in timeline:
            eval_date = (datetime.now() + timedelta(days=item["offset_days"])).isoformat()
            cursor.execute(
                """
                INSERT INTO evaluations (company_id, date, summary, overall_score, opportunities, challenges)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    comp_id,
                    eval_date,
                    item["summary"],
                    item["overall"],
                    json.dumps(item["opportunities"]),
                    json.dumps(item["challenges"])
                )
            )
            eval_id = cursor.lastrowid
            
            for idx, (p_num, p_name) in enumerate(PILLARS_METADATA):
                score = item["scores"][idx]
                analysis = f"Justifying a score of {score} for Pillar {p_num} on {item['summary'][:40]}..."
                cursor.execute(
                    """
                    INSERT INTO pillar_scores (evaluation_id, pillar_number, pillar_name, score, analysis, confidence)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (eval_id, p_num, p_name, score, analysis, 0.9)
                )
                
    conn.commit()
    conn.close()
    print("Database successfully seeded with historical demo data!")

if __name__ == "__main__":
    seed_db()
