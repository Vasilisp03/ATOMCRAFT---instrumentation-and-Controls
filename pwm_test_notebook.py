from pynq import GPIO
import time
import matplotlib.pyplot as plt
from pynq.lib import Pmod_PWM
from pynq.overlays.base import BaseOverlay
import threading

# for button to actually start the test
base = BaseOverlay("base.bit")

# for pmod
pwm = Pmod_PWM(base.PMODA,0)

# use pmod for pwm OR GPIO IDK WHICH TO USE
# pwm = Pmod_PWM(base.PMODA,0)

# Define GPIO pins connected to the H-bridge control inputs
forward_pin = GPIO(GPIO.get_gpio_pin(0), 'out')
backward_pin = GPIO(GPIO.get_gpio_pin(1), 'out')

# Hall sensor pin
hall_sensor_pin = GPIO(GPIO.get_gpio_pin(3), 'in')

# Define the PWM pin connected to the TF coil
pwm_pin = GPIO(GPIO.get_gpio_pin(2), 'out')

# Set PWM frequency and duty cycle for the TF coil
pwm_frequency = 1000 
pwm_duty_cycle = 50  

# hall sensor variables
data_rate = 0.1
run_time = 5
sensor_values = []

# Enable PWM output for the TF coil
pwm_pin.write(1)

start_time = 0

def pwm_signal():
    while True:
        
        if time.time() - start_time >= run_time:
            break
        
        # Control the H-bridge to rotate the TF coil in one direction
        forward_pin.write(1)
        backward_pin.write(0)

        # Adjust the PWM duty cycle for controlling the TF coil speed
        pwm.generate(pwm_frequency, pwm_duty_cycle)

        # Wait for some time (you might need to adjust the duration)
        time.sleep(4)

        pwm.stop()
        # Control the H-bridge to stop the TF coil
        forward_pin.write(0)
        backward_pin.write(0)

        # Wait for some time before changing direction or stopping (you might need to adjust the duration)
        time.sleep(1)

        # Repeat the process for controlling the TF coil in the opposite direction, if needed just swap 
        # forward and backward pin writes

def hall_sensor():
    while True:
        if time.time() - start_time >= run_time:
            break
        
        sensor_values.append(hall_sensor_pin.read())

        # depending on how frequent we want to collect data we can change data_rate
        time.sleep(data_rate)
    print(f'collected {len(sensor_values)} current values')    
    
    plt.plot(sensor_values)
    
    plt.xlabel('Time')
    plt.ylabel('Current')
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

    forward_pin.write(0)
    backward_pin.write(0)
    pwm_pin.write(0)

    pwm_start.join()
    hall_start.join()
