from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import sqlite3
from pydantic import BaseModel
from datetime import datetime
import pytz
import os

# SQLite3データベースの接続を設定
DATABASE = "./data/xiRanking.db" if os.getenv("ENV") == "development" else "/app/data/xiRanking.db"

# UnityのWebGLビルドがあるディレクトリを指定
webgl_build_path = "./xiBuildWebGL" if os.getenv("ENV") == "development" else "/app/xiBuildWebGL"


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

def format_jst(datetime_utc):
    # UTCからJSTへ変換
    utc = pytz.utc
    jst = pytz.timezone('Asia/Tokyo')

    # 文字列をdatetimeに変換し、UTCとして解釈
    utc_time = utc.localize(datetime.strptime(datetime_utc, "%Y-%m-%d %H:%M:%S"))

    # JSTに変換
    jst_time = utc_time.astimezone(jst)

    # 指定のフォーマットに変換
    return jst_time.strftime("%Y年%m月%d日 %H時%M分")

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

    # JSTに変換した結果を新しいリストに格納
    formatted_results = [
        {
            "id": item["id"],
            "name": item["name"],
            "score": item["score"],
            "created_at": format_jst(item["created_at"])
        }
        for item in results
    ]

    return templates.TemplateResponse("ranking.html", {"request": request, "results": formatted_results})

app.mount("/static", StaticFiles(directory=webgl_build_path), name="static")

@app.get("/")
def read_index():
    # index.htmlを返す
    return FileResponse(os.path.join(webgl_build_path, "index.html"))

class BrotliMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Brotli圧縮ファイルへのリクエストを判定し、ヘッダーを付与
        if request.url.path.endswith(".br"):
            response.headers["Content-Encoding"] = "br"
        return response

app.add_middleware(BrotliMiddleware)
