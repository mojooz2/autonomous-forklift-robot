from machine import Pin, PWM
from utime import sleep

class Actuator:
    def __init__(self, dirPin, PWMPin):
        self.mDir = Pin(dirPin, Pin.OUT)  # set motor direction pin
        self.pwm = PWM(Pin(PWMPin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
        self.height= 5
           
    def set(self, dir, speed):
        self.mDir.value(dir)                     # forward = 0 reverse = 1 motor
        self.pwm.duty_u16(int(65535 * speed / 100))  # speed range 0-100 motor
    
# Actuator lifts at 7mm/s at max speed

def lift(dist):
    """
    Lift the fork dist mm. 
    """
    actuator = Actuator(dirPin=0, PWMPin=1)
    lift_time = dist/7
    actuator.set(dir=1, speed=100)
    sleep(lift_time)
    actuator.set(dir=1, speed=0)

def lower(dist):
    """
    Lower the fork dist mm. 
    """
    actuator = Actuator(dirPin=0, PWMPin=1)
    lift_time = dist/7
    actuator.set(dir=0, speed=100)
    sleep(lift_time)
    actuator.set(dir=0, speed=0)  
