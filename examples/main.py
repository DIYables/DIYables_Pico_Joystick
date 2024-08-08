from DIYables_Pico_Joystick import Joystick
import time

# Initialize the joystick with the corresponding pins for X, Y, and button
joystick = Joystick(pin_x=26, pin_y=27, pin_button=22)

# Configure the debounce time if necessary (default is 50ms)
joystick.set_debounce_time(100)  # debounce time set to 100 milliseconds

while True:
    joystick.loop()  # Must be called frequently to process button debouncing

    # Read the analog values from the X and Y axes
    x_value = joystick.read_x()
    y_value = joystick.read_y()
    press_count = joystick.get_press_count()

    # Check if the button has been pressed or released
    if joystick.is_pressed():
        print("Button Pressed")
    if joystick.is_released():
        print("Button Released")

    # Print the joystick's X and Y coordinates, and pressed count
    print(f'Joystick Position - X: {x_value}, Y: {y_value}, pressed count: {press_count}')

    time.sleep(0.05)  # Delay to reduce the output frequency

