"""
This MicroPython library is designed for Raspberry Pi Pico to make it easy to use with joystick

It is created by DIYables to work with DIYables products, but also work with products from other brands. Please consider purchasing products from [DIYables Store on Amazon](https://amazon.com/diyables) from to support our work.

Product Link:
- Joystick: https://diyables.io/products/joystick
- Sensor Kit: https://diyables.io/products/sensor-kit


Copyright (c) 2024, DIYables.io. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

- Neither the name of the DIYables.io nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY DIYABLES.IO "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL DIYABLES.IO BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""


from machine import Pin, ADC
import time

class Joystick:
    def __init__(self, pin_x, pin_y, pin_button, mode=Pin.PULL_UP):
        # Initialize the button
        self.btn_pin = Pin(pin_button, Pin.IN, mode)
        self.mode = mode
        self.debounce_time = 0
        self.count = 0
        self.count_mode = 'COUNT_FALLING'
        
        # Set initial state based on pull mode
        if self.mode == Pin.PULL_DOWN:
            self.unpressed_state = 0
            self.pressed_state = 1
        else:
            self.unpressed_state = 1
            self.pressed_state = 0
        
        self.previous_steady_state = self.btn_pin.value()
        self.last_steady_state = self.previous_steady_state
        self.last_flickerable_state = self.previous_steady_state
        self.last_debounce_time = 0

        # Initialize ADC for X and Y axes if pins are provided
        if pin_x is not None:
            self.adc_x = ADC(Pin(pin_x))
        if pin_y is not None:
            self.adc_y = ADC(Pin(pin_y))

    def set_debounce_time(self, time_ms):
        self.debounce_time = time_ms

    def read_button_state(self):
        return self.last_steady_state

    def is_pressed(self):
        return self.previous_steady_state == self.unpressed_state and self.last_steady_state == self.pressed_state

    def is_released(self):
        return self.previous_steady_state == self.pressed_state and self.last_steady_state == self.unpressed_state

    def set_press_count_mode(self, mode):
        if mode in ['COUNT_BOTH', 'COUNT_FALLING', 'COUNT_RISING']:
            self.count_mode = mode

    def get_press_count(self):
        return self.count

    def reset_press_count(self):
        self.count = 0

    def read_x(self):
        if hasattr(self, 'adc_x'):
            return self.adc_x.read_u16() >> 4  # Shift the bits right by 4, this is to convert back to 12-bit ADC of Pico
        else:
            return None

    def read_y(self):
        if hasattr(self, 'adc_y'):
            return self.adc_y.read_u16() >> 4  # Shift the bits right by 4, this is to convert back to 12-bit ADC of Pico
        else:
            return None

    def loop(self):
        current_state = self.btn_pin.value()
        current_time = time.ticks_ms()

        if current_state != self.last_flickerable_state:
            self.last_debounce_time = current_time
            self.last_flickerable_state = current_state

        if time.ticks_diff(current_time, self.last_debounce_time) >= self.debounce_time:
            self.previous_steady_state = self.last_steady_state
            self.last_steady_state = current_state

        if self.previous_steady_state != self.last_steady_state:
            if self.count_mode == 'COUNT_BOTH':
                self.count += 1
            elif (self.count_mode == 'COUNT_FALLING' and
                  self.previous_steady_state == self.pressed_state and
                  self.last_steady_state == self.unpressed_state):
                self.count += 1
            elif (self.count_mode == 'COUNT_RISING' and
                  self.previous_steady_state == self.unpressed_state and
                  self.last_steady_state == self.pressed_state):
                self.count += 1

