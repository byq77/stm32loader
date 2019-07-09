# Author: Floris Lambrechts
# GitHub repository: https://github.com/florisla/stm32loader
#
# This file is part of stm32loader.
#
# stm32loader is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3, or (at your option) any later
# version.
# 
# stm32loader is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with stm32loader; see the file LICENSE.  If not see
# <http://www.gnu.org/licenses/>.

"""
Handle RS-232 serial communication through pyserial.

Offer support for toggling RESET and BOOT0.
"""

# not naming this file itself 'serial', becase that name-clashes in Python 2
from __future__ import print_function
import serial
import sys
import RPi.GPIO as GPIO


class SerialConnectionRpi:
    """Wrap a serial.Serial connection and toggle reset and boot0."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, serial_port, baud_rate=115200, parity="E", gpio_reset_pin=int(12), gpio_boot0_pin=int(11)):
        """Construct a SerialConnectionRpi (not yet connected)."""
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.parity = parity
        self.can_toggle_reset = True
        self.can_toggle_boot0 = True
        self.reset_active_high = False
        self.boot0_active_low = False

        # call connect() to establish connection
        self.serial_connection = None

        self._timeout = None

        # assigned using setter methods
        self.timeout = 5

        self._gpio_reset_pin = gpio_reset_pin
        self._gpio_boot0_pin = gpio_boot0_pin
        self._gpio_reset_init = False
        self._gpio_boot0_init = False
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

    @property
    def timeout(self):
        """Get timeout."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Set timeout."""
        self._timeout = timeout
        self.serial_connection.timeout = timeout

    def connect(self):
        """Connect to the RS-232 serial port."""
        self.serial_connection = serial.Serial(
            port=self.serial_port,
            baudrate=self.baud_rate,
            # number of write_data bits
            bytesize=8,
            parity=self.parity,
            stopbits=1,
            # don't enable software flow control
            xonxoff=False,
            # don't enable RTS/CTS flow control
            rtscts=False,
            # 
            dsrdtr=False,
            # set a timeout value, None for waiting forever
            timeout=self.timeout,
        )

    def write(self, *args, **kwargs):
        """Write the given data to the serial connection."""
        return self.serial_connection.write(*args, **kwargs)

    def read(self, *args, **kwargs):
        """Read the given amount of bytes from the serial connection."""
        return self.serial_connection.read(*args, **kwargs)

    def enable_reset(self, enable=True):
        """Enable or disable the reset IO line."""
        # by default reset is active low
        if not self._gpio_reset_init:
            GPIO.setup(self._gpio_reset_pin, GPIO.OUT)
            self._gpio_reset_init = True

        if self.reset_active_high:
        	level = (GPIO.HIGH if enable else GPIO.LOW)  # active HIGH
        else:
        	level = (GPIO.LOW if enable else GPIO.HIGH)  # active LOW
        GPIO.output(self._gpio_reset_pin, level)

    def enable_boot0(self, enable=True):
        """Enable or disable the boot0 IO line."""
        # by default boot0 is active high
        if not self._gpio_boot0_init:
            GPIO.setup(self._gpio_boot0_pin, GPIO.OUT)
            self._gpio_boot0_init = True

        if self.boot0_active_low:
        	level = (GPIO.LOW if enable else GPIO.HIGH)  # active LOW
        else:
        	level = (GPIO.HIGH if enable else GPIO.LOW)  # active HIGH
        GPIO.output(self._gpio_boot0_pin, level)
