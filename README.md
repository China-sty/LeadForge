# LeadForge — 面向 ToB 制造企业的 AI 获客引擎

> **Turn cold leads into warm deals**（把冷线索锻造成热订单）

一个**通用、多租户**的 ToB 制造企业 AI 获客平台。任何制造企业接入后，通过配置「目标客户画像 + 评分规则」，即可用 AI 补齐「**找客户 → 触达客户 → 承接转化 → 聚焦优化**」的完整获客链路。

## 特性

- **潜客挖掘**：从企业数据源拉取候选企业，LLM 判断是否为目标客户
- **线索评分**：行业匹配度 / 采购能力 / 渠道价值 三维打分，加权排序
- **智能触达**：为每个目标客户生成**个性化触达话术**（按行业痛点切入）
- **询盘承接**：自动回复询盘、生成报价初稿与下一步建议
- **官网 AI 客服**：落地页 + 聊天式客服，介绍产品、引导留资
- **转化漏斗**：待触达 → 已触达 → 已回复 → 报价中 → 打样中 → 已成交 六阶段跟踪
- **聚焦分析**：AI 分析行业线索分布，给出「主攻哪个行业」的建议
- **多租户配置化**：企业画像 / 产品线 / 评分规则均可配置，一套引擎服务多个企业

## 架构

多智能体协作，复用「结构化输出（function calling + Pydantic）+ 确定性加权」的成熟模式：

```
数据源 → 潜客挖掘 Agent → 线索评分 Agent → 触达 Agent（话术生成）→ 询盘 Agent（报价）
                        └────────── 老板看板 / 销售工具 ──────────┘
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 LLM

```bash
cp .env.example .env   # 填 OPENAI_API_KEY / OPENAI_BASE_URL / LLM_MODEL
```

### 3. 运行

```bash
# 命令行跑一次挖掘（输出排序好的客户 + 话术）
python -m leadforge.main

# Web 看板
python -m uvicorn leadforge.web:app --host 127.0.0.1 --port 8002
# 浏览器打开 http://127.0.0.1:8002，点「开始挖掘」
```

## 目录结构

```
LeadForge/
├─ plan.md                      # 实施计划（5 个 Phase）
├─ config/enterprise.yaml       # 企业配置（多租户：目标画像/评分规则）
├─ leadforge/
│  ├─ main.py                   # CLI 入口
│  ├─ web.py                    # FastAPI：看板/触达/询盘/聚焦/官网客服
│  ├─ pipeline.py               # 流水线：挖掘→评分→触达
│  ├─ llm.py                    # LLM 客户端（结构化输出）
│  ├─ models.py                 # 数据模型 + 结构化输出模型
│  ├─ store.py                  # SQLite 持久化 + 漏斗统计
│  ├─ config.py                 # 企业配置加载
│  ├─ agents/
│  │  ├─ miner.py               # 潜客挖掘 Agent
│  │  ├─ scorer.py              # 线索评分 Agent
│  │  ├─ outreach.py            # 智能触达 Agent（话术生成）
│  │  └─ enquiry.py             # 询盘承接 Agent（报价）
│  └─ datasources/
│     ├─ base.py                # 数据源接口
│     └─ mock.py                # 示例数据源（演示用，脱敏）
├─ web/
│  ├─ index.html                # 老板看板（漏斗/聚焦/话术/询盘）
│  └─ landing.html              # 官网落地页 + AI 客服
└─ tests/test_pipeline.py       # 流水线冒烟测试
```

## 说明

- 当前数据源为**示例数据**（`MockDataSource`），换真实数据源只需实现 `DataSource` 接口（如工商数据 API）。
- 演示内容全部**脱敏**，不绑定任何真实企业。
- 本系统仅辅助获客，最终成交由人完成。
