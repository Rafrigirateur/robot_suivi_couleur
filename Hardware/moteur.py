import RPi.GPIO as GPIO
import time

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
        moteur = Moteur(force=50)
        print("Moteur initialisé. Test en cours...")
        
        # Test de rotation à gauche
        print("Avancer")
        moteur._set_motors(GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW, moteur.force)
        time.sleep(2)
        
        # Test de rotation à droite
        print("Reculer")
        moteur._set_motors(GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.HIGH, moteur.force)
        time.sleep(2)
        
        # Test d'arrêt
        print("Arrêt du moteur...")
        moteur.stop()
        
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur. Nettoyage...")
    finally:
        moteur.cleanup()