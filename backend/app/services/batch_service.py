from sqlalchemy.orm import Session
from app.models.batch import Batch, BatchStage
from app.core.tenant_enforcer import TenantEnforcer
from fastapi import HTTPException

VALID_TRANSITIONS = {
    BatchStage.PREPARATION: [BatchStage.INOCULATION],
    BatchStage.INOCULATION: [BatchStage.COLONIZATION],
    BatchStage.COLONIZATION: [BatchStage.FRUITING],
    BatchStage.FRUITING: [BatchStage.HARVEST],
    BatchStage.HARVEST: [BatchStage.COMPLETED],
}

def update_batch_stage(db: Session, batch_id: int, new_stage: str, organization_id: int):
    enforcer = TenantEnforcer(db, organization_id)
    batch = enforcer.safe_get(Batch, batch_id)
    
    current = BatchStage(batch.current_stage)
    target = BatchStage(new_stage)
    
    if target not in VALID_TRANSITIONS.get(current, []):
        raise ValueError(f"Invalid stage transition from {current} to {target}")
    
    batch.current_stage = new_stage
    db.commit()
    return batch

def create_batch(db: Session, batch_data: dict, organization_id: int) -> Batch:
    """Create batch with automatic organization assignment"""
    enforcer = TenantEnforcer(db, organization_id)
    return enforcer.safe_create(Batch, **batch_data)

def get_user_batches(db: Session, organization_id: int):
    """Get all batches for user's organization"""
    enforcer = TenantEnforcer(db, organization_id)
    return enforcer.get_all(Batch)