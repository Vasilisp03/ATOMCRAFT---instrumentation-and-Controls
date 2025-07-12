from pynq import GPIO
import time
import matplotlib.pyplot as plt
from pynq.lib import Pmod_PWM
from pynq.overlays.base import BaseOverlay
from pynq.lib.arduino import Arduino_Analog
from pynq.lib.arduino import ARDUINO_GROVE_A1
import threading

# set overlay
base = BaseOverlay("base.bit")

# for pmod
pwm = Pmod_PWM(base.PMODA,0)

# Hall sensor pin
analog1 = Arduino_Analog(base.ARDUINO,ARDUINO_GROVE_A1)

# Set PWM frequency and duty cycle for the TF coil
freq = 1000 
global dc
dc = 50  

# hall sensor variables
data_rate = 0.1
run_time = 5
sensor_values = []

# Enable PWM output for the TF coil

def pwm_signal():
    global dc
    while True:
        time.sleep(0.01)
        
        
        if base.buttons[1].read() == 1:
            if dc < 98:
                dc = dc + 1
        elif base.buttons[2].read() == 1:
            if dc > 2:
                dc = dc - 1
        
        pwm.generate(freq, dc)

    pwm.stop()

def hall_sensor():
    print('Hall sensor ready')
    while True: 
        if base.buttons[3].read()==1:
            analog1.set_log_interval_ms(10)
            analog1.start_log()
            
            time.sleep(5)
            
            sensor_values = analog1.get_log()
            
            plt.plot(sensor_values[0])
            plt.xlabel('Time')
            plt.ylabel('Voltage (temp)')
            plt.title('Current in TF coil')

            plt.show()


try:
    print('running...')
    pwm_start = threading.Thread(target = pwm_signal)
    hall_start = threading.Thread(target = hall_sensor)

    start_time = time.time()

    pwm_start.start()
    hall_start.start()

except KeyboardInterrupt:

    pwm.stop()

    pwm_start.join()
    hall_start.join()
