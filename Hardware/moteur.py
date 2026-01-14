import RPI.GPIO as GPIO
import time

class Moteur:
    def ___init__(self, 
                  ain1=26, ain2=20, pwma=21,
                  bin1=17, bin2=27, pwmb=18,
                  stby=22,
                  force=20,
                  temps360=2.5):
        
        # Pins
        self.AIN1 = ain1
        self.AIN2 = ain2
        self.BIN1 = bin1
        self.BIN2 = bin2
        self.STBY = stby
        
        # Parametres
        self.force = force
        self.temps360 = temps360
        
        # Init GPIO
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(pwma, GPIO.OUT)
        GPIO.setup(pwmb, GPIO.OUT)
        GPIO.setup(self.STBY, GPIO.OUT)
        
        self.pwmA = GPIO.PWM(pwma, 1000)
        self.pwmB = GPIO.PWM(pwmb, 1000)
        
        self.pwmA.start(0)
        self.pwmB.start(0)
        
        # Activer le driver
        GPIO.output(self.STBY, GPIO.HIGH)

    # Controlleur bas niveau
    def _set_motors(self, a1, a2, b1, b2, duty):
        GPIO.output(self.AIN1, a1)
        GPIO.output(self.AIN2, a2)
        GPIO.output(self.BIN1, b1)
        GPIO.output(self.BIN2, b2)
        self.pwmA.ChangeDutyCycle(duty)
        self.pwmB.ChangeDutyCycle(duty)
    
    # Cleand up
    def stop(self):
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB.ChangeDutyCycle(0)
        GPIO.output(self.STBY, GPIO.LOW)
        
    def cleanup(self):
        self.stop()
        GPIO.cleanup()