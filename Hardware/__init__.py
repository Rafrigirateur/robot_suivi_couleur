from .camera import Camera

try:
    from .moteur import Moteur
except ImportError:
    print("Attention : Le module Moteur n'a pas pu être chargé (RPi.GPIO manquant).")