#Don't need this file anymore

from machine import Pin, I2C
from libs.tiny_code_reader.tiny_code_reader import TinyCodeReader
from libs.VL53L0X.VL53L0X import VL53L0X
from utime import sleep

def QR_code_reader():
    red = Pin(22, Pin.OUT)
    red.value(1)
    sleep(0.1)
    
    qr_bus = I2C(id=0, scl=Pin(9), sda=Pin(8), freq=400000)
    print(qr_bus.scan())
    qr_devs = qr_bus.scan()
    assert len(qr_devs) == 1 # This demo requires exactly one device
    assert qr_devs[0] == 12 # Expected device
    qr_code_reader = TinyCodeReader(qr_bus)
    

    

    QR_code = None
    while QR_code is None:
        QR_code = qr_code_reader.poll()
        sleep(0.5)
        print("Reading")
        
    print(QR_code)

    

if __name__ == "__main__":
    QR_code_reader()

