import time
import sys
import os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from Hardware import Moteur
from Controlle import MoteurControle

class Debug_Moteur:
    def __init__(self):
        self.moteur = Moteur(force=30)
        self.ctrl = MoteurControle(self.moteur)

    def test_debilosse(self):
        try:
            print("AVANCE")
            self.ctrl.avancer()
            time.sleep(2)

            print("STOP")
            self.ctrl.stop()
            time.sleep(1)

            print("RECULE")
            self.ctrl.reculer()
            time.sleep(2)

            print("STOP")
            self.ctrl.stop()
            time.sleep(1)

            print("GAUCHE")
            self.ctrl.gauche()
            time.sleep(1.5)

            print("DROITE")
            self.ctrl.droite()
            time.sleep(1.5)

            print("STOP FINAL")
            self.ctrl.stop()

        finally:
            self.moteur.cleanup()
            print("GPIO CLEANUP 👍")


if __name__ == "__main__":
    print("LANCEMENT TEST DEBUG")
    Debug_Moteur().test_debilosse()