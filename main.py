from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sqlite3
from pydantic import BaseModel

# SQLite3データベースの接続を設定
DATABASE = "xiRanking.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# FastAPIアプリケーションの作成
app = FastAPI()

# Jinja2のテンプレート設定
templates = Jinja2Templates(directory="templates")

# Pydanticモデル
class Result(BaseModel):
    name: str
    score: int

# 初回のテーブル作成
def create_table():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

create_table()

@app.post("/result/")
def create_item(item: Result):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (name, score) VALUES (?, ?)",
        (item.name, item.score)
    )
    conn.commit()
    conn.close()
    return {"id": cursor.lastrowid, "name": item.name, "score": item.score}

@app.get("/result/")
def read_results():
    conn = get_db_connection()
    results = conn.execute("SELECT * FROM results ORDER BY score DESC").fetchall()
    conn.close()
    return [{"id": item["id"], "name": item["name"], "score": item["score"], "created_at": item["created_at"]} for item in results]

@app.get("/ranking/")
def get_ranking_page(request: Request):
    conn = get_db_connection()
    results = conn.execute("SELECT * FROM results ORDER BY score DESC").fetchall()

    conn.close()
    return templates.TemplateResponse("ranking.html", {"request": request, "results": results})
