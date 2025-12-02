"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2026-07-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Users
    op.create_table('users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'FARM_MANAGER', 'WORKER', name='userrole'), default='WORKER'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    # Farms
    op.create_table('farms',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('location', sa.String),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Rooms
    op.create_table('rooms',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('farm_id', sa.Integer, sa.ForeignKey('farms.id')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('capacity', sa.Integer),
        sa.Column('temperature_target', sa.Float),
        sa.Column('humidity_target', sa.Float),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Strains
    op.create_table('strains',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, unique=True, nullable=False),
        sa.Column('species', sa.String, nullable=False),
        sa.Column('supplier', sa.String),
        sa.Column('colonization_days', sa.Integer),
        sa.Column('fruiting_days', sa.Integer),
        sa.Column('difficulty', sa.String),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Recipes
    op.create_table('recipes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String),
        sa.Column('farm_id', sa.Integer, sa.ForeignKey('farms.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Recipe Versions
    op.create_table('recipe_versions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('recipe_id', sa.Integer, sa.ForeignKey('recipes.id')),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('ingredients', sa.JSON),
        sa.Column('hydration_percentage', sa.Float),
        sa.Column('spawn_ratio', sa.Float),
        sa.Column('notes', sa.String),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Batches
    op.create_table('batches',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('batch_number', sa.String, unique=True, nullable=False),
        sa.Column('farm_id', sa.Integer, sa.ForeignKey('farms.id')),
        sa.Column('room_id', sa.Integer, sa.ForeignKey('rooms.id')),
        sa.Column('strain_id', sa.Integer, sa.ForeignKey('strains.id')),
        sa.Column('recipe_version_id', sa.Integer, sa.ForeignKey('recipe_versions.id')),
        sa.Column('current_stage', sa.Enum('PREPARATION', 'INOCULATION', 'COLONIZATION', 'FRUITING', 'HARVEST', 'COMPLETED', name='batchstage')),
        sa.Column('start_date', sa.DateTime),
        sa.Column('status', sa.String, default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_batches_status_stage', 'batches', ['status', 'current_stage'])

    # Grow Bags
    op.create_table('grow_bags',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('batch_id', sa.Integer, sa.ForeignKey('batches.id')),
        sa.Column('barcode', sa.String, unique=True),
        sa.Column('status', sa.String, default='active'),
        sa.Column('weight', sa.Float),
    )

    # Growth Logs
    op.create_table('growth_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('batch_id', sa.Integer, sa.ForeignKey('batches.id')),
        sa.Column('stage', sa.String),
        sa.Column('notes', sa.String),
        sa.Column('image_url', sa.String),
        sa.Column('health_score', sa.Float),
        sa.Column('created_at', sa.DateTime),
    )
    op.create_index('ix_growth_logs_batch_created', 'growth_logs', ['batch_id', 'created_at'])

    # Environment Logs
    op.create_table('environment_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('room_id', sa.Integer, sa.ForeignKey('rooms.id')),
        sa.Column('temperature', sa.Float),
        sa.Column('humidity', sa.Float),
        sa.Column('co2', sa.Float),
        sa.Column('recorded_at', sa.DateTime),
    )
    op.create_index('ix_environment_room_time', 'environment_logs', ['room_id', 'recorded_at'])

    # Harvests
    op.create_table('harvests',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('batch_id', sa.Integer, sa.ForeignKey('batches.id')),
        sa.Column('quantity_kg', sa.Float),
        sa.Column('quality_score', sa.Float),
        sa.Column('harvest_date', sa.DateTime),
        sa.Column('selling_price', sa.Float),
    )

    # AI Insights
    op.create_table('ai_insights',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('batch_id', sa.Integer, sa.ForeignKey('batches.id')),
        sa.Column('type', sa.String),
        sa.Column('input_data', sa.JSON),
        sa.Column('recommendation', sa.String),
        sa.Column('confidence_score', sa.Float),
        sa.Column('created_at', sa.DateTime),
    )

    # Sensors
    op.create_table('sensors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('room_id', sa.Integer, sa.ForeignKey('rooms.id')),
        sa.Column('sensor_type', sa.String),
        sa.Column('device_id', sa.String),
        sa.Column('status', sa.String, default='active'),
        sa.Column('last_reading', sa.String),
    )


def downgrade() -> None:
    op.drop_table('sensors')
    op.drop_table('ai_insights')
    op.drop_table('harvests')
    op.drop_table('environment_logs')
    op.drop_table('growth_logs')
    op.drop_table('grow_bags')
    op.drop_table('batches')
    op.drop_table('recipe_versions')
    op.drop_table('recipes')
    op.drop_table('strains')
    op.drop_table('rooms')
    op.drop_table('farms')
    op.drop_table('users')