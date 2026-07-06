import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.schema import CompanyEvaluation, PillarEvaluation, DiscoveredBestPractice

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "growth_capabilities.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite tables for companies, evaluations, and pillar scores."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create Companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            industry TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. Create Evaluations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            summary TEXT,
            overall_score REAL,
            opportunities TEXT, -- JSON array of strings
            challenges TEXT, -- JSON array of strings
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    # 3. Create Pillar Scores table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pillar_scores (
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
    
    conn.commit()
    conn.close()

def save_evaluation(evaluation: CompanyEvaluation) -> int:
    """Inserts a new company evaluation record into the SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if company exists, if not create it
    cursor.execute("SELECT id FROM companies WHERE name = ?", (evaluation.company_name,))
    row = cursor.fetchone()
    if row:
        company_id = row["id"]
        # Update industry and description if changed
        cursor.execute(
            "UPDATE companies SET industry = ?, description = ? WHERE id = ?",
            (evaluation.industry, evaluation.summary[:200], company_id)
        )
    else:
        cursor.execute(
            "INSERT INTO companies (name, industry, description) VALUES (?, ?, ?)",
            (evaluation.company_name, evaluation.industry, evaluation.summary[:200])
        )
        company_id = cursor.lastrowid
        
    # Insert new evaluation record
    now_str = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO evaluations (company_id, date, summary, overall_score, opportunities, challenges)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            company_id,
            now_str,
            evaluation.summary,
            evaluation.overall_score,
            json.dumps(evaluation.biggest_opportunities),
            json.dumps(evaluation.biggest_challenges)
        )
    )
    evaluation_id = cursor.lastrowid
    
    # Insert individual pillar scores
    for pillar in evaluation.pillars:
        cursor.execute(
            """
            INSERT INTO pillar_scores (evaluation_id, pillar_number, pillar_name, score, analysis, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation_id,
                pillar.pillar_number,
                pillar.pillar_name,
                pillar.score,
                json.dumps({
                    "maturity_label": pillar.maturity_label,
                    "score_rationale": pillar.score_rationale,
                    "strengths": [s.model_dump() for s in pillar.strengths],
                    "weaknesses": [w.model_dump() for w in pillar.weaknesses],
                    "supporting_evidence": [e.model_dump() for e in pillar.supporting_evidence]
                }),
                pillar.confidence
            )
        )
        
    conn.commit()
    conn.close()
    return evaluation_id

def get_companies() -> List[Dict[str, Any]]:
    """Returns a list of all companies with their latest evaluation metadata."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.id,
            c.name,
            c.industry,
            c.description,
            e.date as last_eval_date,
            e.overall_score as last_score
        FROM companies c
        LEFT JOIN evaluations e ON e.company_id = c.id
        WHERE e.id = (
            SELECT MAX(id) FROM evaluations WHERE company_id = c.id
        ) OR e.id IS NULL
        ORDER BY c.name ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_company_trends(company_name: str) -> List[Dict[str, Any]]:
    """Retrieves all evaluations for a specific company, ordered by date, showing scores and details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get company ID
    cursor.execute("SELECT id FROM companies WHERE name = ?", (company_name,))
    comp_row = cursor.fetchone()
    if not comp_row:
        conn.close()
        return []
    company_id = comp_row["id"]
    
    # Get evaluations
    cursor.execute(
        "SELECT id, date, summary, overall_score, opportunities, challenges FROM evaluations WHERE company_id = ? ORDER BY date ASC",
        (company_id,)
    )
    eval_rows = cursor.fetchall()
    
    trends = []
    for r in eval_rows:
        eval_id = r["id"]
        # Fetch pillar scores for this evaluation
        cursor.execute(
            "SELECT pillar_number, pillar_name, score, analysis, confidence FROM pillar_scores WHERE evaluation_id = ? ORDER BY pillar_number ASC",
            (eval_id,)
        )
        pillar_rows = cursor.fetchall()
        pillars = []
        for p in pillar_rows:
            p_dict = dict(p)
            try:
                details = json.loads(p_dict["analysis"])
                p_dict["maturity_label"] = details.get("maturity_label", "Developing")
                p_dict["score_rationale"] = details.get("score_rationale", "")
                p_dict["strengths"] = details.get("strengths", [])
                p_dict["weaknesses"] = details.get("weaknesses", [])
                p_dict["supporting_evidence"] = details.get("supporting_evidence", [])
            except Exception:
                p_dict["maturity_label"] = "Developing"
                p_dict["score_rationale"] = p_dict["analysis"] or ""
                p_dict["strengths"] = []
                p_dict["weaknesses"] = []
                p_dict["supporting_evidence"] = []
            pillars.append(p_dict)
        
        trends.append({
            "id": eval_id,
            "date": r["date"],
            "summary": r["summary"],
            "overall_score": r["overall_score"],
            "opportunities": json.loads(r["opportunities"]) if r["opportunities"] else [],
            "challenges": json.loads(r["challenges"]) if r["challenges"] else [],
            "pillars": pillars
        })
        
    conn.close()
    return trends

def get_market_comparison() -> Dict[str, Any]:
    """Returns a comparative matrix of the latest scores for all companies and the pillar averages."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get latest evaluation for all companies
    cursor.execute("""
        SELECT 
            c.name as company_name,
            c.industry,
            e.id as evaluation_id,
            e.overall_score,
            e.date
        FROM companies c
        JOIN evaluations e ON e.company_id = c.id
        WHERE e.id = (
            SELECT MAX(id) FROM evaluations WHERE company_id = c.id
        )
    """)
    latest_evals = cursor.fetchall()
    
    companies_data = []
    pillar_totals = {i: 0.0 for i in range(1, 9)}
    pillar_names = {}
    
    for le in latest_evals:
        eval_id = le["evaluation_id"]
        cursor.execute(
            "SELECT pillar_number, pillar_name, score FROM pillar_scores WHERE evaluation_id = ? ORDER BY pillar_number ASC",
            (eval_id,)
        )
        pillar_rows = cursor.fetchall()
        
        pillars_scores = {}
        for pr in pillar_rows:
            p_num = pr["pillar_number"]
            p_name = pr["pillar_name"]
            score = pr["score"]
            pillars_scores[p_num] = score
            pillar_totals[p_num] += score
            pillar_names[p_num] = p_name
            
        companies_data.append({
            "company_name": le["company_name"],
            "industry": le["industry"],
            "overall_score": le["overall_score"],
            "date": le["date"],
            "scores": pillars_scores
        })
        
    # Calculate averages
    averages = {}
    num_companies = len(companies_data)
    if num_companies > 0:
        for p_num, total in pillar_totals.items():
            averages[p_num] = round(total / num_companies, 1)
    else:
        for p_num in range(1, 9):
            averages[p_num] = 0.0
            
    conn.close()
    
    return {
        "companies": companies_data,
        "averages": averages,
        "pillar_names": pillar_names
    }
