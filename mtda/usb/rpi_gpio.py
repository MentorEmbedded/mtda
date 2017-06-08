# System imports
import abc
import RPi.GPIO as GPIO

# Local imports
from mtda.usb.switch import UsbSwitch

class RPiGpioUsbSwitch(UsbSwitch):

    def __init__(self):
        self.dev = None
        self.pin = 0
        GPIO.setwarnings(False)

    def configure(self, conf):
        """ Configure this USB switch from the provided configuration"""
        if 'pin' in conf:
            self.pin = int(conf['pin'], 10)
        if self.pin > 0:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
        return

    def probe(self):
        return

    def on(self):
        """ Power on the target USB port"""
        return GPIO.output(self.pin, GPIO.LOW)

    def off(self):
        """ Power off the target USB port"""
        return GPIO.output(self.pin, GPIO.HIGH)

    def status(self):
        """ Determine the current power state of the USB port"""
        if GPIO.input(self.pin) == 1:
            return self.POWERED_OFF
        else:
            return self.POWERED_ON

    def toggle(self):
        s = self.status()
        if s == self.POWERED_ON:
            self.off()
            return self.POWERED_OFF
        else:
            self.on()
            return self.POWERED_ON

def instantiate():
   return RPiGpioUsbSwitch()
