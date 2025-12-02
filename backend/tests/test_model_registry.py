"""
Test SQLAlchemy Model Registry Configuration
"""
import pytest
from sqlalchemy.orm import configure_mappers
from sqlalchemy.exc import InvalidRequestError

def test_model_registry_configuration():
    """
    Verify that all models can be configured without registry errors.
    This catches issues like:
    - Missing imports
    - Circular relationship problems
    - Duplicate model definitions
    """
    try:
        # This will trigger mapper configuration for all models
        configure_mappers()
        print("✅ All models configured successfully")
        assert True
    except InvalidRequestError as e:
        pytest.fail(f"Model registry configuration failed: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error during model configuration: {e}")

def test_all_models_importable():
    """Verify all models can be imported"""
    from app.models import (
        User, Organization, OrganizationMember, Farm, Room, Strain,
        Recipe, RecipeVersion, Batch, GrowBag, EnvironmentLog, 
        GrowthLog, Harvest, InventoryItem, InventoryTransaction,
        Supplier, PurchaseOrder, PurchaseOrderItem, Subscription,
        Notification, ImageInspection, InspectionFinding, YieldPrediction,
        KnowledgeDocument, DocumentChunk, AuditLog, FeatureFlag,
        Conversation, Message
    )
    print("✅ All models imported successfully")
    assert True

if __name__ == "__main__":
    test_model_registry_configuration()
    test_all_models_importable()