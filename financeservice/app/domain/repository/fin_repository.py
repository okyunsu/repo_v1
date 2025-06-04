import logging
from typing import Optional, List, Dict, Any, Union
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.foundation.infra.database.database import AsyncSessionLocal
from app.foundation.infra.database.models import Company, Statement, Report, Financial, Metric
from app.foundation.infra.utils.convert import convert_amount

logger = logging.getLogger(__name__)

# ===== 데이터 조회 함수 =====

async def get_company_info(company_name: str = None, corp_code: str = None) -> Optional[Dict[str, Any]]:
    """회사 정보를 조회합니다. 회사명 또는 회사 코드로 조회 가능합니다."""
    try:
        async with AsyncSessionLocal() as session:
            query = select(Company)
            
            if company_name:
                query = query.where(Company.corp_name == company_name)
            elif corp_code:
                query = query.where(Company.corp_code == corp_code)
            else:
                raise ValueError("회사명 또는 회사 코드를 입력해야 합니다.")
                
            result = await session.execute(query)
            company = result.scalar_one_or_none()
            
            if not company:
                return None
                
            return {
                "corp_code": company.corp_code,
                "corp_name": company.corp_name,
                "stock_code": company.stock_code
            }
    except Exception as e:
        logger.error(f"회사 정보 조회 중 오류 발생: {str(e)}")
        return None

async def get_financial_statements(
    company_name: str = None,
    corp_code: str = None,
    year: Optional[Union[int, str]] = None,
    limit_years: int = None
) -> List[Dict[str, Any]]:
    """재무제표 데이터를 조회합니다."""
    try:
        if company_name:
            corp_code = await _get_corp_code_by_name(company_name)
            if not corp_code:
                return []
        
        if not corp_code:
            raise ValueError("회사명 또는 회사 코드를 입력해야 합니다.")
            
        async with AsyncSessionLocal() as session:
            query = select(Financial).options(
                selectinload(Financial.company),
                selectinload(Financial.statement)
            ).where(Financial.corp_code == corp_code)
            
            if year is not None:
                query = query.where(Financial.bsns_year == str(year))
                
            if limit_years and not year:
                years = await _get_recent_years(corp_code, limit_years)
                if years:
                    query = query.where(Financial.bsns_year.in_(years))
                    
            query = query.order_by(desc(Financial.bsns_year), Financial.sj_div, Financial.ord)
            
            result = await session.execute(query)
            financials = result.scalars().all()
            
            return [_financial_to_dict(financial) for financial in financials]
    except Exception as e:
        logger.error(f"재무제표 데이터 조회 중 오류 발생: {str(e)}")
        return []

async def save_financial_statements(statements: List[Dict[str, Any]]) -> bool:
    """재무제표 데이터를 저장합니다."""
    if not statements:
        logger.warning("저장할 재무제표 데이터가 없습니다.")
        return False
        
    try:
        async with AsyncSessionLocal() as session:
            # 1. statement 테이블에 재무제표 유형 저장
            await _save_statement_types(session, statements)
            
            # 2. companies 테이블에 회사 정보 저장
            await _save_company_info(session, statements[0])
            
            # 3. reports 테이블에 보고서 정보 저장
            await _save_report_info(session, statements[0])
            
            # 4. financials 테이블에 재무제표 데이터 저장
            await _save_financial_data(session, statements)
            
            await session.commit()
            return True
    except Exception as e:
        logger.error(f"재무제표 데이터 저장 중 오류 발생: {str(e)}")
        return False

async def _get_corp_code_by_name(company_name: str) -> Optional[str]:
    """회사명으로 회사 코드를 조회합니다."""
    try:
        async with AsyncSessionLocal() as session:
            query = select(Company.corp_code).where(Company.corp_name == company_name)
            result = await session.execute(query)
            corp_code = result.scalar_one_or_none()
            return corp_code
    except Exception as e:
        logger.error(f"회사 코드 조회 중 오류 발생: {str(e)}")
        return None

