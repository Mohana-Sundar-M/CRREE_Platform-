import sqlite3
import json
from typing import List, Dict

DB_PATH = "eval_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS evaluations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  task_id TEXT,
                  score REAL,
                  breakdown TEXT,
                  performance TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_evaluation(task_id: str, score: float, breakdown: Dict, performance: Dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO evaluations (task_id, score, breakdown, performance) VALUES (?, ?, ?, ?)",
              (task_id, score, json.dumps(breakdown), json.dumps(performance)))
    conn.commit()
    conn.close()

def get_history(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM evaluations ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_metrics():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), AVG(score) FROM evaluations")
    count, avg_score = c.fetchone()
    conn.close()
    return {
        "evaluation_count": count or 0,
        "average_score": avg_score or 0.01
    }

init_db()
