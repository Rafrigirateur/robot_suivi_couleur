import RPi.GPIO as GPIO
import time

malus_gauche = 0    #De 0 à 100, on fait vitesse * (1 - malus/100) pour compenser les différences de moteurs
malus_droite = 0
class Moteur:
    def __init__(self, 
                  ain1=17, ain2=27, 
                  bin1=24, bin2=23, 
                  stby=22, # Correspond à NSLEEP
                  force=20,
                  temps360=3.2):
        
        # Pins (Mis à jour selon mouvement2.py)
        self.AIN1 = ain1
        self.AIN2 = ain2
        self.BIN1 = bin1
        self.BIN2 = bin2
        self.STBY = stby # NSLEEP
        
        # Parametres
        self.force = force
        self.temps360 = temps360
        
        # Init GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup([self.AIN1, self.AIN2, self.BIN1, self.BIN2, self.STBY], GPIO.OUT)
        
        # Initialisation des PWM sur les 4 broches de direction
        self.pwm_ain1 = GPIO.PWM(self.AIN1, 2000)
        self.pwm_ain2 = GPIO.PWM(self.AIN2, 2000)
        self.pwm_bin1 = GPIO.PWM(self.BIN1, 2000)
        self.pwm_bin2 = GPIO.PWM(self.BIN2, 2000)
        
        self.pwm_ain1.start(0)
        self.pwm_ain2.start(0)
        self.pwm_bin1.start(0)
        self.pwm_bin2.start(0)
        
        # Activer le driver (NSLEEP à HIGH)
        GPIO.output(self.STBY, GPIO.HIGH)

    # Controlleur bas niveau adapté à la nouvelle logique
    def _set_motors(self, a1, a2, b1, b2, duty):
        """
        Pour chaque moteur, si l'entrée est HIGH, on applique le PWM (duty).
        Si l'entrée est LOW, on met le rapport cyclique à 0.
        """
        self.pwm_ain1.ChangeDutyCycle(duty if a1 == GPIO.HIGH else 0)
        self.pwm_ain2.ChangeDutyCycle(duty if a2 == GPIO.HIGH else 0)
        self.pwm_bin1.ChangeDutyCycle(duty if b1 == GPIO.HIGH else 0)
        self.pwm_bin2.ChangeDutyCycle(duty if b2 == GPIO.HIGH else 0)
    
    def piloter(self, gauche, droite):
        """
        Contrôle les moteurs avec des valeurs de -100 à 100.
        gauche: vitesse du moteur A
        droite: vitesse du moteur B
        """
        # --- Moteur Gauche (A) ---
        vitesse_a = max(min(gauche, 100), -100) * (1 - malus_gauche/100) # On borne entre -100 et 100

        if vitesse_a > 0:
            # Avancer : AIN1 HIGH, AIN2 LOW
            self.pwm_ain1.ChangeDutyCycle(vitesse_a)
            self.pwm_ain2.ChangeDutyCycle(0)
        elif vitesse_a < 0:
            # Reculer : AIN1 LOW, AIN2 HIGH
            self.pwm_ain1.ChangeDutyCycle(0)
            self.pwm_ain2.ChangeDutyCycle(abs(vitesse_a))
        else:
            self.pwm_ain1.ChangeDutyCycle(0)
            self.pwm_ain2.ChangeDutyCycle(0)

        # --- Moteur Droit (B) ---
        vitesse_b = max(min(droite, 100), -100) * (1 - malus_droite/100)
        if vitesse_b > 0:
            # Avancer : BIN1 HIGH, BIN2 LOW
            self.pwm_bin1.ChangeDutyCycle(vitesse_b)
            self.pwm_bin2.ChangeDutyCycle(0)
        elif vitesse_b < 0:
            # Reculer : BIN1 LOW, BIN2 HIGH
            self.pwm_bin1.ChangeDutyCycle(0)
            self.pwm_bin2.ChangeDutyCycle(abs(vitesse_b))
        else:
            self.pwm_bin1.ChangeDutyCycle(0)
            self.pwm_bin2.ChangeDutyCycle(0)
    
    def stop(self):
        self.pwm_ain1.ChangeDutyCycle(0)
        self.pwm_ain2.ChangeDutyCycle(0)
        self.pwm_bin1.ChangeDutyCycle(0)
        self.pwm_bin2.ChangeDutyCycle(0)
        # Optionnel : mettre NSLEEP à LOW pour économiser de l'énergie
        # GPIO.output(self.STBY, GPIO.LOW)
        
    def cleanup(self):
        self.stop()
        GPIO.output(self.STBY, GPIO.LOW)
        GPIO.cleanup()

# Test de la classe Moteur
if __name__ == "__main__":
    try:
        moteur = Moteur()
        print("Test du pilotage différentiel...")

        print("En avant toute (50%)")
        moteur.piloter(50, 50)
        time.sleep(2)

        print("Rotation sur place à droite")
        moteur.piloter(40, -40)
        time.sleep(1)

        print("Reculer en courbe")
        moteur.piloter(-30, -60)
        time.sleep(2)

        moteur.stop()
        
    except KeyboardInterrupt:
        pass
    finally:
        moteur.cleanup()