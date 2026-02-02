'''
Ce script calcule les paramètres d'étalonnage d'une caméra à partir des photos de dammiers
disponibles dans le répertoire "repertoire_image/*.jpg"

Ensuite, il calcule la matrice permettant la mise à plat du damier "vue_au_sol.jpg" (warping).

Les différentes variables nécessaires au warping (remise à plat pour la vue oiseau) sont disponibles dans le fichier 
"parametres_calibration_robot.npy".
'''

import numpy as np
import glob
import cv2 as cv

# PARAMETRES DAMIER (nombre de coins intérieurs verticaux et horizontaux)
COINS_X = 9
COINS_Y = 6

# critere d'arret de la recherche
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# print(criteria)
# points de damier image réguliers sur lesquels recaller
objp = np.zeros((COINS_Y * COINS_X, 3), np.float32)

objp[:, :2] = np.mgrid[0:COINS_X, 0:COINS_Y].T.reshape(-1, 2)
# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
images = glob.glob("img/*.png")


# Lecture des images et détections de coins.
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Detections des points saillants
    ret, corners = cv.findChessboardCorners(gray, (COINS_X, COINS_Y), None)
    # Si on en trouve on les met dans une liste
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        # Affichage des points trouves pour verification
        cv.drawChessboardCorners(img, (COINS_X, COINS_Y), corners2, ret)
        cv.imshow("img", img)
        cv.waitKey(0)
    else: print("pas trouver")
cv.destroyAllWindows()


ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

# Lescture d'une image de damier à recaller
img = cv.imread("vueRobot.png")

def corners_unwarp(img, nx, ny, mtx, dist):
    # suppression de distorsion
    undistorted = cv.undistort(img, mtx, dist, None, mtx)
    # conversion en niveaux de gris
    gray = cv.cvtColor(undistorted, cv.COLOR_BGR2GRAY)
    #  détection des points
    ret, corners = cv.findChessboardCorners(gray, (nx, ny), None)
    # si on trouve des points
    if ret == True:
        offset = 50  # offset for dst points
        img_size = (undistorted.shape[1], undistorted.shape[0])
        # affichage des points
        cv.drawChessboardCorners(undistorted, (COINS_X, COINS_Y), corners, ret)
        # définition des coins de l echiquier
        src = np.float32([corners[0], corners[nx - 1], corners[-1], corners[-nx]])
        
        # Définition des coins de l'échiquier sur l'image finale. 
        dst = np.float32(
            [
                [ offset, img_size[1]*0.8 ],
                [ img_size[0]-offset,img_size[1]*0.8],
                [ img_size[0]-offset,img_size[1]-offset],
                [offset, img_size[1]-offset ],
            ]
        )
        
        # Calcul de matrice de transformation
        M = cv.getPerspectiveTransform(src, dst)
        # test de la viewbird sur l'échiquier
        warped = cv.warpPerspective(undistorted, M, img_size, flags=cv.INTER_LINEAR)
        print("etalonnage OK")
    return warped, M

top_down, perspective_M = corners_unwarp(img, COINS_X, COINS_Y, mtx, dist)

cv.imshow("img", top_down)
cv.waitKey(0)
with open('parametres_calibration_robot.npy', 'wb') as f:
    np.save(f, perspective_M)
    np.save(f, mtx)
    np.save(f, dist)

