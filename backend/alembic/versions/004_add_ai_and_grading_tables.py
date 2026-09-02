"""Add AI, inspection, harvest grading tables and tenant relationships.

Revision ID: 004
Revises: 003
Create Date: 2026-08-12 01:15:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('ai_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('messages', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_conversations_id'), 'ai_conversations', ['id'], unique=False)

    op.create_table('image_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('stage', sa.String(), nullable=True),
        sa.Column('health_score', sa.Float(), nullable=True),
        sa.Column('contamination_risk', sa.String(), nullable=True),
        sa.Column('issues', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_analyses_id'), 'image_analyses', ['id'], unique=False)

    op.create_table('image_inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('ai_status', sa.String(), nullable=True),
        sa.Column('overall_health_score', sa.Float(), nullable=True),
        sa.Column('contamination_probability', sa.Float(), nullable=True),
        sa.Column('detected_stage', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_inspections_id'), 'image_inspections', ['id'], unique=False)

    op.create_table('yield_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('predicted_yield_kg', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('expected_harvest_date', sa.DateTime(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_yield_predictions_id'), 'yield_predictions', ['id'], unique=False)

    op.create_table('harvest_grades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('harvest_id', sa.Integer(), nullable=True),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('grade', sa.Enum('A', 'B', 'C', name='gradelevel'), nullable=True),
        sa.Column('quantity_kg', sa.Float(), nullable=True),
        sa.Column('price_per_kg', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('graded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.ForeignKeyConstraint(['graded_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['harvest_id'], ['harvests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_harvest_grades_id'), 'harvest_grades', ['id'], unique=False)

    op.create_table('inspection_findings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inspection_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('recommendation', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['inspection_id'], ['image_inspections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inspection_findings_id'), 'inspection_findings', ['id'], unique=False)

    op.add_column('ai_insights', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_ai_insights_id'), 'ai_insights', ['id'], unique=False)

    op.add_column('batches', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('batches', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('batches', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_batches_id'), 'batches', ['id'], unique=False)
    op.create_foreign_key('fk_batches_organization_id', 'batches', 'organizations', ['organization_id'], ['id'])

    op.add_column('environment_logs', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('environment_logs', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
    op.add_column('environment_logs', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_environment_logs_id'), 'environment_logs', ['id'], unique=False)
    op.create_foreign_key('fk_environment_logs_organization_id', 'environment_logs', 'organizations', ['organization_id'], ['id'])

    op.add_column('farms', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('farms', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_farms_id'), 'farms', ['id'], unique=False)
    op.create_foreign_key('fk_farms_organization_id', 'farms', 'organizations', ['organization_id'], ['id'])

    op.add_column('grow_bags', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
    op.add_column('grow_bags', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_grow_bags_id'), 'grow_bags', ['id'], unique=False)

    op.add_column('growth_logs', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('growth_logs', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_growth_logs_id'), 'growth_logs', ['id'], unique=False)
    op.create_foreign_key('fk_growth_logs_organization_id', 'growth_logs', 'organizations', ['organization_id'], ['id'])

    op.add_column('harvests', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('harvests', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
    op.add_column('harvests', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_harvests_id'), 'harvests', ['id'], unique=False)
    op.create_foreign_key('fk_harvests_organization_id', 'harvests', 'organizations', ['organization_id'], ['id'])

    op.add_column('recipe_versions', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_recipe_versions_id'), 'recipe_versions', ['id'], unique=False)

    op.add_column('recipes', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('recipes', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_recipes_id'), 'recipes', ['id'], unique=False)
    op.create_foreign_key('fk_recipes_organization_id', 'recipes', 'organizations', ['organization_id'], ['id'])

    op.add_column('rooms', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('rooms', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)
    op.create_foreign_key('fk_rooms_organization_id', 'rooms', 'organizations', ['organization_id'], ['id'])

    op.add_column('sensors', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
    op.add_column('sensors', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_sensors_id'), 'sensors', ['id'], unique=False)

    op.add_column('strains', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_strains_id'), 'strains', ['id'], unique=False)

    op.add_column('users', sa.Column('password_reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires', sa.DateTime(), nullable=True))
    op.create_index('ix_users_password_reset_token', 'users', ['password_reset_token'], unique=False)
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('current_organization_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('mfa_enabled', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('mfa_secret', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_foreign_key('fk_users_current_organization_id', 'users', 'organizations', ['current_organization_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_users_current_organization_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index('ix_users_password_reset_token', table_name='users')
    op.drop_column('users', 'mfa_secret')
    op.drop_column('users', 'mfa_enabled')
    op.drop_column('users', 'current_organization_id')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'password_reset_expires')
    op.drop_column('users', 'password_reset_token')
    op.drop_index(op.f('ix_strains_id'), table_name='strains')
    op.drop_column('strains', 'updated_at')
    op.drop_index(op.f('ix_sensors_id'), table_name='sensors')
    op.drop_column('sensors', 'updated_at')
    op.drop_column('sensors', 'created_at')
    op.drop_constraint('fk_rooms_organization_id', 'rooms', type_='foreignkey')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_column('rooms', 'updated_at')
    op.drop_column('rooms', 'organization_id')
    op.drop_constraint('fk_recipes_organization_id', 'recipes', type_='foreignkey')
    op.drop_index(op.f('ix_recipes_id'), table_name='recipes')
    op.drop_column('recipes', 'updated_at')
    op.drop_column('recipes', 'organization_id')
    op.drop_index(op.f('ix_recipe_versions_id'), table_name='recipe_versions')
    op.drop_column('recipe_versions', 'updated_at')
    op.drop_constraint('fk_harvests_organization_id', 'harvests', type_='foreignkey')
    op.drop_index(op.f('ix_harvests_id'), table_name='harvests')
    op.drop_column('harvests', 'updated_at')
    op.drop_column('harvests', 'created_at')
    op.drop_column('harvests', 'organization_id')
    op.drop_constraint('fk_growth_logs_organization_id', 'growth_logs', type_='foreignkey')
    op.drop_index(op.f('ix_growth_logs_id'), table_name='growth_logs')
    op.drop_column('growth_logs', 'updated_at')
    op.drop_column('growth_logs', 'organization_id')
    op.drop_index(op.f('ix_grow_bags_id'), table_name='grow_bags')
    op.drop_column('grow_bags', 'updated_at')
    op.drop_column('grow_bags', 'created_at')
    op.drop_constraint('fk_farms_organization_id', 'farms', type_='foreignkey')
    op.drop_index(op.f('ix_farms_id'), table_name='farms')
    op.drop_column('farms', 'updated_at')
    op.drop_column('farms', 'organization_id')
    op.drop_constraint('fk_environment_logs_organization_id', 'environment_logs', type_='foreignkey')
    op.drop_index(op.f('ix_environment_logs_id'), table_name='environment_logs')
    op.drop_column('environment_logs', 'updated_at')
    op.drop_column('environment_logs', 'created_at')
    op.drop_column('environment_logs', 'organization_id')
    op.drop_constraint('fk_batches_organization_id', 'batches', type_='foreignkey')
    op.drop_index(op.f('ix_batches_id'), table_name='batches')
    op.drop_column('batches', 'updated_at')
    op.drop_column('batches', 'deleted_at')
    op.drop_column('batches', 'organization_id')
    op.drop_index(op.f('ix_ai_insights_id'), table_name='ai_insights')
    op.drop_column('ai_insights', 'updated_at')
    op.drop_index(op.f('ix_inspection_findings_id'), table_name='inspection_findings')
    op.drop_table('inspection_findings')
    op.drop_index(op.f('ix_harvest_grades_id'), table_name='harvest_grades')
    op.drop_table('harvest_grades')
    op.drop_index(op.f('ix_yield_predictions_id'), table_name='yield_predictions')
    op.drop_table('yield_predictions')
    op.drop_index(op.f('ix_image_inspections_id'), table_name='image_inspections')
    op.drop_table('image_inspections')
    op.drop_index(op.f('ix_image_analyses_id'), table_name='image_analyses')
    op.drop_table('image_analyses')
    op.drop_index(op.f('ix_ai_conversations_id'), table_name='ai_conversations')
    op.drop_table('ai_conversations')
