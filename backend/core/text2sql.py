# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text
from db.models import SqlSchemaMetadata
from core.sql_validator import validate_sql
import re
import uuid


def build_schema_context(db: Session) -> str:
    tables = db.query(SqlSchemaMetadata).filter(
        SqlSchemaMetadata.layer.in_(["DWS", "ADS", "DIM"])
    ).all()
    context = ""
    current_table = ""
    for t in tables:
        if t.table_name != current_table:
            if current_table:
                context += ")" + NL
            ctx_name = t.table_comment or t.table_name
            context += "-- " + ctx_name + NL + "CREATE TABLE " + t.table_name + "(" + NL
            current_table = t.table_name
        comment = t.column_comment or ""
        terms = ", ".join(t.business_terms) if t.business_terms else ""
        note = " -- " + comment
        if terms:
            note += " (业务术语: " + terms + ")"
        context += "    " + t.column_name + note + NL
    if current_table:
        context += ")" + NL
    return context


def _build_explanation_system_prompt(schema_context: str) -> str:
    return (
        "你是二手车拍卖数据仓库的查询助手。请按照以下结构回答：" + NL
        + NL
        + "1. [问题理解]用一句话解释你对用户问题的理解" + NL
        + "2. [涉及表]列出会用到的数据表及其作用" + NL
        + "3. [查询逻辑]说明查询思路" + NL
        + "4. [生成的SQL]用 triple-backtick-sql 包裹最终 SQL" + NL
        + NL
        + "相关表结构：" + NL
        + schema_context + NL
        + NL
        + "注意：优先使用 ADS/DWS 聚合层" + NL
        + "- SQL 必须是可执行的 PostgreSQL 语句"
    )


def extract_sql(response: str) -> str:
    BT3 = chr(96) * 3
    match = re.search(BT3 + r"sql\\s*(.*?)\\s*" + BT3, response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return response.strip()


def _fallback_sql(user_question: str) -> str:
    q = user_question.lower()
    if "门店" in q:
        return "SELECT s.name as store_name, d.total_amount, d.auction_count, d.sold_count FROM dws_ucar_store_aution_1d d JOIN dim_stores s ON d.store_id = s.id WHERE d.stat_date = CURRENT_DATE - 1 ORDER BY d.total_amount DESC"
    elif "GMV" in q or "销售" in q:
        return "SELECT SUM(total_amount) as gmv FROM dws_ucar_store_aution_1d WHERE stat_date = CURRENT_DATE - 1"
    elif "品牌" in q or "流拍" in q:
        return "SELECT s.name, d.unsold_count::float / NULLIF(d.auction_count, 0) as unsold_rate FROM dws_ucar_store_aution_1d d JOIN dim_stores s ON d.store_id = s.id WHERE d.stat_date = CURRENT_DATE - 1 ORDER BY unsold_rate DESC LIMIT 5"
    return "SELECT * FROM dim_stores"


def _fallback_explanation(user_question: str) -> dict:
    q = user_question.lower()
    if "门店" in q:
        return {"question_understanding": "查询昨日各门店销售情况", "tables_involved": "dws_ucar_store_aution_1d, dim_stores", "query_logic": "筛选昨日数据关联门店名称按销售额降序", "sql": _fallback_sql(user_question)}
    elif "GMV" in q or "销售" in q:
        return {"question_understanding": "查询昨日总销售额", "tables_involved": "dws_ucar_store_aution_1d", "query_logic": "对 total_amount 做 SUM 聚合", "sql": _fallback_sql(user_question)}
    return {"question_understanding": user_question, "tables_involved": "dim_stores", "query_logic": "兜底返回门店列表", "sql": "SELECT * FROM dim_stores"}


def detect_chart_type(data: list) -> str:
    if not data or len(data) == 1:
        return "table"
    first = data[0]
    if any(k in first for k in ["date", "stat_date", "stat_month", "create_time"]):
        return "line"
    if len(data) <= 10:
        return "bar"
    return "table"


async def preview_query(user_question: str, db: Session) -> dict:
    trace_id = str(uuid.uuid4())[:8]
    schema_context = build_schema_context(db)
    system_prompt = _build_explanation_system_prompt(schema_context)
    parsed = None
    sql = None
    for attempt in range(3):
        try:
            from core.llm import call_llm
            response = await call_llm(system_prompt, user_question, trace_id=trace_id)
            parsed = _parse_explanation_response(response)
            sql = parsed.get("sql")
            if sql and "SELECT" in sql.upper():
                break
        except Exception:
            pass
        if attempt == 2:
            parsed = _fallback_explanation(user_question)
            sql = parsed.get("sql")
            break
    if not sql:
        parsed = _fallback_explanation(user_question)
        sql = parsed.get("sql")
    validation = validate_sql(sql, db)
    return {
        "sql": sql,
        "question_understanding": parsed.get("question_understanding", user_question),
        "tables_involved": parsed.get("tables_involved", ""),
        "query_logic": parsed.get("query_logic", ""),
        "sql_valid": validation.success,
        "error": validation.error if not validation.success else None,
        "trace_id": trace_id,
    }


async def execute_query(user_question: str, sql: str, db: Session) -> dict:
    trace_id = str(uuid.uuid4())[:8]
    validation = validate_sql(sql, db)
    if not validation.success:
        return {"success": False, "error": validation.error, "sql": sql, "trace_id": trace_id}
    try:
        result = db.execute(sa_text(sql))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return {
            "success": True,
            "sql": sql,
            "data": rows,
            "chart_type": detect_chart_type(rows),
            "trace_id": trace_id,
        }
    except Exception as e:
        return {"success": False, "error": "执行错误: " + str(e), "sql": sql, "trace_id": trace_id}


async def generate_sql(user_question: str, db: Session) -> dict:
    preview = await preview_query(user_question, db)
    if not preview.get("sql"):
        return {"success": False, "error": "未生成 SQL", "trace_id": preview.get("trace_id")}
    try:
        result = db.execute(sa_text(preview["sql"]))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return {
            "success": True,
            "sql": preview["sql"],
            "data": rows,
            "chart_type": detect_chart_type(rows),
            "trace_id": preview["trace_id"],
        }
    except Exception as e:
        return {"success": False, "error": "执行错误: " + str(e), "sql": preview["sql"], "trace_id": preview.get("trace_id")}


def _parse_explanation_response(response: str) -> dict:
    result = {"question_understanding": "", "tables_involved": "", "query_logic": "", "sql": None}
    for key, marker in [
        ("question_understanding", "[问题理解]"),
        ("tables_involved", "[涉及表]"),
        ("query_logic", "[查询逻辑]"),
    ]:
        if marker in response:
            after = response[idx + len(marker):]
            next_markers = ["[涉及表]", "[查询逻辑]", "[生成的SQL]"]
            next_idx = len(after)
            for m in next_markers:
                if m in after and after.index(m) < next_idx:
                    next_idx = after.index(m)
            result[key] = after[:next_idx].strip()
    BT3 = chr(96) * 3
    sql_match = re.search(BT3 + r"sql\s*(.*?)\s*" + BT3, response, re.DOTALL | re.IGNORECASE)
    if sql_match:
        result["sql"] = sql_match.group(1).strip()
    return result
