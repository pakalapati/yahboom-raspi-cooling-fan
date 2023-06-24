import Adafruit_GPIO.I2C as I2C

import time
import os
import smbus
bus = smbus.SMBus(1)

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

hat_addr = 0x0d
rgb_effect_reg = 0x04
fan_reg = 0x08
count = 0
fan_speed = 0
Max_LED = 3

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

def setFanSpeed(speed):
    bus.write_byte_data(hat_addr, fan_reg, speed&0xff)

def setRGB(num, r, g, b):
    if num >= Max_LED:
        bus.write_byte_data(hat_addr, 0x00, 0xff)
        bus.write_byte_data(hat_addr, 0x01, r&0xff)
        bus.write_byte_data(hat_addr, 0x02, g&0xff)
        bus.write_byte_data(hat_addr, 0x03, b&0xff)
    elif num >= 0:
        bus.write_byte_data(hat_addr, 0x00, num&0xff)
        bus.write_byte_data(hat_addr, 0x01, r&0xff)
        bus.write_byte_data(hat_addr, 0x02, g&0xff)
        bus.write_byte_data(hat_addr, 0x03, b&0xff)

def getCPULoadRate():
    f1 = os.popen("cat /proc/stat", 'r')
    stat1 = f1.readline()
    count = 10
    data_1 = []
    for i  in range (count):
        data_1.append(int(stat1.split(' ')[i+2]))
    total_1 = data_1[0]+data_1[1]+data_1[2]+data_1[3]+data_1[4]+data_1[5]+data_1[6]+data_1[7]+data_1[8]+data_1[9]
    idle_1 = data_1[3]

    time.sleep(1)

    f2 = os.popen("cat /proc/stat", 'r')
    stat2 = f2.readline()
    data_2 = []
    for i  in range (count):
        data_2.append(int(stat2.split(' ')[i+2]))
    total_2 = data_2[0]+data_2[1]+data_2[2]+data_2[3]+data_2[4]+data_2[5]+data_2[6]+data_2[7]+data_2[8]+data_2[9]
    idle_2 = data_2[3]

    total = int(total_2-total_1)
    idle = int(idle_2-idle_1)
    usage = int(total-idle)
    print("idle:"+str(idle)+"  total:"+str(total))
    usageRate =int(float(usage * 100/ total))
    print("usageRate:%d"%usageRate)
    return "CPU:"+str(usageRate)+"%"


def run(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True)


def setOLEDshow():
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    cmd = os.popen('vcgencmd measure_temp').readline()
    global g_temp
    g_temp = float(cmd.replace("temp=","").replace("'C\n",""))

    # Write two lines of text.

    draw.text((x, top+8), "CPU Temp: " + str(g_temp),  font=font, fill=255)
    draw.text((x, top+16), "Time: " + str(time.strftime('%H:%M:%S')),  font=font, fill=255)
    draw.text((x, top+24), "Fan Speed: " + str(fan_speed) + "%",  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(1)

setFanSpeed(0x00)

while True:
    try:

        setOLEDshow()
        
        if g_temp <= 40:            
            fan_speed = 0
            setFanSpeed(0x00)
            setRGB(Max_LED, 0x00, 0x00, 0xff)
        elif g_temp <= 42:            
            fan_speed = 40
            setFanSpeed(0x04)
            setRGB(Max_LED, 0x00, 0xbf, 0xff)
        elif g_temp <= 44:            
            fan_speed = 60
            setFanSpeed(0x06)
            setRGB(Max_LED, 0xff, 0xff, 0x00)
        elif g_temp <= 46:            
            fan_speed = 80
            setFanSpeed(0x08)
            setRGB(Max_LED, 0xff, 0xa5, 0x00)
        elif g_temp <= 48:            
            fan_speed = 90
            setFanSpeed(0x09)
            setRGB(Max_LED, 0xff, 0x45, 0x00)
        else:            
            fan_speed = 100
            setFanSpeed(0x01)
            setRGB(Max_LED, 0xff, 0x00, 0x00)
        
    except:
        pass