async def _get_recent_years(corp_code: str, limit: int) -> List[str]:
    """최근 N개 연도를 조회합니다."""
    try:
        async with AsyncSessionLocal() as session:
            query = select(Financial.bsns_year).where(
                Financial.corp_code == corp_code
            ).distinct().order_by(desc(Financial.bsns_year)).limit(limit)
            
            result = await session.execute(query)
            years = [row[0] for row in result.fetchall()]
            return years
    except Exception as e:
        logger.error(f"연도 조회 중 오류 발생: {str(e)}")
        return []

async def _save_statement_types(session: AsyncSession, statements: List[Dict[str, Any]]) -> None:
    """재무제표 유형을 저장합니다."""
    statement_types = {}
    for stmt in statements:
        sj_div = stmt["sj_div"]
        if sj_div not in statement_types:
            statement_types[sj_div] = stmt["sj_nm"]
    
    for sj_div, sj_nm in statement_types.items():
        # 기존 데이터 확인
        query = select(Statement).where(Statement.sj_div == sj_div)
        result = await session.execute(query)
        existing = result.scalar_one_or_none()
        
        if not existing:
            statement = Statement(sj_div=sj_div, sj_nm=sj_nm)
            session.add(statement)

async def _save_company_info(session: AsyncSession, statement: Dict[str, Any]) -> None:
    """회사 정보를 저장합니다."""
    try:
        corp_code = statement["corp_code"]
        
        # 기존 회사 정보 확인
        query = select(Company).where(Company.corp_code == corp_code)
        result = await session.execute(query)
        existing_company = result.scalar_one_or_none()
        
        company_data = {
            "corp_code": corp_code,
            "corp_name": existing_company.corp_name if existing_company else statement.get("corp_name", ""),
            "stock_code": existing_company.stock_code if existing_company else statement.get("stock_code", "")
        }
        
        if not company_data["corp_name"]:
            from app.domain.service.dart_api_service import DartApiService
            dart_api = DartApiService()
            company_info = await dart_api.get_company_info(corp_code)
            if company_info:
                company_data["corp_name"] = company_info.corp_name
                company_data["stock_code"] = company_info.stock_code
            else:
                raise ValueError("회사명(corp_name)을 찾을 수 없습니다.")
        
        if existing_company:
            # 업데이트
            existing_company.corp_name = company_data["corp_name"]
            existing_company.stock_code = company_data["stock_code"]
        else:
            # 새로 생성
            company = Company(**company_data)
            session.add(company)
            
    except Exception as e:
        logger.error(f"회사 정보 저장 중 오류 발생: {str(e)}")
        raise

async def _save_report_info(session: AsyncSession, statement: Dict[str, Any]) -> None:
    """보고서 정보를 저장합니다."""
    rcept_no = statement["rcept_no"]
    
    # 기존 보고서 정보 확인
    query = select(Report).where(Report.rcept_no == rcept_no)
    result = await session.execute(query)
    existing_report = result.scalar_one_or_none()
    
    if not existing_report:
        report = Report(
            rcept_no=rcept_no,
            reprt_code=statement.get("reprt_code", "11011")
        )
        session.add(report)

async def _save_financial_data(session: AsyncSession, statements: List[Dict[str, Any]]) -> None:
    """재무제표 데이터를 저장합니다."""
    for stmt in statements:
        try:
            if await _is_duplicate_financial_data(session, stmt):
                continue
                
            financial_data = _prepare_financial_data(stmt)
            financial = Financial(**financial_data)
            session.add(financial)
            
            # 배치 크기마다 flush 실행
            if len(session.new) >= 100:  # 100개씩 배치 처리
                await session.flush()
                
        except Exception as e:
            logger.error(f"재무제표 데이터 저장 중 개별 오류: {stmt.get('account_nm', 'Unknown')} - {str(e)}")
            continue
    
    # 남은 데이터 flush
    if session.new:
        await session.flush()

