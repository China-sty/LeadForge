"""FastAPI Web 层：老板看板 + 挖掘接口。"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

load_dotenv()

from .config import load_config
from .datasources.mock import MockDataSource
from .llm import LLMClient
from .pipeline import Pipeline
from .store import Store

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "enterprise.yaml"
INDEX_PATH = PROJECT_ROOT / "web" / "index.html"

config = load_config(str(CONFIG_PATH))
llm = LLMClient()
store = Store()
pipeline = Pipeline(config, llm, MockDataSource())

app = FastAPI(title="LeadForge")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_PATH.read_text(encoding="utf-8")


@app.post("/mine")
def mine() -> dict:
    """运行挖掘流水线（同步，MVP 阶段可能耗时数十秒）。"""
    store.clear()
    leads = pipeline.run()
    store.save_leads(leads)
    return {"mined": len(leads)}


@app.get("/api/leads")
def leads() -> list:
    return store.list_leads()


@app.get("/api/stats")
def stats() -> dict:
    return store.stats(config.threshold)


@app.get("/api/config")
def get_config() -> dict:
    return {
        "enterprise": config.name,
        "products": config.products,
        "keywords": config.industry_keywords,
    }
