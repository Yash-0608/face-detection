from ultralytics import YOLO
import cv2
from pathlib import Path


MODEL_PATH = Path("model/best.pt")


model = YOLO(MODEL_PATH)



def detect_faces(image_path, output_path):

    image_path = Path(image_path)
    output_path = Path(output_path)


    print("Input:", image_path)
    print("Output:", output_path)


    results = model.predict(
        source=str(image_path),
        conf=0.6,
        verbose=False
    )


    result = results[0]


    # Draw boxes
    output_image = result.plot()


    # Save image
    saved = cv2.imwrite(
        str(output_path),
        output_image
    )


    if saved:
        print("Result saved:", output_path)

    else:
        print("FAILED TO SAVE RESULT")


    return output_path