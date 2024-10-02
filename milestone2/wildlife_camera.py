from threading import Thread, Lock
# from sensor_mock import MockSensor
from event_queue import EventQueue
from time import sleep
from ADCDevice import *
from gpiozero import MotionSensor
from picamera2 import Picamera2
import time
import datetime


class WildlifeCamera:
    def __init__(self, eq: EventQueue):
        self.voltage = 0.0
        self.adc = ADCDevice()
        self.sensorPin = 17  
        self.sensor = MotionSensor(self.sensorPin)
        self.sensor.wait_for_no_motion()
        self.picam2 = Picamera2()
        self.event_queue = eq  
        self.lock = Lock()

        # Check I2C address
        if self.adc.detectI2C(0x4b): 
            self.adc = ADS7830()
        else:
            print("No correct I2C address found.\n"
                  "Please use command 'i2cdetect -y 1' to check the I2C address!\n"
                  "Program Exit.\n")
            exit(-1)

    
if __name__ == "__main__":
    main()