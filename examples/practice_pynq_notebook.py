from time import sleep
from pynq.overlays.base import BaseOverlay

base = BaseOverlay("base.bit")

Delay1 = 0.1
Delay2 = 0.1
color = 0
rgbled_position = [4,5]

for led in base.leds:
    led.on()    
while (base.buttons[3].read()==0):
    if (base.switches[0].read==1):
        Delay2 = 0.5
    elif (base.switches[1].read==1):
        Delay2 = 0.001
    if (base.buttons[0].read()==1):
        color = (color+1) % 8
        for led in rgbled_position:
            base.rgbleds[led].write(color)
            base.rgbleds[led].write(color)
        sleep(Delay1)
        
    elif (base.buttons[1].read()==1):
        for led in base.leds:
            led.off()
        sleep(Delay2)
        for led in base.leds:
            led.toggle()
            sleep(Delay2)
            
    elif (base.buttons[2].read()==1):
        for led in reversed(base.leds):
            led.off()
        sleep(Delay2)
        for led in reversed(base.leds):
            led.toggle()
            sleep(Delay2)                  
    
print('End of this demo ...')
for led in base.leds:
    led.off()
for led in rgbled_position:
    base.rgbleds[led].off()