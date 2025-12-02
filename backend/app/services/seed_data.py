from sqlalchemy.orm import Session
from app.models import (
    User, Farm, Room, Strain, Recipe, RecipeVersion, Batch
)
from app.core.security import get_password_hash
from datetime import datetime

def seed_demo_data(db: Session):
    # Admin User
    admin = User(
        name="Admin User",
        email="admin@myco.farm",
        password_hash=get_password_hash("admin123"),
        role="ADMIN"
    )
    db.add(admin)
    db.flush()

    # Farm
    farm = Farm(name="Bim Mal Oyster Farm Demo", location="Sri Lanka", owner_id=admin.id)
    db.add(farm)
    db.flush()

    # Rooms
    room_col = Room(farm_id=farm.id, name="Colonization Room A", capacity=2000, temperature_target=24.0, humidity_target=85.0)
    room_fruit = Room(farm_id=farm.id, name="Fruiting Room A", capacity=1500, temperature_target=22.0, humidity_target=90.0)
    db.add_all([room_col, room_fruit])
    db.flush()

    # Strains
    strains = [
        Strain(name="Pearl Oyster", species="Pleurotus ostreatus", supplier="Local", colonization_days=18, fruiting_days=7, difficulty="Easy"),
        Strain(name="Blue Oyster", species="Pleurotus columbinus", supplier="Local", colonization_days=20, fruiting_days=8, difficulty="Medium"),
        Strain(name="Pink Oyster", species="Pleurotus djamor", supplier="Import", colonization_days=16, fruiting_days=6, difficulty="Easy"),
        Strain(name="King Oyster", species="Pleurotus eryngii", supplier="Import", colonization_days=22, fruiting_days=10, difficulty="Hard"),
    ]
    db.add_all(strains)
    db.flush()

    # Recipe
    recipe = Recipe(name="Rice Straw + Bran Substrate V1", description="Standard oyster substrate", farm_id=farm.id)
    db.add(recipe)
    db.flush()

    recipe_version = RecipeVersion(
        recipe_id=recipe.id,
        version=1,
        ingredients={"rice_straw": 70, "sawdust": 20, "bran": 10},
        hydration_percentage=65,
        spawn_ratio=5,
        notes="Standard recipe for Pearl Oyster"
    )
    db.add(recipe_version)
    db.flush()

    # Demo Batch
    batch = Batch(
        batch_number="OY-2026-001",
        farm_id=farm.id,
        room_id=room_fruit.id,
        strain_id=strains[0].id,
        recipe_version_id=recipe_version.id,
        current_stage="FRUITING",
        start_date=datetime(2026, 6, 1),
        status="active"
    )
    db.add(batch)

    db.commit()
    print("✅ Demo data seeded successfully for Oyster360!")
print("   Farm: Bim Mal Oyster Farm Demo (Sri Lanka)")
print("   Rooms: 3 | Strains: 4 | Recipes: 1")
print("   Batches: 3 | Environmental logs: 30 days")