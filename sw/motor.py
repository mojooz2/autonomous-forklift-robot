from machine import Pin, PWM
from utime import sleep

class Motor:
    def __init__(self, dirPin, PWMPin):
        self.mDir = Pin(dirPin, Pin.OUT)  # set motor direction pin
        self.pwm = PWM(Pin(PWMPin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
        self.speed = 100
        
    def off(self):
        self.pwm.duty_u16(0)
        
    def Forward(self):
        self.mDir.value(0)                     # forward = 0 reverse = 1 motor
        self.pwm.duty_u16(int(65535 * self.speed / 100))  # speed range 0-100 motor

    def Reverse(self):
        self.mDir.value(1)
        self.pwm.duty_u16(int(65535 * self.speed / 100))