async def _is_duplicate_financial_data(session: AsyncSession, stmt: Dict[str, Any]) -> bool:
    """중복된 재무제표 데이터인지 확인합니다."""
    query = select(Financial.id).where(
        and_(
            Financial.corp_code == stmt["corp_code"],
            Financial.bsns_year == stmt["bsns_year"],
            Financial.sj_div == stmt["sj_div"],
            Financial.account_nm == stmt["account_nm"]
        )
    )
    
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        logger.info(f"이미 존재하는 데이터 건너뛰기: {stmt['corp_code']} - {stmt['bsns_year']} - {stmt['sj_div']} - {stmt['account_nm']}")
        return True
    return False

def _prepare_financial_data(stmt: Dict[str, Any]) -> Dict[str, Any]:
    """재무제표 데이터를 저장 형식으로 변환합니다."""
    # ord 필드 타입 변환
    ord_value = stmt.get("ord")
    if ord_value is not None:
        try:
            ord_value = int(ord_value) if ord_value != '' else None
        except (ValueError, TypeError):
            ord_value = None
    
    return {
        "corp_code": stmt["corp_code"],
        "bsns_year": stmt["bsns_year"],
        "sj_div": stmt["sj_div"],
        "account_nm": stmt["account_nm"],
        "thstrm_nm": stmt.get("thstrm_nm"),
        "thstrm_amount": convert_amount(stmt.get("thstrm_amount")),
        "frmtrm_nm": stmt.get("frmtrm_nm"),
        "frmtrm_amount": convert_amount(stmt.get("frmtrm_amount")),
        "bfefrmtrm_nm": stmt.get("bfefrmtrm_nm"),
        "bfefrmtrm_amount": convert_amount(stmt.get("bfefrmtrm_amount")),
        "ord": ord_value,
        "currency": stmt.get("currency", "KRW"),
        "rcept_no": stmt.get("rcept_no")
    }

def _financial_to_dict(financial: Financial) -> Dict[str, Any]:
    """Financial 모델을 딕셔너리로 변환합니다."""
    return {
        "id": financial.id,
        "corp_code": financial.corp_code,
        "bsns_year": financial.bsns_year,
        "sj_div": financial.sj_div,
        "account_nm": financial.account_nm,
        "thstrm_nm": financial.thstrm_nm,
        "thstrm_amount": financial.thstrm_amount,
        "frmtrm_nm": financial.frmtrm_nm,
        "frmtrm_amount": financial.frmtrm_amount,
        "bfefrmtrm_nm": financial.bfefrmtrm_nm,
        "bfefrmtrm_amount": financial.bfefrmtrm_amount,
        "ord": financial.ord,
        "currency": financial.currency,
        "rcept_no": financial.rcept_no,
        "created_at": financial.created_at,
        "updated_at": financial.updated_at,
        "companies": {
            "corp_name": financial.company.corp_name,
            "stock_code": financial.company.stock_code
        } if financial.company else None,
        "statement": {
            "sj_nm": financial.statement.sj_nm
        } if financial.statement else None
    }

async def get_existing_years(company_name: str) -> List[str]:
    """회사의 기존 데이터 연도 목록을 조회합니다."""
    try:
        corp_code = await _get_corp_code_by_name(company_name)
        if not corp_code:
            return []
            
        async with AsyncSessionLocal() as session:
            query = select(Financial.bsns_year).where(
                Financial.corp_code == corp_code
            ).distinct().order_by(desc(Financial.bsns_year))
            
            result = await session.execute(query)
            years = [row[0] for row in result.fetchall()]
            return years
    except Exception as e:
        logger.error(f"기존 연도 조회 중 오류 발생: {str(e)}")
        return []

