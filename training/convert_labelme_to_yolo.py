import json
from pathlib import Path
from PIL import Image


# ==========================
# CONFIG
# ==========================

DATASET = Path("dataset")

LABEL_DIRS = [
    DATASET / "labels/train",
    DATASET / "labels/val",
    DATASET / "labels/test"
]


CLASS_MAP = {
    "face": 0
}


# ==========================
# CONVERT FUNCTION
# ==========================

def convert_json(json_file):

    with open(json_file, "r") as file:
        data = json.load(file)


    image_path = (
        json_file.parent.parent.parent
        / "images"
        / json_file.parent.name
        / data["imagePath"].split("\\")[-1]
    )


    if not image_path.exists():
        print(
            f"Image missing: {image_path}"
        )
        return


    img = Image.open(image_path)

    img_width, img_height = img.size


    yolo_lines = []


    for shape in data["shapes"]:

        label = shape["label"]

        if label not in CLASS_MAP:
            continue


        class_id = CLASS_MAP[label]


        points = shape["points"]

        x1 = points[0][0]
        y1 = points[0][1]

        x2 = points[1][0]
        y2 = points[1][1]


        box_width = x2 - x1
        box_height = y2 - y1


        x_center = x1 + box_width / 2
        y_center = y1 + box_height / 2


        # Normalize

        x_center /= img_width
        y_center /= img_height

        box_width /= img_width
        box_height /= img_height


        yolo_lines.append(
            f"{class_id} "
            f"{x_center:.6f} "
            f"{y_center:.6f} "
            f"{box_width:.6f} "
            f"{box_height:.6f}"
        )


    txt_file = json_file.with_suffix(".txt")


    with open(txt_file, "w") as file:
        file.write(
            "\n".join(yolo_lines)
        )


# ==========================
# RUN
# ==========================

total = 0


for folder in LABEL_DIRS:

    json_files = list(
        folder.glob("*.json")
    )

    print(
        f"\nProcessing {folder}"
    )

    for json_file in json_files:

        convert_json(json_file)

        total += 1


print("\nConversion completed!")
print(
    f"Files converted: {total}"
)