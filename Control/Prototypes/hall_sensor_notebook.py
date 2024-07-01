from pynq import GPIO
import time
import matplotlib.pyplot as plt

hall_sensor_pin = GPIO(GPIO.get_gpio_pin(0), 'in')

data_rate = 0.1
run_time = 5
sensor_values = []

start_time = time.time()

try:
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

except KeyboardInterrupt:
    pass