async def check_existing_data(company_name: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """기존 데이터 확인"""
    return await get_financial_data(company_name, year)

async def get_financial_data(company_name: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """재무 데이터 조회"""
    return await get_financial_statements(company_name=company_name, year=year)

async def get_key_financial_items(company_name: str = None) -> List[Dict[str, Any]]:
    """주요 재무 항목을 조회합니다."""
    try:
        async with AsyncSessionLocal() as session:
            query = select(Financial).options(
                selectinload(Financial.company),
                selectinload(Financial.statement)
            ).where(
                Financial.account_nm.in_([
                    "자산총계", "부채총계", "자본총계", "유동자산", "유동부채",
                    "매출액", "영업이익", "당기순이익", "영업활동현금흐름"
                ])
            )
            
            if company_name:
                corp_code = await _get_corp_code_by_name(company_name)
                if corp_code:
                    query = query.where(Financial.corp_code == corp_code)
                    
            query = query.order_by(Financial.corp_code, desc(Financial.bsns_year), Financial.sj_div, Financial.account_nm)
            
            result = await session.execute(query)
            financials = result.scalars().all()
            
            return [_financial_to_dict(financial) for financial in financials]
    except Exception as e:
        logger.error(f"주요 재무 항목 조회 중 오류 발생: {str(e)}")
        return []

async def get_statement_summary() -> List[Dict[str, Any]]:
    """회사별 재무제표 종류와 데이터 수를 조회합니다."""
    try:
        async with AsyncSessionLocal() as session:
            query = select(
                Financial.corp_code,
                Company.corp_name,
                Financial.sj_div,
                Statement.sj_nm,
                func.count(Financial.id).label('count')
            ).select_from(
                Financial
            ).join(Company, Financial.corp_code == Company.corp_code
            ).join(Statement, Financial.sj_div == Statement.sj_div
            ).group_by(
                Financial.corp_code, Company.corp_name, Financial.sj_div, Statement.sj_nm
            ).order_by(Financial.corp_code, Financial.sj_div)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            return [
                {
                    "corp_code": row.corp_code,
                    "corp_name": row.corp_name,
                    "sj_div": row.sj_div,
                    "sj_nm": row.sj_nm,
                    "count": row.count
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"재무제표 요약 조회 중 오류 발생: {str(e)}")
        return []

async def get_financial_statements_by_corp_code(corp_code: str) -> List[Dict[str, Any]]:
    """회사 코드로 재무제표 데이터를 조회합니다."""
    try:
        async with AsyncSessionLocal() as session:
            query = select(Financial).where(
                Financial.corp_code == corp_code
            ).order_by(desc(Financial.bsns_year), Financial.sj_div, Financial.ord)
            
            result = await session.execute(query)
            financials = result.scalars().all()
            
            return [_financial_to_dict(financial) for financial in financials]
    except Exception as e:
        logger.error(f"재무제표 데이터 조회 중 오류 발생: {str(e)}")
        return []

async def save_financial_ratios(ratios: Dict[str, Any]) -> None:
    """재무비율을 저장합니다."""
    try:
        async with AsyncSessionLocal() as session:
            # 기존 데이터 확인
            query = select(Metric).where(
                and_(
                    Metric.corp_code == ratios["corp_code"],
                    Metric.bsns_year == ratios["bsns_year"]
                )
            )
            result = await session.execute(query)
            existing_metric = result.scalar_one_or_none()
            
            metric_data = {
                "corp_code": ratios["corp_code"],
                "corp_name": ratios["corp_name"],
                "bsns_year": ratios["bsns_year"],
                "debt_ratio": ratios.get("debt_ratio"),
                "current_ratio": ratios.get("current_ratio"),
                "interest_coverage_ratio": ratios.get("interest_coverage_ratio"),
                "operating_profit_ratio": ratios.get("operating_profit_ratio"),
                "net_profit_ratio": ratios.get("net_profit_ratio"),
                "roe": ratios.get("roe"),
                "roa": ratios.get("roa"),
                "debt_dependency": ratios.get("debt_dependency"),
                "cash_flow_debt_ratio": ratios.get("cash_flow_debt_ratio"),
                "sales_growth": ratios.get("sales_growth"),
                "operating_profit_growth": ratios.get("operating_profit_growth"),
                "eps_growth": ratios.get("eps_growth")
            }
            
            if existing_metric:
                # 업데이트
                for key, value in metric_data.items():
                    if key != "corp_code":  # Primary key는 제외
                        setattr(existing_metric, key, value)
            else:
                # 새로 생성
                metric = Metric(**metric_data)
                session.add(metric)
            
            await session.commit()
    except Exception as e:
        logger.error(f"재무비율 저장 중 오류 발생: {str(e)}")
        raise