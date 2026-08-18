from ultralytics import YOLO
import cv2


model = YOLO("model/best.pt")


cap = cv2.VideoCapture(1)


if not cap.isOpened():
    print("Camera not detected")
    exit()


print("Camera started")


while True:

    ret, frame = cap.read()

    if not ret:
        break


    results = model.predict(
        frame,
        conf=0.25,
        verbose=False
    )


    annotated = results[0].plot()


    cv2.imshow(
        "Face Detection",
        annotated
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()