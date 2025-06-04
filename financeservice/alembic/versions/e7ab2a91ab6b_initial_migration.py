"""Initial migration

Revision ID: e7ab2a91ab6b
Revises: 
Create Date: 2025-05-27 12:22:01.334355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7ab2a91ab6b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 회사 정보 테이블
    op.create_table('companies',
        sa.Column('corp_code', sa.String(length=20), nullable=False),
        sa.Column('corp_name', sa.String(length=100), nullable=False),
        sa.Column('stock_code', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('corp_code')
    )
    
    # 재무제표 유형 테이블
    op.create_table('statement',
        sa.Column('sj_div', sa.String(length=10), nullable=False),
        sa.Column('sj_nm', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('sj_div')
    )
    
    # 보고서 정보 테이블
    op.create_table('reports',
        sa.Column('rcept_no', sa.String(length=20), nullable=False),
        sa.Column('reprt_code', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('rcept_no')
    )
    
    # 재무 데이터 테이블
    op.create_table('financials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('corp_code', sa.String(length=20), nullable=False),
        sa.Column('bsns_year', sa.String(length=4), nullable=False),
        sa.Column('sj_div', sa.String(length=10), nullable=False),
        sa.Column('account_nm', sa.String(length=100), nullable=False),
        sa.Column('thstrm_nm', sa.String(length=20), nullable=True),
        sa.Column('thstrm_amount', sa.Numeric(), nullable=True),
        sa.Column('frmtrm_nm', sa.String(length=20), nullable=True),
        sa.Column('frmtrm_amount', sa.Numeric(), nullable=True),
        sa.Column('bfefrmtrm_nm', sa.String(length=20), nullable=True),
        sa.Column('bfefrmtrm_amount', sa.Numeric(), nullable=True),
        sa.Column('ord', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('rcept_no', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['corp_code'], ['companies.corp_code'], ),
        sa.ForeignKeyConstraint(['rcept_no'], ['reports.rcept_no'], ),
        sa.ForeignKeyConstraint(['sj_div'], ['statement.sj_div'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('corp_code', 'bsns_year', 'sj_div', 'account_nm', name='_financial_unique')
    )
    
    # 재무 비율 테이블
    op.create_table('metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('corp_code', sa.String(length=20), nullable=False),
        sa.Column('corp_name', sa.String(length=100), nullable=True),
        sa.Column('bsns_year', sa.String(length=4), nullable=False),
        sa.Column('debt_ratio', sa.Numeric(), nullable=True),
        sa.Column('current_ratio', sa.Numeric(), nullable=True),
        sa.Column('interest_coverage_ratio', sa.Numeric(), nullable=True),
        sa.Column('operating_profit_ratio', sa.Numeric(), nullable=True),
        sa.Column('net_profit_ratio', sa.Numeric(), nullable=True),
        sa.Column('roe', sa.Numeric(), nullable=True),
        sa.Column('roa', sa.Numeric(), nullable=True),
        sa.Column('debt_dependency', sa.Numeric(), nullable=True),
        sa.Column('cash_flow_debt_ratio', sa.Numeric(), nullable=True),
        sa.Column('sales_growth', sa.Numeric(), nullable=True),
        sa.Column('operating_profit_growth', sa.Numeric(), nullable=True),
        sa.Column('eps_growth', sa.Numeric(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['corp_code'], ['companies.corp_code'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('corp_code', 'bsns_year', name='_metric_unique')
    )


def downgrade() -> None:
    op.drop_table('metrics')
    op.drop_table('financials')
    op.drop_table('reports')
    op.drop_table('statement')
    op.drop_table('companies')
