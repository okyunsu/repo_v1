from typing import Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy import select
from app.foundation.infra.database.database import AsyncSessionLocal
from app.foundation.infra.database.models import Company

from app.domain.service.dart_api_service import DartApiService
from app.domain.model.schema.company_schema import CompanySchema

logger = logging.getLogger(__name__)

class CompanyInfoService:
    """
    회사 정보 조회 서비스
    
    회사 정보를 DB에서 조회하고, 없으면 DART API를 통해 조회합니다.
    
    의존성:
    - DartApiService: DART API 통신을 위한 서비스
    """
    
    def __init__(self, dart_api_service: Optional[DartApiService] = None):
        """
        서비스 초기화
        
        Args:
            dart_api_service: DART API 서비스 (없으면 새로 생성)
        """
        self.dart_api = dart_api_service or DartApiService()
        logger.info("CompanyInfoService가 초기화되었습니다.")

    async def get_company_info(self, company_name: str) -> CompanySchema:
        """
        회사 정보를 조회합니다.
        
        Args:
            company_name: 회사명
            
        Returns:
            CompanySchema: 회사 정보
            
        Raises:
            ValueError: 회사 정보를 찾을 수 없는 경우
        """
        # 1. DB에서 회사 정보 조회
        db_company = await self._get_company_from_db(company_name)
        if db_company:
            return self._create_company_schema_from_db(db_company)
            
        # 2. DART API에서 회사 정보 조회
        dart_company = await self.dart_api.get_company_info(company_name)
        if not dart_company:
            raise ValueError(f"회사 정보를 찾을 수 없습니다: {company_name}")
            
        # 3. 회사 정보 저장
        await self._save_company_info(dart_company)
        
        return CompanySchema(**dart_company)

    async def _get_company_from_db(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        DB에서 회사 정보를 조회합니다.
        
        Args:
            company_name: 회사명
            
        Returns:
            Optional[Dict]: 회사 정보 (없으면 None)
        """
        try:
            async with AsyncSessionLocal() as session:
                query = select(Company).where(Company.corp_name == company_name)
                result = await session.execute(query)
                company = result.scalar_one_or_none()
                
                if company:
                    return {
                        "corp_code": company.corp_code,
                        "corp_name": company.corp_name,
                        "stock_code": company.stock_code
                    }
                return None
        except Exception as e:
            logger.error(f"회사 정보 조회 중 오류 발생: {str(e)}")
            return None
    
    def _create_company_schema_from_db(self, db_company: Dict[str, Any]) -> CompanySchema:
        """
        DB 데이터로부터 CompanySchema 객체를 생성합니다.
        
        Args:
            db_company: DB에서 조회한 회사 정보
            
        Returns:
            CompanySchema: 회사 정보 객체
        """
        now = datetime.now().isoformat()
        return CompanySchema(
            corp_code=db_company["corp_code"],
            corp_name=db_company["corp_name"],
            stock_code=db_company["stock_code"],
            created_at=now,
            updated_at=now
        )
        
    async def _save_company_info(self, company_info: Dict[str, Any]) -> None:
        """
        회사 정보를 DB에 저장합니다.
        
        Args:
            company_info: 회사 정보
        """
        try:
            async with AsyncSessionLocal() as session:
                # 기존 회사 정보 확인
                query = select(Company).where(Company.corp_code == company_info["corp_code"])
                result = await session.execute(query)
                existing_company = result.scalar_one_or_none()
                
                if existing_company:
                    # 업데이트
                    existing_company.corp_name = company_info["corp_name"]
                    existing_company.stock_code = company_info.get("stock_code", "")
                else:
                    # 새로 생성
                    company = Company(
                        corp_code=company_info["corp_code"],
                        corp_name=company_info["corp_name"],
                        stock_code=company_info.get("stock_code", "")
                    )
                    session.add(company)
                
                await session.commit()
        except Exception as e:
            logger.error(f"회사 정보 저장 중 오류 발생: {str(e)}")
            raise 