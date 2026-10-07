from machine import Pin, PWM, I2C
from libs.VL53L0X.VL53L0X import VL53L0X
from libs.tiny_code_reader.tiny_code_reader import TinyCodeReader
from utime import sleep
from utime import ticks_ms, ticks_diff

red = Pin(22, Pin.OUT)
red.value(1)

i2c_bus = I2C(id=1, sda=Pin(14), scl=Pin(15)) # I2C1 on GP14 & GP15
    
# Setup vl53l0 object
vl53l0 = VL53L0X(i2c_bus)
vl53l0.set_Vcsel_pulse_period(vl53l0.vcsel_period_type[0], 18)
vl53l0.set_Vcsel_pulse_period(vl53l0.vcsel_period_type[1], 14)
vl53l0.start()
qr_bus = I2C(id=0, scl=Pin(9), sda=Pin(8), freq=400000)
    
qr_code_reader = TinyCodeReader(qr_bus)

while True:
    sleep(0.1)
    distance = vl53l0.read()
    sleep(TinyCodeReader.TINY_CODE_READER_DELAY)
    qr_code = None
    try:
        qr_code = qr_code_reader.poll()
    except:
        qr_code = None
    print(distance, qr_code)
    