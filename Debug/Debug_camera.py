import cv2 as cv
from Hardware.camera import Camera

cap = cv.VideoCapture(0)

while (True):
    ret, frame = cap.read()
    cv.imshow('Video', frame)    
    
    if cv.waitKey(1) == 27:
        break    
 
cap.release()
cv.destroyAllWindows()

