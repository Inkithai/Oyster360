"""Add Sri Lankan mushroom-farm MVP tables (expenses, buyers, sales, bag/flush fields).

Revision ID: 005
Revises: 004
Create Date: 2026-10-12 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('batches', sa.Column('expected_harvest_date', sa.DateTime(), nullable=True))
    op.add_column('batches', sa.Column('bags_prepared', sa.Integer(), server_default='500', nullable=True))
    op.add_column('batches', sa.Column('bags_inoculated', sa.Integer(), server_default='500', nullable=True))
    op.add_column('batches', sa.Column('bags_contaminated', sa.Integer(), server_default='0', nullable=True))
    op.add_column('batches', sa.Column('bags_harvested', sa.Integer(), server_default='0', nullable=True))
    op.add_column('batches', sa.Column('notes', sa.String(), nullable=True))

    op.add_column('harvests', sa.Column('flush_number', sa.Integer(), server_default='1', nullable=True))
    op.add_column('harvests', sa.Column('unsold_kg', sa.Float(), server_default='0', nullable=True))
    op.add_column('harvests', sa.Column('spoiled_kg', sa.Float(), server_default='0', nullable=True))
    op.add_column('harvests', sa.Column('notes', sa.String(), nullable=True))

    op.create_table(
        'farm_expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column(
            'category',
            sa.Enum(
                'SUBSTRATE', 'SPAWN', 'BAGS', 'PACKAGING',
                'ELECTRICITY', 'WATER', 'LABOUR', 'TRANSPORT', 'OTHER',
                name='expensecategory',
            ),
            nullable=False,
        ),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('amount_lkr', sa.Float(), nullable=False),
        sa.Column('expense_date', sa.DateTime(), nullable=True),
        sa.Column('recorded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id']),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_farm_expenses_id'), 'farm_expenses', ['id'], unique=False)
    op.create_index(
        op.f('ix_farm_expenses_organization_id'),
        'farm_expenses',
        ['organization_id'],
        unique=False,
    )

    op.create_table(
        'buyers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column(
            'buyer_type',
            sa.Enum(
                'RETAILER', 'RESTAURANT', 'WHOLESALER',
                'DIRECT_CUSTOMER', 'HOTEL', 'INTERMEDIARY',
                name='buyertype',
            ),
            nullable=False,
        ),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_buyers_id'), 'buyers', ['id'], unique=False)
    op.create_index(op.f('ix_buyers_organization_id'), 'buyers', ['organization_id'], unique=False)

    op.create_table(
        'harvest_sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('buyer_id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('harvest_id', sa.Integer(), nullable=True),
        sa.Column('quantity_kg', sa.Float(), nullable=False),
        sa.Column('price_per_kg_lkr', sa.Float(), nullable=False),
        sa.Column('total_amount_lkr', sa.Float(), nullable=False),
        sa.Column('amount_paid_lkr', sa.Float(), nullable=False),
        sa.Column('balance_due_lkr', sa.Float(), nullable=False),
        sa.Column(
            'payment_status',
            sa.Enum('PAID', 'PARTIAL', 'UNPAID', name='paymentstatus'),
            nullable=False,
        ),
        sa.Column('sale_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('recorded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id']),
        sa.ForeignKeyConstraint(['buyer_id'], ['buyers.id']),
        sa.ForeignKeyConstraint(['harvest_id'], ['harvests.id']),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_harvest_sales_id'), 'harvest_sales', ['id'], unique=False)
    op.create_index(
        op.f('ix_harvest_sales_organization_id'),
        'harvest_sales',
        ['organization_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_harvest_sales_organization_id'), table_name='harvest_sales')
    op.drop_index(op.f('ix_harvest_sales_id'), table_name='harvest_sales')
    op.drop_table('harvest_sales')

    op.drop_index(op.f('ix_buyers_organization_id'), table_name='buyers')
    op.drop_index(op.f('ix_buyers_id'), table_name='buyers')
    op.drop_table('buyers')

    op.drop_index(op.f('ix_farm_expenses_organization_id'), table_name='farm_expenses')
    op.drop_index(op.f('ix_farm_expenses_id'), table_name='farm_expenses')
    op.drop_table('farm_expenses')

    op.drop_column('harvests', 'notes')
    op.drop_column('harvests', 'spoiled_kg')
    op.drop_column('harvests', 'unsold_kg')
    op.drop_column('harvests', 'flush_number')

    op.drop_column('batches', 'notes')
    op.drop_column('batches', 'bags_harvested')
    op.drop_column('batches', 'bags_contaminated')
    op.drop_column('batches', 'bags_inoculated')
    op.drop_column('batches', 'bags_prepared')
    op.drop_column('batches', 'expected_harvest_date')
