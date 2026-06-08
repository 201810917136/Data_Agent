# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text
from db.models import SqlSchemaMetadata
import re

def build_schema_context(db: Session) -> str:
    tables = db.query(SqlSchemaMetadata).filter(
        SqlSchemaMetadata.layer.in_(["DWS", "ADS", "DIM"])
    ).all()
    context = ""
    current_table = ""
    for t in tables:
        if t.table_name != current_table:
            if current_table:
                context += ")\n"
            context += f"-- {t.table_comment or t.table_name}\nCREATE TABLE {t.table_name} (\n"
            current_table = t.table_name
        comment = t.column_comment or ""
        terms = ", ".join(t.business_terms) if t.business_terms else ""
        note = f" -- {comment}" + (f" (业务术语: {terms})" if terms else "")
        context += f"    {t.column_name}{note}\n"
    if current_table:
        context += ")\n"
    return context

def build_system_prompt(schema_context: str) -> str:
    return f"""你是二手车拍卖数据仓库的查询助手。

查询策略：
1. 优先查 ADS/DWS 应用层（已面向场景聚合，性能最好）
2. 需要明细时查 DWD 明细层
3. 维度过滤关联 DIM 维度表
4. 不要直接查 ODS 原始层

相关表结构：
{schema_context}

规则：
1. 生成标准 PostgreSQL SQL
2. 不使用 SELECT *
3. 只返回可执行的 SQL 语句
4. 用 ```sql 和 ``` 包裹 SQL 语句
5. 不要包含任何解释文字或分析"""

def extract_sql(response: str) -> str:
    match = re.search(r"```sql\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # 如果没有代码块，直接返回
    return response.strip()

async def generate_sql(user_question: str, db: Session) -> dict:
    schema_context = build_schema_context(db)
    system_prompt = build_system_prompt(schema_context)
    
    # LLM 调用，最多重试2次
    sql = None
    for attempt in range(3):
        try:
            from core.llm import call_llm
            response = await call_llm(system_prompt, user_question)
            sql = extract_sql(response)
            # 验证 SQL 是否包含 SELECT
            if "SELECT" in sql.upper():
                break
        except Exception as e:
            pass
        if attempt == 2:
            sql = _fallback_sql(user_question)
    
    # 如果 LLM 调用失败，使用 fallback
    if not sql:
        sql = _fallback_sql(user_question)
    
    validation = validate_sql(sql, db)
    if not validation.success:
        return {"success": False, "error": validation.error, "sql": sql}
    try:
        result = db.execute(sa_text(sql))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return {"success": True, "sql": sql, "data": rows, "chart_type": detect_chart_type(rows)}
    except Exception as e:
        return {"success": False, "error": f"执行错误: {str(e)}", "sql": sql}

def _fallback_sql(user_question: str) -> str:
    q = user_question.lower()
    if "门店" in q:
        return """SELECT s.name as store_name, d.total_amount, d.auction_count, d.sold_count
FROM dws_ucar_store_aution_1d d
JOIN dim_stores s ON d.store_id = s.id
WHERE d.stat_date = CURRENT_DATE - 1
ORDER BY d.total_amount DESC"""
    elif "GMV" in q or "销售" in q:
        return "SELECT SUM(total_amount) as gmv FROM dws_ucar_store_aution_1d WHERE stat_date = CURRENT_DATE - 1"
    elif "品牌" in q or "流拍" in q:
        return "SELECT s.name, d.unsold_count::float / NULLIF(d.auction_count, 0) as unsold_rate FROM dws_ucar_store_aution_1d d JOIN dim_stores s ON d.store_id = s.id WHERE d.stat_date = CURRENT_DATE - 1 ORDER BY unsold_rate DESC LIMIT 5"
    return "SELECT * FROM dim_stores"

def detect_chart_type(data: list) -> str:
    if not data or len(data) == 1:
        return "table"
    first = data[0]
    if any(k in first for k in ["date", "stat_date", "stat_month", "create_time"]):
        return "line"
    if len(data) <= 10:
        return "bar"
    return "table"

from core.sql_validator import validate_sql