import csv
import json
import re
from collections import Counter
from pathlib import Path

source = Path("data/raw/taco/TACO/data/annotations.json")
output = Path("data/manifests/taco_master_taxonomy.csv")

with source.open(encoding="utf-8") as f:
    dataset = json.load(f)

counts = Counter(a["category_id"] for a in dataset["annotations"])

# These are provisional visual-material mappings, not verified composition.
material_groups = {
    "plastic": [
        "Clear plastic bottle", "Other plastic bottle", "Other plastic",
        "Plastic film", "Other plastic wrapper", "Plastic bottle cap",
        "Plastic straw", "Disposable plastic cup", "Other plastic cup",
        "Plastic lid", "Spread tub", "Other plastic container",
        "Squeezable tube", "Garbage bag", "Single-use carrier bag",
        "Polypropylene bag", "Tupperware", "Plastic utensils",
        "Plastic glooves", "Six pack rings",
    ],
    "paper": [
        "Normal paper", "Magazine paper", "Wrapping paper",
        "Tissues", "Paper bag", "Paper straw",
    ],
    "cardboard": [
        "Corrugated carton", "Egg carton", "Pizza box", "Toilet tube",
    ],
    "metal": [
        "Drink can", "Food Can", "Scrap metal", "Metal bottle cap",
        "Metal lid", "Pop tab", "Aluminium foil",
    ],
    "glass": [
        "Glass bottle", "Broken glass", "Glass cup", "Glass jar",
    ],
    "organic": ["Food waste"],
}

# Packaging and other materials that should not be guessed from appearance.
composite_or_uncertain = {
    "Other carton", "Drink carton", "Meal carton",
    "Foam food container", "Foam cup", "Styrofoam piece",
    "Aluminium blister pack", "Carded blister pack",
    "Plasticified paper bag", "Aerosol", "Battery",
    "Cigarette", "Unlabeled litter", "Shoe",
    "Rope & strings", "Spread tub", "Squeezable tube",
    "Garbage bag", "Plastic glooves", "Six pack rings",
}

special_handling = {
    "Battery": "BATTERY_SPECIAL_HANDLING",
    "Aerosol": "HAZARD_REVIEW",
    "Broken glass": "SHARP_OBJECT_REVIEW",
    "Cigarette": "FIRE_AND_RESIDUE_REVIEW",
    "Unlabeled litter": "UNKNOWN_IDENTITY",
}

def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

rows = []

for category in dataset["categories"]:
    cid = category["id"]
    name = category["name"]
    count = counts[cid]

    material = next(
        (group for group, names in material_groups.items()
         if name in names),
        "unknown_or_composite"
    )

    if name in composite_or_uncertain:
        material = "unknown_or_composite"

    hazard = special_handling.get(name, "STANDARD_REVIEW")

    if name == "Unlabeled litter":
        readiness = "IDENTITY_UNKNOWN"
        notes = "Preserve source annotation; do not assign a guessed identity."
    elif name == "Battery":
        readiness = "SUPPLEMENT_REQUIRED"
        notes = "Only two annotations in this TACO report; obtain more data."
    elif count < 30:
        readiness = "LOW_DATA_RETAIN"
        notes = "Preserve category; gather more examples before dedicated training."
    elif material == "unknown_or_composite":
        readiness = "MATERIAL_REVIEW"
        notes = "Identity retained; material needs verification."
    else:
        readiness = "CANDIDATE_REVIEW"
        notes = "Candidate category; inspect samples and annotation quality."

    rows.append({
        "category_id": cid,
        "source_category": name,
        "object_identity": slug(name),
        "proposed_material": material,
        "hazard_or_handling_flag": hazard,
        "annotation_count": count,
        "training_readiness": readiness,
        "notes": notes,
    })

output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda r: r["category_id"]))

print(f"Saved: {output}")
print(f"Categories preserved: {len(rows)}")
print(f"Annotations counted: {sum(counts.values())}")
print(f"Categories needing more data: {sum(r['training_readiness'] == 'LOW_DATA_RETAIN' for r in rows)}")
print("No source annotations or images were modified.")
