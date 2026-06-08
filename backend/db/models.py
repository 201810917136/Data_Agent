from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text, ARRAY
from db.session import Base

class SqlSchemaMetadata(Base):
    __tablename__ = "sql_schema_metadata"
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(255), nullable=False)
    table_comment = Column(String(500))
    column_name = Column(String(255))
    business_terms = Column(ARRAY(String))
    column_comment = Column(String(500))
    layer = Column(String(20), nullable=False)
    permission_level = Column(String(50))
    is_join_key = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class QueryExample(Base):
    __tablename__ = "query_examples"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    sql = Column(Text, nullable=False)
    layer = Column(String(20))
    tags = Column(ARRAY(String))
    created_at = Column(DateTime)

class UserPermission(Base):
    __tablename__ = "user_permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    allowed_tables = Column(ARRAY(String))
    allowed_columns = Column(ARRAY(String))
    denied_columns = Column(ARRAY(String))
    created_at = Column(DateTime)
