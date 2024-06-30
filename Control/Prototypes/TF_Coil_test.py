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

# Hall sensor data variables
sensor_values = []

# Enable PWM output for the TF coil
def pwm_signal():
    # Set PWM frequency/period (microsecs) and duty cycle for the TF coil
    period = 50 
    duty_cycle = 0
    
    # Declare PID variables
    error = 0
    error_sum = 0
    error_dif = 0
    old_error = 0
    
    current_val = 0
    prev_val = 0
    ref_val = 0
    
    samp_period = 0
    samp_time_begin = time.time()
    samp_time_end = 0
    
    # PID Constants
    kp = 250
    ki = 0
    kd = 0
    
    offset = analog1.read('raw')[0] - 32768
    
    while base.buttons[0].read() == 0:
        # Get current measurement and convert
        current_val = analog1.read('raw')[0] - offset
        
        current_val = current_val * 0.80 + prev_val * 0.20
        current_val = (current_val - 32768)/65535 * 5.0 * 0.168
                
        time.sleep(1)
        print(current_val)
        
        # Set reference current
        if base.buttons[1].read() == 1:
            ref_val = 0.20
        else: 
            ref_val = 0
            
        #Read input time 

        samp_time_end = time.time() 
        samp_period = samp_time_end - samp_time_begin 
        samp_time_begin = time.time() 
        
        # Calculate errors
        error = ref_val - current_val
        error_sum = error_sum + error
        error_dif = error - old_error

        # Calculate gains and output 
        duty_cycle = (kp * error) #+ (ki * error_sum * samp_period) + (kd * error_dif / samp_period)
        duty_cycle = int(duty_cycle)
        
        # Apply PWM duty cycle limits
        if duty_cycle < 2:
            duty_cycle = 2
        elif duty_cycle > 98:
            duty_cycle = 98
        
        # Send output
        pwm.generate(period, duty_cycle)
        
        # Calculate next PID step values 
        old_error = error 
        prev_val = current_val
        
        # Debugging
        # time.sleep(0.1)
        # print(error)  

    pwm.stop()
    print('Program Ended')

# Create/log current sensor data
def hall_sensor():
    print('Hall sensor ready')
    while base.buttons[0].read() == 0: 
        if base.buttons[3].read() == 1:
            analog1.set_log_interval_ms(10)
            analog1.start_log()
            
            time.sleep(5)
            
            sensor_values = analog1.get_log()
            
            plt.plot(sensor_values[0])
            plt.xlabel('Time')
            plt.ylabel('Voltage (temp)')
            plt.title('Current in TF coil')

            plt.show()

# Main loop
try:
    print('running...')
    pwm_start = threading.Thread(target = pwm_signal)
    hall_start = threading.Thread(target = hall_sensor)

    start_time = time.time()

    pwm_start.start()
    hall_start.start()
    
    while base.buttons[0].read() == 1:
        pwm_start.join()
        hall_start.join()

except KeyboardInterrupt:

    pwm.stop()

    pwm_start.join()
    hall_start.join()
