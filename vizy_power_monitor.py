#!/bin/python3
import getpass
import time
import os
import signal
from datetime import datetime  
from vizypowerboard import VizyPowerBoard, get_cpu_temp

BRIGHTNESS = 0x30
WHITE = [BRIGHTNESS//3, BRIGHTNESS//3, BRIGHTNESS//3]
YELLOW = [BRIGHTNESS//2, BRIGHTNESS//2, 0]
SYNC_TIMEOUT = 60*5 # seconds
# Start using fan at this temperature.
TEMP_MIN = 65 # Celcius
# CPU is throttled back at 80C -- we want to try our hardest not to get there.
TEMP_MAX = 75 
FAN_MIN = 1
FAN_MAX = 5
FAN_WINDOW = 30 # seconds
FAN_ATTEN = 0.25

script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)
logfile = open("log.txt", "a")

def log(msg):
    logfile.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} {msg}\n")
    logfile.flush()

log(f"Running {os.path.realpath(__file__)} as user {getpass.getuser()}")
if getpass.getuser() != "root":
    log(f"ERROR:  must run as root")

class PowerMonitor:
    def __init__(self):
        log("Running Vizy Power Monitor...")
        self.count = 0
        self.last_fan_speed = 0
        self.fan_speed = (0, 0)
        self.avg_fan_speed = 0
        self.run = True

        def handler(signum, frame):
            self.run = False

        signal.signal(signal.SIGINT, handler)   
        signal.signal(signal.SIGTERM, handler)  

        self.v = VizyPowerBoard()

        # Set time using battery-backed RTC time on Vizy Power Board,
        # unless it's already been set by systemd-timesyncd.  
        # So we set the time based on the RTC value.  If we can't sync
        # in the future because we don't have a network connection, 
        # we have the battery-backed RTC value to fall back on. 
        if not os.path.exists("/run/systemd/timesync/synchronized"):
            self.v.rtc_set_system_datetime() 

        # Set background LED to yellow (finished booting).
        self.v.led_background(*YELLOW)

        # Poll continuously...
        while self.run:

            self.handle_timesync()
            self.handle_fan()
            self.handle_power_button()

            time.sleep(1)

        if self.v.led_background()==YELLOW:
            self.v.led_background(*WHITE)
        self.v.fan(0)

        log("Exiting Vizy Power Monitor")


    def handle_power_button(self):
        # Check power button status.
        powerOff = self.v.power_off_requested()
        if powerOff:
            # Initate shutdown.
            # Turn off background LED.
            self.v.led_background(0, 0, 0)
            # Flash LED red as we shut down.
            self.v.led(255, 0, 0, 0, True, 15, 500, 500)
            os.system('shutdown now')
            self.run = False


    def handle_timesync(self):
        # Spend the first minutes looking for timesync update so we can update the RTC.
        if self.count<SYNC_TIMEOUT:
            if os.path.exists("/run/systemd/timesync/synchronized"):
                # Update RTC time because it will likely be slightly more accurate.
                self.v.rtc(datetime.now())
                count = SYNC_TIMEOUT # We're done.
            else:
                self.count += 1      


    # We scale the fan speed based on the temperature.  At TEMP_MIN, the fan turns at
    # FAN_MIN.  At TEMP_MAX, the fan turns at FAN_MAX.  
    def handle_fan(self):
        temp = get_cpu_temp()
        fan_speed = (temp-TEMP_MIN)/(TEMP_MAX-TEMP_MIN)*(FAN_MAX-FAN_MIN) + FAN_MIN
        self.avg_fan_speed = FAN_ATTEN*fan_speed + (1-FAN_ATTEN)*self.avg_fan_speed
        if self.avg_fan_speed<FAN_MIN:
            fan_speed = FAN_MIN
        elif self.avg_fan_speed>FAN_MAX:
            fan_speed = FAN_MAX
        else:
            fan_speed = round(self.avg_fan_speed)

        #print(temp, fan_speed, self.avg_fan_speed)
        t = time.time()

        # Be more responsive to increases in fan speed than decreases.
        if fan_speed>self.fan_speed[0]: 
            self.fan_speed = (fan_speed, t)
            self.set_fan(fan_speed)
            self.v.fan(fan_speed)
        # Only decrease fan speed if our window expires.
        elif t-self.fan_speed[1]>FAN_WINDOW:
            self.fan_speed = (fan_speed, t)
            self.set_fan(fan_speed)
            self.v.fan(fan_speed)

    def set_fan(self, speed):
        self.v.fan(speed)
        if speed != self.last_fan_speed:
            self.last_fan_speed = speed
            log(f"CPU temp {get_cpu_temp():.1f}, changing fan speed to {speed}")

try:
    PowerMonitor()
except Exception as e:
    log(f"Received exceptiopn {e}, exiting")    
finally:
    log("Exiting")




