from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.strain import Strain

router = APIRouter()

SRI_LANKA_DOA_VARIETIES: List[Dict[str, Any]] = [
    {
        "name": "American Oyster (Bhutani)",
        "local_name_si": "ඇමරිකන් ඔයිස්ටර් (භූතානි)",
        "local_name_ta": "அமெரிக்கன் சிப்பி காளான்",
        "species": "Pleurotus ostreatus",
        "colonization_days": 18,
        "fruiting_days": 6,
        "expected_flushes": 3,
        "expected_yield_g_per_bag": 350,
        "optimal_temp_c": "24–28°C",
        "optimal_humidity_pct": "85–90%",
        "difficulty": "Easy",
        "doa_notes": (
            "Most widely cultivated commercial variety in Sri Lanka. High yield on "
            "rubber/mango sawdust with rice bran, MgSO4, CaCO3, and soy flour."
        ),
    },
    {
        "name": "Abalone Mushroom",
        "local_name_si": "ඇබලෝනි බිම්මල්",
        "local_name_ta": "அபலோன் காளான்",
        "species": "Pleurotus cystidiosus",
        "colonization_days": 28,
        "fruiting_days": 8,
        "expected_flushes": 3,
        "expected_yield_g_per_bag": 300,
        "optimal_temp_c": "26–30°C",
        "optimal_humidity_pct": "85–92%",
        "difficulty": "Medium",
        "doa_notes": (
            "Thick, fleshy caps with longer shelf life for transport to supermarkets "
            "and hotels; requires casing/scraping after colonization."
        ),
    },
    {
        "name": "Pink Oyster",
        "local_name_si": "රෝස ඔයිස්ටර්",
        "local_name_ta": "இளஞ்சிவப்பு சிப்பி காளான்",
        "species": "Pleurotus djamor",
        "colonization_days": 14,
        "fruiting_days": 5,
        "expected_flushes": 2,
        "expected_yield_g_per_bag": 280,
        "optimal_temp_c": "26–32°C",
        "optimal_humidity_pct": "85–90%",
        "difficulty": "Easy",
        "doa_notes": (
            "Fast-colonizing warm-climate variety suited for low-country zones; "
            "short shelf life so best sold same-day to local buyers."
        ),
    },
    {
        "name": "Milky Mushroom",
        "local_name_si": "කිරි බිම්මල් (මිල්කි)",
        "local_name_ta": "பால் காளான்",
        "species": "Calocybe indica",
        "colonization_days": 22,
        "fruiting_days": 10,
        "expected_flushes": 3,
        "expected_yield_g_per_bag": 400,
        "optimal_temp_c": "28–34°C",
        "optimal_humidity_pct": "85–90%",
        "difficulty": "Medium",
        "doa_notes": (
            "Thrives in warmer dry-zone and low-country climates; requires soil/sand "
            "casing layer and diffused light during fruiting."
        ),
    },
]

DOA_STAGE_CHECKLISTS: List[Dict[str, Any]] = [
    {
        "stage": "PREPARATION",
        "title": "Substrate Mixing & Bagging (DOA Standard)",
        "checklist": [
            "Sieve rubber or mango sawdust to remove splinters that puncture polypropylene bags.",
            "Mix 100 kg sawdust + 10 kg rice bran + 2 kg CaCO3 (lime) + 200 g MgSO4 with water to 60–65% moisture (squeeze test: no water drips).",
            "Fill 7x14 inch polypropylene bags firmly (approx. 800g–1kg wet weight) and fit PVC neck rings with cotton plugs.",
            "Steam sterilize in barrel steamer at 100°C for 3–4 hours continuously.",
        ],
    },
    {
        "stage": "INOCULATION",
        "title": "Cooling & Spawn Inoculation",
        "checklist": [
            "Cool sterilized grow bags completely (<28°C) in a clean, draft-free inoculation room.",
            "Disinfect hands and work surface with 70% surgical spirit before opening spawn bottles.",
            "Add 1–2 tablespoons of certified grain/paddy spawn per bag and re-plug tightly with clean cotton.",
        ],
    },
    {
        "stage": "COLONIZATION",
        "title": "Dark Room Mycelium Incubation (18–28 Days)",
        "checklist": [
            "Store bags upright in a clean, dark incubation rack at 25–28°C.",
            "Inspect every 3 days for green mold (Trichoderma) or black mold; immediately remove contaminated bags from the shed.",
            "Wait until white mycelium completely colonizes the bottom of the bag before opening.",
        ],
    },
    {
        "stage": "FRUITING",
        "title": "Bag Opening & Cropping House Management",
        "checklist": [
            "Move fully white bags to the cropping house, remove cotton plug & ring, and open or slit bag mouth.",
            "Mist clean water 2–3 times daily onto floor/walls and fine mist around bags to maintain 85–90% humidity.",
            "Ensure cross-ventilation (low CO2) and indirect natural light so caps form properly without long stems.",
        ],
    },
    {
        "stage": "HARVEST",
        "title": "Flush Harvesting, Grading & Next Flush",
        "checklist": [
            "Harvest mushrooms in the early morning before cap edges curl upwards or release spores.",
            "Twist and pull the entire cluster cleanly from the bag mouth so rotting stem bases do not attract flies.",
            "Weigh harvest immediately, pack in ventilated 200g/500g/1kg packs, and scrape dried mycelium lightly for the next flush (7–10 days later).",
        ],
    },
]


@router.get("/", response_model=List[dict])
def get_strains(db: Session = Depends(get_db)):
    strains = db.query(Strain).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "species": s.species,
            "supplier": s.supplier,
            "difficulty": s.difficulty,
            "colonization_days": s.colonization_days,
            "fruiting_days": s.fruiting_days,
        }
        for s in strains
    ]


@router.get("/doa-varieties", response_model=List[Dict[str, Any]])
def get_doa_varieties():
    """Return Department of Agriculture (Sri Lanka) recommended mushroom varieties."""
    return SRI_LANKA_DOA_VARIETIES


@router.get("/cultivation-guide", response_model=Dict[str, Any])
def get_cultivation_guide():
    """Return rule-based Sri Lanka DOA cultivation checklists and variety guidelines."""
    return {
        "source": "Department of Agriculture (DOA) Sri Lanka — Mushroom Cultivation Guide",
        "varieties": SRI_LANKA_DOA_VARIETIES,
        "stage_checklists": DOA_STAGE_CHECKLISTS,
    }
