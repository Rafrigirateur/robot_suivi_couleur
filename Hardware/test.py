import cv2

cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
print("Opened:", cap.isOpened())

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Frame vide")
        break

    cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
