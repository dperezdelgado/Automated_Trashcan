import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "data" / "manifests"
INVENTORY = MANIFESTS / "trashnet_inventory.csv"
CONFLICTS = MANIFESTS / "trashnet_duplicate_conflicts.csv"
OUTPUT = MANIFESTS / "trashnet_split.csv"
SEED = 42

for path in (INVENTORY, CONFLICTS):
    if not path.exists():
        raise FileNotFoundError(f"Required file missing: {path}")

with INVENTORY.open(newline="", encoding="utf-8-sig") as f:
    inventory = list(csv.DictReader(f))

with CONFLICTS.open(newline="", encoding="utf-8-sig") as f:
    conflicts = list(csv.DictReader(f))

excluded = {row["RelativePath"] for row in conflicts}
if len(excluded) != 6:
    raise ValueError(f"Expected 6 flagged files, found {len(excluded)}")

by_class = defaultdict(list)
for row in inventory:
    if row["RelativePath"] not in excluded:
        by_class[row["Class"]].append(row)

rng = random.Random(SEED)
output_rows = []

for class_name in sorted(by_class):
    rows = sorted(by_class[class_name], key=lambda r: r["RelativePath"])
    rng.shuffle(rows)

    n = len(rows)
    n_train = round(n * 0.70)
    n_val = round(n * 0.15)

    for index, row in enumerate(rows):
        if index < n_train:
            split = "train"
        elif index < n_train + n_val:
            split = "val"
        else:
            split = "test"

        output_rows.append({
            "Class": row["Class"],
            "RelativePath": row["RelativePath"],
            "SHA256": row["SHA256"],
            "Split": split,
            "Seed": SEED,
        })

output_rows.sort(key=lambda r: (r["Class"], r["Split"], r["RelativePath"]))

with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f, fieldnames=["Class", "RelativePath", "SHA256", "Split", "Seed"]
    )
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Inventory rows: {len(inventory)}")
print(f"Excluded conflict files: {len(excluded)}")
print(f"Included images: {len(output_rows)}")
print(f"Split totals: {dict(Counter(r['Split'] for r in output_rows))}")
print("Class counts:")
for name in sorted(by_class):
    counts = Counter(r["Split"] for r in output_rows if r["Class"] == name)
    print(f"  {name}: {dict(counts)}")
print(f"Manifest: {OUTPUT.relative_to(ROOT)}")
