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

    def capture(self, label=None):
        """Capture images with a specific naming convention."""
        with self.lock:  
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            voltage = self.voltage  
            label = label or "motion_detected"  

            for i in range(5):
                filename = f'./temp/{label}_{i + 1}_{timestamp}_{voltage:.2f}.jpg'
                
                # Capture the image
                self.picam2.start_and_capture_files(filename, initial_delay=0, delay=1, num_files=1)
                print(f"Captured image: {filename}")
                sleep(1) 
    def read_led_voltage(self):
            """Continuously read LED voltage."""
            while True:
                value = self.adc.analogRead(0)  
                self.voltage = value / 255.0 * 3.3 
                sleep(0.1)  
    def read_motion_detector(self):
                """Detect motion and trigger the capture method."""
                previous_state = False
                while True:
                    current_state = self.sensor.motion_detected

                    if current_state and not previous_state:
                        print("Motion detected! >>>")
                        self.capture()  
                        previous_state = True

                    elif not current_state and previous_state:
                        print("Motion stopped! <<<")
                        previous_state = False
                    
                    sleep(0.1) 
            
  
def main():
    eq = EventQueue()  
    camera = WildlifeCamera(eq)

    # Start threads for different functionalities
    voltage_thread = Thread(target=camera.read_led_voltage)
    motion_thread = Thread(target=camera.read_motion_detector)
    # event_queue_thread = Thread(target=camera.read_event_queue)

    voltage_thread.start()
    motion_thread.start()
    # event_queue_thread.start()

      
if __name__ == "__main__":
    main()