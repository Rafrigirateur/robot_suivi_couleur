import RPi.GPIO as GPIO
import sys
import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from Hardware import moteur as Moteur

class MoteurControle:
    def __init__(self, moteur: Moteur):
        self.moteur = moteur

    def avancer(self):
        self.moteur._set_motors(
            GPIO.HIGH, GPIO.LOW,
            GPIO.HIGH, GPIO.LOW,
            self.moteur.force
        )

    def reculer(self):
        self.moteur._set_motors(
            GPIO.LOW, GPIO.HIGH,
            GPIO.LOW, GPIO.HIGH,
            self.moteur.force
        )

    def gauche(self):
        self.moteur._set_motors(
            GPIO.LOW, GPIO.HIGH,
            GPIO.HIGH, GPIO.LOW,
            self.moteur.force*0.75
        )

    def droite(self):
        self.moteur._set_motors(
            GPIO.HIGH, GPIO.LOW,
            GPIO.LOW, GPIO.HIGH,
            self.moteur.force*0.75
        )

    def stop(self):
        self.moteur.stop()
