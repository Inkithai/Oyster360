"""Add tenant, operations, inventory and document tables.

Revision ID: 003
Revises: 002
Create Date: 2026-08-12 00:53:19.053525
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The initial enum predates the read-only VIEWER role.
    if op.get_bind().dialect.name == 'postgresql':
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'VIEWER'")

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('resource', sa.String(), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)

    op.create_table('feature_flags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_feature_flags_id'), 'feature_flags', ['id'], unique=False)

    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    op.create_table('conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)

    op.create_table('knowledge_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('document_type', sa.String(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('processing_status', sa.String(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_documents_id'), 'knowledge_documents', ['id'], unique=False)

    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

    op.create_table('organization_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_members_id'), 'organization_members', ['id'], unique=False)

    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('token', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)

    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True),
        sa.Column('plan', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_subscriptions_organization_id'), 'subscriptions', ['organization_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_stripe_customer_id'), 'subscriptions', ['stripe_customer_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_stripe_subscription_id'), 'subscriptions', ['stripe_subscription_id'], unique=True)

    op.create_table('suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)
    op.create_index(op.f('ix_suppliers_organization_id'), 'suppliers', ['organization_id'], unique=False)

    op.create_table('document_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.String(), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=True),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['knowledge_documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_id'), 'document_chunks', ['id'], unique=False)

    op.create_table('inventory_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('SPAWN', 'SUBSTRATE', 'GROW_BAG', 'PACKAGING', 'CLEANING', 'OTHER', name='itemcategory'), nullable=False),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('current_stock', sa.Float(), nullable=True),
        sa.Column('reorder_level', sa.Float(), nullable=True),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_items_id'), 'inventory_items', ['id'], unique=False)

    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('content', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)

    op.create_table('purchase_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'ORDERED', 'RECEIVED', 'CANCELLED', name='purchaseorderstatus'), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('expected_date', sa.DateTime(), nullable=True),
        sa.Column('received_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    op.create_index(op.f('ix_purchase_orders_id'), 'purchase_orders', ['id'], unique=False)
    op.create_index(op.f('ix_purchase_orders_organization_id'), 'purchase_orders', ['organization_id'], unique=False)

    op.create_table('inventory_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=True),
        sa.Column('transaction_type', sa.Enum('IN', 'OUT', 'ADJUSTMENT', name='transactiontype'), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('performed_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['inventory_items.id'], ),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_transactions_id'), 'inventory_transactions', ['id'], unique=False)

    op.create_table('purchase_order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=True),
        sa.Column('item_name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=True),
        sa.Column('received_quantity', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_order_items_id'), 'purchase_order_items', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_purchase_order_items_id'), table_name='purchase_order_items')
    op.drop_table('purchase_order_items')
    op.drop_index(op.f('ix_inventory_transactions_id'), table_name='inventory_transactions')
    op.drop_table('inventory_transactions')
    op.drop_index(op.f('ix_purchase_orders_organization_id'), table_name='purchase_orders')
    op.drop_index(op.f('ix_purchase_orders_id'), table_name='purchase_orders')
    op.drop_table('purchase_orders')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_inventory_items_id'), table_name='inventory_items')
    op.drop_table('inventory_items')
    op.drop_index(op.f('ix_document_chunks_id'), table_name='document_chunks')
    op.drop_table('document_chunks')
    op.drop_index(op.f('ix_suppliers_organization_id'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_id'), table_name='suppliers')
    op.drop_table('suppliers')
    op.drop_index(op.f('ix_subscriptions_stripe_subscription_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_stripe_customer_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_organization_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_index(op.f('ix_organization_members_id'), table_name='organization_members')
    op.drop_table('organization_members')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_knowledge_documents_id'), table_name='knowledge_documents')
    op.drop_table('knowledge_documents')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    op.drop_table('conversations')
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
    op.drop_index(op.f('ix_feature_flags_id'), table_name='feature_flags')
    op.drop_table('feature_flags')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
