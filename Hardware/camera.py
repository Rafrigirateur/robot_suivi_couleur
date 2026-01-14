import cv2 as cv

class Camera:
    def __init__(self, camId=0,
                 width=640, 
                 height=480, 
                 fps=30) -> None:
        self.cap = cv.VideoCapture(camId)
        self.configure(width, height, fps)
    
    def configure(self, width=None, height=None, fps=None):
        if width is not None:
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        if fps is not None:
            self.cap.set(cv.CAP_PROP_FPS, fps)
    
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release()