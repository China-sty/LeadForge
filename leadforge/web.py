"""FastAPI Web 层：老板看板 + 触达 + 询盘 + 聚焦分析 + 官网客服。"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

from .agents.enquiry import EnquiryAgent
from .config import load_config
from .datasources.mock import MockDataSource
from .llm import LLMClient
from .models import Company
from .pipeline import Pipeline
from .store import Store

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "enterprise.yaml"
INDEX_PATH = PROJECT_ROOT / "web" / "index.html"
LANDING_PATH = PROJECT_ROOT / "web" / "landing.html"

config = load_config(str(CONFIG_PATH))
llm = LLMClient()
store = Store()
pipeline = Pipeline(config, llm, MockDataSource())
enquiry_agent = EnquiryAgent(llm)

app = FastAPI(title="LeadForge")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_PATH.read_text(encoding="utf-8")


@app.get("/landing", response_class=HTMLResponse)
def landing() -> str:
    return LANDING_PATH.read_text(encoding="utf-8")


@app.post("/mine")
def mine() -> dict:
    store.clear()
    leads = pipeline.run(with_outreach=True)
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
    return {"enterprise": config.name, "products": config.products, "keywords": config.industry_keywords}


class StageIn(BaseModel):
    stage: str


@app.post("/api/leads/{lead_id}/stage")
def update_stage(lead_id: int, body: StageIn) -> dict:
    store.update_stage(lead_id, body.stage)
    return {"ok": True}


class EnquiryIn(BaseModel):
    lead_id: int
    message: str


@app.post("/api/enquiry")
def enquiry(body: EnquiryIn) -> dict:
    lead = next((l for l in store.list_leads() if l["id"] == body.lead_id), None)
    if lead is None:
        return {"error": "线索不存在"}
    company = Company(
        name=lead["company_name"], industry=lead["industry"], scope=lead["scope"],
        scale=lead["scale"], region=lead["region"],
    )
    resp = enquiry_agent.respond(company, body.message, config)
    store.update_stage(body.lead_id, "报价中")
    return {"reply": resp.reply, "quote_draft": resp.quote_draft, "next_action": resp.next_action}


@app.get("/api/focus")
def focus() -> dict:
    leads = store.list_leads()
    industries: dict[str, dict] = {}
    for l in leads:
        ind = l["industry"] or "未知"
        industries.setdefault(ind, {"count": 0, "score_sum": 0.0})
        industries[ind]["count"] += 1
        industries[ind]["score_sum"] += l["total_score"] or 0
    summary = [
        {"industry": k, "count": v["count"], "avg_score": round(v["score_sum"] / v["count"], 1)}
        for k, v in industries.items()
    ]
    summary.sort(key=lambda x: -x["avg_score"])
    return {"summary": summary, "recommendation": _focus_recommendation(summary)}


def _focus_recommendation(summary: list) -> str:
    if not summary:
        return "暂无数据，先运行挖掘。"
    text = "\n".join(f"- {s['industry']}: {s['count']} 家，平均分 {s['avg_score']}" for s in summary[:5])
    try:
        return llm.chat(
            [
                {"role": "system", "content": "你是获客策略分析师。根据行业线索数据，给出 2~3 句聚焦建议（主攻哪个行业、为什么）。"},
                {"role": "user", "content": f"线索行业分布：\n{text}\n\n请给建议。"},
            ],
            temperature=0.4,
        )
    except Exception:
        return "聚焦分析生成失败，请参考行业分布数据。"


class ChatIn(BaseModel):
    message: str


@app.post("/api/chat")
def chat(body: ChatIn) -> dict:
    reply = llm.chat(
        [
            {"role": "system", "content": f"你是企业「{config.name}」的官网销售客服，产品是「{'、'.join(config.products)}」。热情专业地介绍产品、解答客户问题，并在合适时引导客户留下联系方式（姓名/公司/电话）。"},
            {"role": "user", "content": body.message},
        ],
        temperature=0.5,
    )
    return {"reply": reply}
