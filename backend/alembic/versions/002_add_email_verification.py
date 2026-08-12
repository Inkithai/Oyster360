"""Add email verification fields

Revision ID: 002
Revises: 001
Create Date: 2026-07-07
"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('email_verification_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('email_verification_expires', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verification_expires')