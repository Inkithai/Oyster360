"""Professional Seed Data for MycoFarm AI Demo"""
from sqlalchemy.orm import Session
from app.models import (
    User, Farm, Room, Strain, Recipe, RecipeVersion, 
    Batch, GrowthLog, EnvironmentLog, Harvest
)
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random

def seed_demo_data(db: Session):
    print("🌱 Seeding MycoFarm AI Demo Data...")

    # 1. Admin User
    admin = User(
        name="Farm Admin",
        email="admin@myco.farm",
        password_hash=get_password_hash("admin123"),
        role="ADMIN"
    )
    db.add(admin)
    db.flush()

    # 2. Farm
    farm = Farm(
        name="Bim Mal Oyster Farm Demo",
        location="Sri Lanka",
        owner_id=admin.id
    )
    db.add(farm)
    db.flush()

    # 3. Rooms
    rooms = [
        Room(farm_id=farm.id, name="Colonization Room A", capacity=2000, temperature_target=24.0, humidity_target=85.0),
        Room(farm_id=farm.id, name="Fruiting Room A", capacity=1000, temperature_target=22.0, humidity_target=90.0),
        Room(farm_id=farm.id, name="Fruiting Room B", capacity=1000, temperature_target=22.5, humidity_target=88.0),
    ]
    db.add_all(rooms)
    db.flush()

    # 4. Strains
    strains = [
        Strain(name="Pearl Oyster", species="Pleurotus ostreatus", supplier="Local", colonization_days=18, fruiting_days=7, difficulty="Easy"),
        Strain(name="Pink Oyster", species="Pleurotus djamor", supplier="Local", colonization_days=16, fruiting_days=6, difficulty="Easy"),
        Strain(name="Blue Oyster", species="Pleurotus columbinus", supplier="Import", colonization_days=20, fruiting_days=8, difficulty="Medium"),
        Strain(name="King Oyster", species="Pleurotus eryngii", supplier="Import", colonization_days=22, fruiting_days=10, difficulty="Hard"),
    ]
    db.add_all(strains)
    db.flush()

    # 5. Recipe
    recipe = Recipe(name="High Yield Rice Straw Recipe V1", description="Optimized for Pearl Oyster", farm_id=farm.id)
    db.add(recipe)
    db.flush()

    recipe_version = RecipeVersion(
        recipe_id=recipe.id,
        version=1,
        ingredients=[{"name": "Rice Straw", "percentage": 70}, {"name": "Sawdust", "percentage": 20}, {"name": "Wheat Bran", "percentage": 10}],
        hydration_percentage=65,
        spawn_ratio=5,
        notes="Standard high-yield recipe"
    )
    db.add(recipe_version)
    db.flush()

    # 6. Batches
    batches = [
        Batch(
            batch_number="OY-2026-001",
            farm_id=farm.id,
            room_id=rooms[1].id,
            strain_id=strains[0].id,
            recipe_version_id=recipe_version.id,
            current_stage="COMPLETED",
            start_date=datetime(2026, 5, 10),
            status="completed"
        ),
        Batch(
            batch_number="OY-2026-002",
            farm_id=farm.id,
            room_id=rooms[1].id,
            strain_id=strains[0].id,
            recipe_version_id=recipe_version.id,
            current_stage="FRUITING",
            start_date=datetime(2026, 6, 20),
            status="active"
        ),
        Batch(
            batch_number="OY-2026-003",
            farm_id=farm.id,
            room_id=rooms[0].id,
            strain_id=strains[1].id,
            recipe_version_id=recipe_version.id,
            current_stage="COLONIZATION",
            start_date=datetime(2026, 7, 1),
            status="active"
        ),
    ]
    db.add_all(batches)
    db.flush()

    # 7. Harvest for completed batch
    harvest = Harvest(
        batch_id=batches[0].id,
        quantity_kg=120,
        quality_score=92,
        harvest_date=datetime(2026, 6, 15),
        selling_price=800
    )
    db.add(harvest)

    # 8. Growth Logs for active batch
    for i in range(25):
        log_date = batches[1].start_date + timedelta(days=i)
        stage = "COLONIZATION" if i < 18 else "FRUITING"
        health = random.randint(85, 98)
        
        log = GrowthLog(
            batch_id=batches[1].id,
            stage=stage,
            notes=f"Day {i+1} observation",
            health_score=health,
            created_at=log_date
        )
        db.add(log)

    # 9. Environment Logs (30 days)
    for i in range(30):
        date = datetime(2026, 6, 1) + timedelta(days=i)
        for room in rooms:
            log = EnvironmentLog(
                room_id=room.id,
                temperature=round(random.uniform(22, 25), 1),
                humidity=round(random.uniform(85, 95), 1),
                co2=random.randint(800, 1500),
                recorded_at=date
            )
            db.add(log)

    db.commit()
    print("✅ Demo data seeded successfully!")
    print("   - Farm: Bim Mal Oyster Farm Demo")
    print("   - 3 Rooms, 4 Strains, 1 Recipe")
    print("   - 3 Batches (1 completed, 2 active)")
    print("   - 30 days of environment data")