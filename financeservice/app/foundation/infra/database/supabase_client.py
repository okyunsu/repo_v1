# PostgreSQL 연결을 위한 데이터베이스 설정
# 기존 supabase_client.py를 PostgreSQL 연결로 교체

from .database import get_db, AsyncSessionLocal, engine, init_db, close_db
from .models import Company, Statement, Report, Financial, Metric

# 하위 호환성을 위해 기존 변수명 유지 (점진적 마이그레이션용)
# 실제로는 SQLAlchemy 세션을 사용
db_session = AsyncSessionLocal

__all__ = [
    "get_db",
    "AsyncSessionLocal", 
    "engine",
    "init_db",
    "close_db",
    "Company",
    "Statement", 
    "Report",
    "Financial",
    "Metric",
    "db_session"
] 