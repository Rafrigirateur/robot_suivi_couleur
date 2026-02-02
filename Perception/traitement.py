#Aplatir()
#DetectObstacle
#DetectCible
#binToObject()

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import cv2 as cv
from sklearn import linear_model

def Aplatir(image):
    imglinit = cv.imread(image)

    