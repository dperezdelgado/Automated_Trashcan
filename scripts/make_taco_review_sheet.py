import json
from pathlib import Path
from collections import defaultdict
from PIL import Image, ImageDraw

root = Path("data/raw/taco/TACO/data")
annotation_file = root / "annotations.json"
output = Path("results/taco_category_review.jpg")

with annotation_file.open(encoding="utf-8") as f:
    data = json.load(f)

categories = {c["id"]: c["name"] for c in data["categories"]}
images = {im["id"]: im for im in data["images"]}
annotations = defaultdict(list)

for ann in data["annotations"]:
    annotations[ann["category_id"]].append(ann)

# One representative image per category, prioritizing categories
# that have not yet been visually reviewed.
tile_w, tile_h = 220, 180
cols = 6
rows = (len(categories) + cols - 1) // cols

sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), "white")
draw = ImageDraw.Draw(sheet)

for index, (cat_id, name) in enumerate(
    sorted(categories.items(), key=lambda item: item[0])
):
    x = (index % cols) * tile_w
    y = (index // cols) * tile_h

    matching = annotations.get(cat_id, [])
    draw.text((x + 5, y + 4), f"ID {cat_id}: {name[:27]}", fill="black")
    draw.text((x + 5, y + 20), f"Annotations: {len(matching)}", fill="black")

    if not matching:
        draw.text((x + 5, y + 55), "No annotated examples", fill="red")
        continue

    # Select a representative annotated image.
    ann = matching[0]
    image_info = images[ann["image_id"]]
    image_path = root / image_info["file_name"]

    try:
        with Image.open(image_path) as original:
            im = original.convert("RGB")
    except Exception as exc:
        draw.text((x + 5, y + 55), f"Image error: {exc}", fill="red")
        continue

    im.thumbnail((tile_w - 12, tile_h - 48))
    px = x + (tile_w - im.width) // 2
    py = y + 42
    sheet.paste(im, (px, py))

    # Draw the selected category's bounding box.
    sx = im.width / image_info["width"]
    sy = im.height / image_info["height"]
    bx, by, bw, bh = ann["bbox"]

    box = (
        px + bx * sx,
        py + by * sy,
        px + (bx + bw) * sx,
        py + (by + bh) * sy,
    )
    draw.rectangle(box, outline="red", width=2)

output.parent.mkdir(parents=True, exist_ok=True)
sheet.save(output, quality=90)

print(f"Saved visual review sheet: {output}")
print(f"Categories reviewed: {len(categories)}")
