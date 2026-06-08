from sqlalchemy.orm import Session
from sqlalchemy import text

class ValidationResult:
    def __init__(self, success: bool, error: str = ""):
        self.success = success
        self.error = error

def validate_sql(sql: str, db: Session) -> ValidationResult:
    sql_upper = sql.upper().strip()
    forbidden = ["DELETE", "UPDATE", "DROP", "TRUNCATE", "INSERT", "ALTER", "CREATE"]
    for kw in forbidden:
        if kw in sql_upper:
            return ValidationResult(False, f"\u7981\u6b62\u6267\u884c\u5199\u64cd\u4f5c: {kw}")
    if "SELECT" not in sql_upper:
        return ValidationResult(False, "SQL \u5fc5\u987b\u662f SELECT \u67e5\u8be2")
    try:
        db.execute(text(f"EXPLAIN {sql}"))
    except Exception as e:
        return ValidationResult(False, f"SQL \u8bed\u6cd5\u9519\u8bef: {str(e)}")
    return ValidationResult(True)
