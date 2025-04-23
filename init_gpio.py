import gpiod
import time

# Define the chip and CS pin
chip = gpiod.Chip("gpiochip0")
d1 = chip.get_line(24)  # Replace 21 with your actual CS pin
d2 = chip.get_line(23)  # Replace 21 with your actual CS pin
# Enable CS output

d1.request(consumer="D1", type=gpiod.LINE_REQ_DIR_OUT)
d2.request(consumer="D2", type=gpiod.LINE_REQ_DIR_OUT)

d1.set_value(1)
d2.set_value(0)

