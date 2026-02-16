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


def DetectObstacle(image, color_lower, color_upper):
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



def contourDetection(img):
    
    # Conversion to grayscale 
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY) 

    # Blurr
    blur = cv.GaussianBlur(gray, (5,5), 0)
    
    # Find Canny edges 
    edged = cv.Canny(blur, 30, 200) 
    cv.imshow('Canny', edged) 

    # Finding Contours 
    contours, hierarchy = cv.findContours(edged, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) 
    #cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
    #cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
    print("Number of Contours found = " + str(len(contours))) 
    
    # Draw all contours (i.e -1)
    cv.drawContours(img, contours, -1, (0, 255, 0), 3) 
    
    cv.namedWindow('Contours', cv.WINDOW_NORMAL)  
    cv.imshow('Contours', img)

if __name__ == "__main__":
    cam = Camera()
    frame = cam.get_frame()
    
    if frame is not None:
        # 1. Affichage de l'image originale
        cv.imshow('Frame', frame)
        
        # 2. Test de l'Histogramme
        img_hist = histogramme(frame)
        cv.imshow('Histogramme en direct', img_hist)
        
        # ---------------------------------------------------------
        # 3. TEST DE DÉTECTION DE CONTOURS
        # ---------------------------------------------------------
        print("Lancement de la détection de contours...")
        # On passe une copie pour ne pas gribouiller sur l'image originale
        frame_contours = frame.copy()
        contourDetection(frame_contours) 
        
        # 4. TEST DE DETECT OBSTACLE
        lower_val = [5, 100, 0]
        upper_val = [25, 200, 255]
        mask_obstacle = DetectObstacle(frame, lower_val, upper_val)
        cv.imshow('Masque Obstacle', mask_obstacle)
        
        cv.waitKey(0)
    
    cam.release()
    cv.destroyAllWindows()