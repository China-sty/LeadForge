"""SQLite 持久化：线索落库、阶段推进与聚合统计。"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List

from .models import Lead

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Store:
    def __init__(self, db_path: str | None = None):
        self.db_path = str(db_path or PROJECT_ROOT / "data" / "leadforge.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS leads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT, industry TEXT, scope TEXT, scale TEXT, region TEXT,
                        reason TEXT, match_score REAL, capability_score REAL, channel_score REAL,
                        total_score REAL, outreach TEXT, stage TEXT, created_at TEXT
                    )
                    """
                )
                conn.commit()
            finally:
                conn.close()

    def clear(self) -> None:
        with self._lock:
            conn = self._connect()
            try:
                conn.execute("DELETE FROM leads")
                conn.commit()
            finally:
                conn.close()

    def save_leads(self, leads: List[Lead]) -> None:
        with self._lock:
            conn = self._connect()
            try:
                for lead in leads:
                    conn.execute(
                        """
                        INSERT INTO leads
                        (company_name, industry, scope, scale, region, reason,
                         match_score, capability_score, channel_score, total_score,
                         outreach, stage, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now','localtime'))
                        """,
                        (
                            lead.company.name, lead.industry, lead.company.scope,
                            lead.company.scale, lead.company.region, lead.reason,
                            lead.scores.get("行业匹配度"),
                            lead.scores.get("采购能力"),
                            lead.scores.get("渠道价值"),
                            lead.total_score, lead.outreach, lead.stage,
                        ),
                    )
                conn.commit()
            finally:
                conn.close()

    def list_leads(self) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute("SELECT * FROM leads ORDER BY total_score DESC").fetchall()
            finally:
                conn.close()
        return [dict(r) for r in rows]

    def update_stage(self, lead_id: int, stage: str) -> None:
        with self._lock:
            conn = self._connect()
            try:
                conn.execute("UPDATE leads SET stage = ? WHERE id = ?", (stage, lead_id))
                conn.commit()
            finally:
                conn.close()

    def stats(self, threshold: float) -> Dict[str, Any]:
        leads = self.list_leads()
        total = len(leads)
        high_value = sum(1 for l in leads if (l["total_score"] or 0) >= threshold)
        avg = sum(l["total_score"] or 0 for l in leads) / total if total else 0.0

        industries: Dict[str, int] = {}
        for l in leads:
            ind = l["industry"] or "未知"
            industries[ind] = industries.get(ind, 0) + 1

        funnel: Dict[str, int] = {}
        for l in leads:
            stage = l["stage"] or "待触达"
            funnel[stage] = funnel.get(stage, 0) + 1

        return {
            "total": total,
            "high_value": high_value,
            "avg_score": round(avg, 1),
            "industries": industries,
            "funnel": funnel,
        }
