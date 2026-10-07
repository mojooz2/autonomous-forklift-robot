# Import set of modules
from machine import Pin, Timer
from utime import sleep
import micropython

# Import classes and functions from other files
from follow_junction import follow_junction
from motor import Motor
from actuator import lift

micropython.alloc_emergency_exception_buf(100)

button = Pin(26, Pin.IN, Pin.PULL_DOWN)
amber = Pin(28, Pin.OUT)
leftMotor = Motor(dirPin=4, PWMPin=5)
rightMotor = Motor(dirPin=7, PWMPin=6)
red = Pin(22, Pin.OUT)

# If checkButton(t) is activated, it checks whether the button is pressed. If it is, all operators
# in the robot including motors, actuator, and LEDs in the robot are immediately turned OFF.
# checkButton(t) is only activated after the first time the button is pressed (this turns the robot ON)
def checkButton(t):
    if(button.value()==1):
        leftMotor.off()
        rightMotor.off()
        lift(0)
        amber.value(0)
        red.value(0)
        # stops robot by putting it to sleep for 1000 seconds after turning all devices OFF
        sleep(1000)

print("Welcome to main.py! This is IDP team 110")

# Initially, all LED are off until button.value() becomes 1
red.value(0)
amber.value(0)
while(button.value() == 0):
    sleep(0.1)
    continue
while(button.value() == 1):
    sleep(0.1)
    continue
# amber led flashes ON
amber.value(1)

tim = Timer()
# A periodic timer is recalled every 0.1 seconds (freq = 10) checking whether the button is pressed
# If the button is pressed, the if statement in checkButton(t) will be activated, stopping the robot.
tim.init(mode=Timer.PERIODIC, freq=10, callback=checkButton)

# Initial set of directions is always ST -> LT -> IG -> LT -> LD -> RO for the robot to move to bay 1,
# scan the qr code (this is the point where a new set of instructions will be extended to the list
# of directions), load the box, and rotate.
directions = ["ST", "LT", "IG", "LT", "LD", "RO"]

# "follow_junction(moves)" function from "follow_junction.py" is run with "directions" as input.
follow_junction(directions)

print("main.py Done!")
# turns amber led OFF if run is finished.
amber.value(0)

# Reset linear actuator to appropriate height 
