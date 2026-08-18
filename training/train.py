from ultralytics import YOLO


def main():

    model = YOLO("yolo11n.pt")

    model.train(
        data="training/data.yaml",
        epochs=50,
        imgsz=640,
        batch=16,
        name="face_detector",
        project="runs"
    )


if __name__ == "__main__":
    main()