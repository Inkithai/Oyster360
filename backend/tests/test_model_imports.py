"""
Test that all models can be imported without registry errors
"""
def test_all_models_import():
    """Verify all models can be imported"""
    from app.models.base import Base
    from app.models.user import User
    from app.models.organization import Organization, OrganizationMember
    from app.models.batch import Batch
    from app.models.grow_bag import GrowBag
    from app.models.recipe import Recipe, RecipeVersion
    from app.models.room import Room
    from app.models.strain import Strain
    from app.models.harvest import Harvest
    from app.models.environment_log import EnvironmentLog
    from app.models.growth_log import GrowthLog
    from app.models.inventory import InventoryItem, InventoryTransaction
    from app.models.purchase import Supplier, PurchaseOrder, PurchaseOrderItem
    from app.models.subscription import Subscription
    
    # If we reach here without errors, all models are valid
    assert True
    print("✅ All models imported successfully without registry errors")

if __name__ == "__main__":
    test_all_models_import()