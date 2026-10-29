from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import (
    Batch,
    Buyer,
    BuyerType,
    ExpenseCategory,
    Farm,
    FarmExpense,
    Harvest,
    HarvestSale,
    Organization,
    OrganizationMember,
    PaymentStatus,
    Recipe,
    RecipeVersion,
    Room,
    Strain,
    User,
)


def seed_demo_data(db: Session):
    # Admin User
    admin = User(
        name="Kamal Perera",
        email="admin@myco.farm",
        password_hash=get_password_hash("admin123"),
        role="ADMIN",
    )
    db.add(admin)
    db.flush()

    org = Organization(
        name="Bim Mal Mushroom Farm (Maharagama)",
        slug="bim-mal-mushroom-farm",
        owner_id=admin.id,
        created_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(org)
    db.flush()
    admin.current_organization_id = org.id
    db.add(
        OrganizationMember(
            organization_id=org.id,
            user_id=admin.id,
            role="OWNER",
            joined_at=datetime.utcnow(),
        )
    )

    # Farm
    farm = Farm(
        name="Bim Mal Oyster Farm Demo",
        location="Maharagama, Western Province, Sri Lanka",
        owner_id=admin.id,
        organization_id=org.id,
    )
    db.add(farm)
    db.flush()

    # Rooms
    room_col = Room(
        farm_id=farm.id,
        organization_id=org.id,
        name="Dark Incubation Shed A",
        capacity=2000,
        temperature_target=27.0,
        humidity_target=75.0,
    )
    room_fruit = Room(
        farm_id=farm.id,
        organization_id=org.id,
        name="Cropping House B",
        capacity=1500,
        temperature_target=25.0,
        humidity_target=88.0,
    )
    db.add_all([room_col, room_fruit])
    db.flush()

    # Sri Lankan DOA Varieties + Standard Strains
    strains = [
        Strain(
            name="American Oyster (Bhutani)",
            species="Pleurotus ostreatus",
            supplier="DOA Seed Center, Gannoruwa",
            colonization_days=18,
            fruiting_days=6,
            difficulty="Easy",
        ),
        Strain(
            name="Abalone Mushroom",
            species="Pleurotus cystidiosus",
            supplier="Ratmalana Spawn Lab",
            colonization_days=28,
            fruiting_days=8,
            difficulty="Medium",
        ),
        Strain(
            name="Pink Oyster",
            species="Pleurotus djamor",
            supplier="Local Spawn Lab",
            colonization_days=14,
            fruiting_days=5,
            difficulty="Easy",
        ),
        Strain(
            name="Milky Mushroom",
            species="Calocybe indica",
            supplier="DOA Makandura Center",
            colonization_days=22,
            fruiting_days=10,
            difficulty="Medium",
        ),
    ]
    db.add_all(strains)
    db.flush()

    # Recipe (Sri Lankan DOA Rubber Sawdust + Rice Bran Formula)
    recipe = Recipe(
        name="DOA Rubber Sawdust + Rice Bran Standard",
        description="100kg sawdust, 10kg rice bran, 2kg CaCO3, 200g MgSO4",
        farm_id=farm.id,
        organization_id=org.id,
    )
    db.add(recipe)
    db.flush()

    recipe_version = RecipeVersion(
        recipe_id=recipe.id,
        version=1,
        ingredients={"rubber_sawdust": 88, "rice_bran": 10, "caco3_lime": 2},
        hydration_percentage=62,
        spawn_ratio=5,
        notes="Standard Sri Lanka DOA formula for American Oyster & Abalone",
    )
    db.add(recipe_version)
    db.flush()

    # Demo Batch with Grow-Bag counts
    batch = Batch(
        batch_number="OY-2026-001",
        farm_id=farm.id,
        room_id=room_fruit.id,
        organization_id=org.id,
        strain_id=strains[0].id,
        recipe_version_id=recipe_version.id,
        current_stage="FRUITING",
        start_date=datetime(2026, 9, 15),
        bags_prepared=600,
        bags_inoculated=600,
        bags_contaminated=18,
        bags_harvested=582,
        status="active",
    )
    db.add(batch)
    db.flush()

    # Demo Harvest Flushes
    harvest_f1 = Harvest(
        batch_id=batch.id,
        organization_id=org.id,
        flush_number=1,
        quantity_kg=95.0,
        unsold_kg=2.0,
        spoiled_kg=1.5,
        quality_score=94.0,
        harvest_date=datetime(2026, 10, 5),
        selling_price=650.0,
        notes="First flush — strong pinheads",
    )
    db.add(harvest_f1)
    db.flush()

    # Demo Expenses in LKR
    db.add_all([
        FarmExpense(
            organization_id=org.id,
            batch_id=batch.id,
            category=ExpenseCategory.SUBSTRATE,
            description="Rubber sawdust & rice bran for 600 bags",
            amount_lkr=12500.0,
            expense_date=datetime(2026, 9, 14),
            recorded_by=admin.id,
        ),
        FarmExpense(
            organization_id=org.id,
            batch_id=batch.id,
            category=ExpenseCategory.SPAWN,
            description="30 bottles American Oyster grain spawn",
            amount_lkr=6000.0,
            expense_date=datetime(2026, 9, 15),
            recorded_by=admin.id,
        ),
        FarmExpense(
            organization_id=org.id,
            batch_id=batch.id,
            category=ExpenseCategory.LABOUR,
            description="Bagging, steaming & harvesting helper wages",
            amount_lkr=8500.0,
            expense_date=datetime(2026, 10, 5),
            recorded_by=admin.id,
        ),
    ])

    # Demo Buyer & Sale in LKR
    buyer = Buyer(
        organization_id=org.id,
        name="Keells Super — Maharagama",
        buyer_type=BuyerType.RETAILER,
        phone="011-2850123",
        location="Maharagama",
        notes="200g retail packs delivered every Monday & Thursday",
    )
    db.add(buyer)
    db.flush()

    db.add(
        HarvestSale(
            organization_id=org.id,
            buyer_id=buyer.id,
            batch_id=batch.id,
            harvest_id=harvest_f1.id,
            quantity_kg=80.0,
            price_per_kg_lkr=650.0,
            total_amount_lkr=52000.0,
            amount_paid_lkr=40000.0,
            balance_due_lkr=12000.0,
            payment_status=PaymentStatus.PARTIAL,
            sale_date=datetime(2026, 10, 5),
            notes="400 packs (200g) delivered",
            recorded_by=admin.id,
        )
    )

    db.commit()
    print("✅ Demo data seeded successfully for Oyster360 (Sri Lanka MVP)!")
