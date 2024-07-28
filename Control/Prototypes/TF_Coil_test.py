from pynq import GPIO
import time
import matplotlib.pyplot as plt
from pynq.lib import Pmod_PWM
from pynq.overlays.base import BaseOverlay
from pynq.lib.arduino import Arduino_Analog
from pynq.lib.arduino import ARDUINO_GROVE_A1

# Set overlay
base = BaseOverlay("base.bit")

# For pmod
pwm = Pmod_PWM(base.PMODA,0)

# Hall sensor pin
analog1 = Arduino_Analog(base.ARDUINO,ARDUINO_GROVE_A1)
sensorOffset = 0;

# Hall sensor data variables
sensorValues = []

# Definitions
MAX_CURRENT = 0.2

# Set PWM frequency/period (microsecs) and duty cycle for the TF coil
period = 50 
dutyCycle = 0

# Declare PID variables
error = 0
errorSum = 0
errorDif = 0
oldError = 0

rawVal = 0
currentVal = 0
currentValDamped = 0
refVal = 0

kp = 3000
ki = 0.007
kd = -0.05

sampTimeBegin = 0
sampTimeEnd = 0
sampPeriod = 0

# Pulse Reference Variables
executePulse = 0
pulseStarted = 0
pulseTimeStart = 0
pulseTime = 0

# Calibrate 
for i in range(10):
    sensorOffset = sensorOffset + (analog1.read('raw')[0] - 32768)
    time.sleep(100)
    
print('Calibrating...')
sensorOffset = sensorOffset / 10;
    
# MAIN - Enable PWM output for the TF coil
    
print('Running...')
while base.buttons[0].read() == 0:
    # Get current measurement and convert
    rawVal = (analog1.read('raw')[0] - sensorOffset)
    currentVal = ((rawVal - 32768) / 65536) * 5 / 0.186
    currentValDamped = currentValDamped * 0.99 + currentVal * 0.01         

    # Set reference current
    base.buttons[1].read() = executePulse
    if (executePulse == 1 & pulseStarted == 0):
        pulseTimeStart = time.time()
        pulseStarted = 1
        print('Starting Pulse')
        
    if (pulseStarted == HIGH):
        pulseTime = time.time() - pulseTimeStart
        
        analog1.set_log_interval_ms(10)
        analog1.start_log()
        
    if ((pulseTime < 0.5) && (pulseStarted == HIGH)):
        refVal = pulseTime * MAX_CURRENT/0.5
        
    elif ((pulseTime < 1) && (pulseStarted == HIGH)):
        refVal = MAX_CURRENT
        
    elif ((pulseTime < 1.5) && (pulseStarted == HIGH)):
        refVal = MAX_CURRENT - (pulseTime - 1.5) * MAX_CURRENT/0.5
        
    elif ((pulseTime >= 1.5) && (pulseStarted == HIGH)):
        pulseStarted = LOW
        refVal = 0
        
        sensor_values = analog1.get_log()
        plt.plot(sensor_values[0])
        plt.xlabel('Time')
        plt.ylabel('Voltage (temp)')
        plt.title('Current in TF coil')
        plt.show()
        
    else:
        refVal = 0

    #Read input time 
    sampTimeEnd = time.time()
    sampPeriod = sampTimeEnd - sampTimeBegin
    sampTimeBegin = time.time()        
    
    # Calculate errors
    error = refVal - currentValDamped
    errorSum += error
    errorSum = min(2, max(-2, errorSum))
    errorDif = error - oldError

    # Calculate gains and output
    dutyCycle = (kp * error) + (ki * errorSum * sampPeriod) + (kd * errorDif / sampPeriod)
    dutyCycle = min(99, max(1, dutyCycle))

    # Send output
    pwm.generate(period, duty_cycle)

    # Calculate next PID step values
    oldError = error
