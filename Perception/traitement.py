#Aplatir()
#DetectObstacle
#DetectCible
#binToObject()

import io
import numpy as np
import matplotlib
from Hardware.camera import Camera

matplotlib.use('agg')
import matplotlib.pyplot as plt
import cv2 as cv
#from sklearn import linear_model

def Aplatir(image):
    imglinit = cv.imread(image)


def DetectObstacle(image):
    hsv_img = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv_img, np.array(color_lower), np.array(color_upper))

    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel) # Supprime le bruit
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel) # Comble les trous

    return mask


def histogramme(image):
    filtered = cv.bilateralFilter(image, d=20, sigmaColor=19, sigmaSpace=19)
    hsv = cv.cvtColor(filtered, cv.COLOR_BGR2HSV_FULL)

    plt.figure()
    colors = ('r', 'g', 'b')
    labels = ('h', 's', 'v')

    for i, col in enumerate(colors):
        hist = cv.calcHist([hsv], [i], None, [256], [0, 256])
        plt.plot(hist, color=col, label=labels[i])
        plt.xlim([0, 256])

    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png') # Sauvegarde dans le buffer RAM
    buf.seek(0)
    
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    plt.close()

    res_img = cv.imdecode(img_arr, cv.IMREAD_COLOR)
    return res_img

if __name__ == "__main__":
    cam = Camera()
    frame = cam.get_frame()
    
    if frame is not None:
        cv.imshow('Frame', frame)
        
        # Appel de la nouvelle fonction qui renvoie l'image
        img_hist = histogramme(frame)
        
        # Affichage direct du résultat
        cv.imshow('Histogramme en direct', img_hist)
        
        cv.waitKey(0)
    
    cam.release()
    cv.destroyAllWindows()