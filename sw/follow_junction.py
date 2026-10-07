# Import python modules
from machine import Pin, I2C
from utime import sleep

# Import special sensor modules
from libs.VL53L0X.VL53L0X import VL53L0X
from libs.tiny_code_reader.tiny_code_reader import TinyCodeReader

# Import from motor and actuator
from motor import Motor
from actuator import lift, lower

# Import our line following and navigation modules
from line_follow import line_follow
from navigation import navigation_moves

def follow_junction(moves):
    amber = Pin(28, Pin.OUT)
    button = Pin(26, Pin.IN, Pin.PULL_DOWN)
    leftMotor = Motor(dirPin=4, PWMPin=5)
    rightMotor = Motor(dirPin=7, PWMPin=6)
    #red pin left, oragne pin right
    #left motor -> J39, right motor -> J40
    leftLineSensor = Pin(18, Pin.IN, Pin.PULL_DOWN) #pin 24
    rightLineSensor = Pin(19, Pin.IN, Pin.PULL_DOWN) #pin 25
    leftJunctionSensor = Pin(20, Pin.IN, Pin.PULL_DOWN) #pin 26
    rightJunctionSensor = Pin(21, Pin.IN, Pin.PULL_DOWN) #pin 27
    
    i2c_bus = I2C(id=1, sda=Pin(14), scl=Pin(15)) # I2C1 on GP14 & GP15
    
    # Setup vl53l0 object
    vl53l0 = VL53L0X(i2c_bus)
    vl53l0.set_Vcsel_pulse_period(vl53l0.vcsel_period_type[0], 18)
    vl53l0.set_Vcsel_pulse_period(vl53l0.vcsel_period_type[1], 14)
    
    # Setup TinyCodeReader
    qr_bus = I2C(id=0, scl=Pin(9), sda=Pin(8), freq=400000)
    qr_code_reader = TinyCodeReader(qr_bus)

    red = Pin(22, Pin.OUT)
    red.value(0)

    # Start the distance sensor and initialise variables
    vl53l0.start()
    junction = False
    move = 0
    turntime = 0.57
    rotatime = 1.24
    start = True
    bay_station = 1
    
    while start==True:
        # Each loop, read the values from the line sensors
        ll = leftLineSensor.value()
        rl = rightLineSensor.value()
        lj = leftJunctionSensor.value()
        rj = rightJunctionSensor.value()
        
        # The following moves can occur regardless of whether the robot is at a junction
        if moves[move] in ["RO", "LUL", "UUL", "LD", "ST"]:
            if moves[move] == "RO":
                # Rotate the robot 180 degrees
                rightMotor.Forward()
                leftMotor.Reverse()
                sleep(rotatime)
                leftMotor.off()
                rightMotor.off()
                
            elif moves[move] == "LUL" or moves[move] == "UUL":

                # Unloading logic, differs depending on if we are unloading on the upper or lower level

                # Slow down to improve line following accuracy while unloading
                leftMotor.speed = 70
                rightMotor.speed = 70
                
                if moves[move] == "LUL":
                    # Lower level unload

                    # Heigh of fork = 26 mm. The box is actually lower than this because of the pallet height.
                    lift(20)
                    # Height of fork = 46 mm

                    # Move forward a bit to clear the junction
                    leftMotor.Forward()
                    rightMotor.Forward()
                    sleep(0.1)

                    # Line follow until we reach the end of the line
                    while(ll==1 or rl ==1):
                        line_follow(leftLineSensor, rightLineSensor, leftMotor, rightMotor, leftJunctionSensor, rightJunctionSensor)
                        ll = leftLineSensor.value()
                        rl = rightLineSensor.value()
                    leftMotor.off()
                    rightMotor.off()

                    lower(9)
                    # Height of fork = 35 mm

                    # Reverse out after lowering the box
                    leftMotor.Reverse()
                    rightMotor.Reverse()
                    sleep(0.8)
                    leftMotor.off()
                    rightMotor.off()
                    lower(11)
                    # Height of fork = 26 mm
                    
                elif moves[move] == "UUL":
                    # Upper level unload

                    # Height of fork = 26 mm

                    # Move forward a bit to clear the junction
                    leftMotor.Forward()
                    rightMotor.Forward()
                    sleep(0.1)
                    
                    # Line follow until we reach the end of the line 
                    while(ll==1 or rl ==1):
                        line_follow(leftLineSensor, rightLineSensor, leftMotor, rightMotor, leftJunctionSensor, rightJunctionSensor)
                        ll = leftLineSensor.value()
                        rl = rightLineSensor.value()
                    leftMotor.off()
                    rightMotor.off()

                    lower(20)
                    # Height of fork = 6 mm

                    # Reverse out after lowering the box
                    leftMotor.Reverse()
                    rightMotor.Reverse()
                    sleep(0.8)
                    leftMotor.off()
                    rightMotor.off()
                    lift(20)
                    # Height of fork = 26 mm

                # Bring the motors back up to full speed
                leftMotor.speed = 100
                rightMotor.speed = 100
                
            elif moves[move] == "LD":
                # Loading a box

                # Turn on the red LED and power up the QR code reader
                red.value(1)
                
                # Calibrate the linear actuator
                lower(35)
                # Height of fork = 0 mm
                lift(6)
                # Height of fork = 6 mm

                # Reduce speed to improve accuracy of picking up the box
                leftMotor.speed = 80
                rightMotor.speed = 80

                # Read the initial distance and initialise the QR code read to None
                distance = vl53l0.read()
                qr_code = None
                
                # Line follow towards the box until the line sensor reports a distance of 400 mm
                while(lj ==0 and rj ==0 and distance>400):
                    line_follow(leftLineSensor, rightLineSensor, leftMotor, rightMotor, leftJunctionSensor, rightJunctionSensor)
                    lj = leftJunctionSensor.value()
                    rj = rightJunctionSensor.value()
                    distance = vl53l0.read()
                    
                leftMotor.off()
                rightMotor.off()
                
                # Attempt to read the QR code repeatedly. Try except used as polling sometimes throws errors.
                while qr_code == None:
                    sleep(TinyCodeReader.TINY_CODE_READER_DELAY)
                    try:
                        qr_code = qr_code_reader.poll()
                    except:
                        qr_code = None

                # Once the QR code has been read, power off the red LED and the QR code reader            
                red.value(0)

                # Append set of moves depending on QR code value
                moves = navigation_moves(qr_code, bay_station, moves)
                bay_station += 1
                
                # Line follow until we reach the box with the QR code 
                while(lj ==0 and rj ==0):
                    line_follow(leftLineSensor, rightLineSensor, leftMotor, rightMotor, leftJunctionSensor, rightJunctionSensor)
                    lj = leftJunctionSensor.value()
                    rj = rightJunctionSensor.value()
                     
                # Move forward until the distance to the box is 35 mm
                leftMotor.Forward()
                rightMotor.Forward()
                while(distance>35):
                    distance = vl53l0.read()
                
                # Move forward a bit more to pick up the box
                sleep(0.2)
                leftMotor.off()
                rightMotor.off()

                # Raise the box and reverse out of the loading bay
                lift(20)
                # Height of fork = 26 mm
                leftMotor.Reverse()
                rightMotor.Reverse()
                sleep(0.6)
                leftMotor.off()
                rightMotor.off()

                # Bring the motors back up to normal speed
                leftMotor.speed = 100
                rightMotor.speed = 100
            elif moves[move] == "ST":
                # Go straight to exit the initial box, until the junction detection goes to 1 and back to 0
                leftMotor.Forward()
                rightMotor.Forward()
                while lj == 0 or rj == 0:
                    lj = leftJunctionSensor.value()
                    rj = rightJunctionSensor.value()
                while lj == 1 or rj == 1:
                    lj = leftJunctionSensor.value()
                    rj = rightJunctionSensor.value()
                leftMotor.off()
                rightMotor.off()
            move += 1
        #end of {if moves[move] in ["RO", "LUL", "UUL", "LD", "ST"]:}
            
        elif junction == False:
            # Basic line following / keeping robot on white line
            line_follow(leftLineSensor, rightLineSensor, leftMotor, rightMotor, leftJunctionSensor, rightJunctionSensor)
            # Junction detecgt
            if lj == 1 or rj == 1:
                junction = True
        elif junction == True:
            print(moves[move])
            # Continue until we have passed the junction
            while not(lj == 0 and rj == 0):
                leftMotor.Forward()
                rightMotor.Forward()
                lj = leftJunctionSensor.value()
                rj = rightJunctionSensor.value()
            if moves[move] == "LT":
                rightMotor.Forward()
                leftMotor.Reverse()
                sleep(turntime)
                leftMotor.Forward()
                while(lj ==1 or rj==1):
                    lj = leftJunctionSensor.value()
                    rj = rightJunctionSensor.value()
                    continue
                sleep(0.1)
                
            elif moves[move] == "RT":
                rightMotor.Reverse()
                leftMotor.Forward()
                sleep(turntime)
                rightMotor.Forward()
                while(lj ==1 or rj==1):
                    lj = leftJunctionSensor.value()
                    rj = rightJunctionSensor.value()
                    continue
                sleep(0.1)
                
            elif moves[move] == "IG":
                leftMotor.Forward()
                rightMotor.Forward()
                while(lj ==1 or rj==1):
                    lj = leftJunctionSensor.value()
                    rj = rightJunctionSensor.value()
                    continue
                sleep(0.1)
            elif moves[move] == "FL":
                leftMotor.Forward()
                rightMotor.Forward()
                sleep(0.75)
                leftMotor.Reverse()
                sleep(rotatime)
                for i in range(10):
                    sleep(0.2)
                    rightMotor.Reverse()
                    leftMotor.Forward()
                    sleep(0.2)
                    rightMotor.Forward()
                    leftMotor.Reverse()
                leftMotor.off()
                rightMotor.off()
                amber.value(0)
                
            rightMotor.off()
            leftMotor.off()
            move += 1
            junction = False
        # end of {elif junction == True:}
        if move == len(moves) or bay_station > 5:
            start = False
            print("stopping")
