import random
import shutil
import math
from pathlib import Path


# =========================
# CONFIGURATION
# =========================

DATASET_DIR = Path("dataset")

IMAGES_DIR = DATASET_DIR / "images"
LABELS_DIR = DATASET_DIR / "labels"

TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

SEED = 42


# =========================
# CHECK RATIOS
# =========================

if not math.isclose(TRAIN_RATIO + VAL_RATIO + TEST_RATIO, 1.0):
    raise ValueError(
        "Train, validation and test ratios must add up to 1."
    )


# =========================
# CREATE FOLDERS
# =========================

for split in ["train", "val", "test"]:
    (IMAGES_DIR / split).mkdir(parents=True, exist_ok=True)
    (LABELS_DIR / split).mkdir(parents=True, exist_ok=True)


# =========================
# GET ALL IMAGES
# =========================

image_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

images = [
    img for img in IMAGES_DIR.iterdir()
    if img.is_file()
    and img.suffix.lower() in image_extensions
]


print(f"Images found: {len(images)}")


# =========================
# MATCH IMAGE WITH JSON
# =========================

pairs = []
missing_labels = []

for image in images:

    json_file = LABELS_DIR / f"{image.stem}.json"

    if json_file.exists():
        pairs.append((image, json_file))

    else:
        missing_labels.append(image.name)


print(f"Valid image-label pairs: {len(pairs)}")
print(f"Missing labels: {len(missing_labels)}")


if missing_labels:
    print("\nMissing JSON files:")
    for file in missing_labels:
        print(file)


if len(pairs) == 0:
    raise Exception(
        "No matching image and label pairs found!"
    )


# =========================
# SHUFFLE DATA
# =========================

random.seed(SEED)
random.shuffle(pairs)


# =========================
# SPLIT DATA
# =========================

total = len(pairs)

train_count = int(total * TRAIN_RATIO)
val_count = int(total * VAL_RATIO)

train_data = pairs[:train_count]

val_data = pairs[
    train_count:
    train_count + val_count
]

test_data = pairs[
    train_count + val_count:
]


# =========================
# COPY FILES
# =========================

def copy_files(data, split):

    for image, label in data:

        shutil.copy2(
            image,
            IMAGES_DIR / split / image.name
        )

        shutil.copy2(
            label,
            LABELS_DIR / split / label.name
        )


copy_files(train_data, "train")
copy_files(val_data, "val")
copy_files(test_data, "test")


# =========================
# FINAL REPORT
# =========================

print("\nDataset split completed!")
print("------------------------------")
print(f"Train      : {len(train_data)}")
print(f"Validation : {len(val_data)}")
print(f"Test       : {len(test_data)}")
print(f"Total      : {total}")
print("------------------------------")