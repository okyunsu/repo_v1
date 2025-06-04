from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

# Alembic 전용 Base 클래스
Base = declarative_base()

class Company(Base):
    """회사 정보 테이블"""
    __tablename__ = "companies"
    
    corp_code = Column(String(20), primary_key=True)
    corp_name = Column(String(100), nullable=False)
    stock_code = Column(String(20))
    
    # 관계 설정
    financials = relationship("Financial", back_populates="company")
    metrics = relationship("Metric", back_populates="company")

class Statement(Base):
    """재무제표 유형 테이블"""
    __tablename__ = "statement"
    
    sj_div = Column(String(10), primary_key=True)
    sj_nm = Column(String(100), nullable=False)
    
    # 관계 설정
    financials = relationship("Financial", back_populates="statement")

class Report(Base):
    """보고서 정보 테이블"""
    __tablename__ = "reports"
    
    rcept_no = Column(String(20), primary_key=True)
    reprt_code = Column(String(20), nullable=False)
    
    # 관계 설정
    financials = relationship("Financial", back_populates="report")

class Financial(Base):
    """재무 데이터 테이블"""
    __tablename__ = "financials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    corp_code = Column(String(20), ForeignKey("companies.corp_code"), nullable=False)
    bsns_year = Column(String(4), nullable=False)
    sj_div = Column(String(10), ForeignKey("statement.sj_div"), nullable=False)
    account_nm = Column(String(100), nullable=False)
    thstrm_nm = Column(String(20))
    thstrm_amount = Column(Numeric)
    frmtrm_nm = Column(String(20))
    frmtrm_amount = Column(Numeric)
    bfefrmtrm_nm = Column(String(20))
    bfefrmtrm_amount = Column(Numeric)
    ord = Column(Integer)
    currency = Column(String(10))
    rcept_no = Column(String(20), ForeignKey("reports.rcept_no"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    company = relationship("Company", back_populates="financials")
    statement = relationship("Statement", back_populates="financials")
    report = relationship("Report", back_populates="financials")
    
    # 유니크 제약조건
    __table_args__ = (
        UniqueConstraint('corp_code', 'bsns_year', 'sj_div', 'account_nm', name='_financial_unique'),
    )

class Metric(Base):
    """재무 비율 테이블"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    corp_code = Column(String(20), ForeignKey("companies.corp_code"), nullable=False)
    corp_name = Column(String(100))
    bsns_year = Column(String(4), nullable=False)
    debt_ratio = Column(Numeric)
    current_ratio = Column(Numeric)
    interest_coverage_ratio = Column(Numeric)
    operating_profit_ratio = Column(Numeric)
    net_profit_ratio = Column(Numeric)
    roe = Column(Numeric)
    roa = Column(Numeric)
    debt_dependency = Column(Numeric)
    cash_flow_debt_ratio = Column(Numeric)
    sales_growth = Column(Numeric)
    operating_profit_growth = Column(Numeric)
    eps_growth = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    company = relationship("Company", back_populates="metrics")
    
    # 유니크 제약조건
    __table_args__ = (
        UniqueConstraint('corp_code', 'bsns_year', name='_metric_unique'),
    ) 