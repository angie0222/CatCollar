import spidev
import time
from gpiozero import OutputDevice


D_SEL2_PIN = 23
D_SEL1_PIN = 24
CS = 8

# SPI settings
spi_bus = 0  # SPI bus 0
spi_device = 0  # SPI device (CS) 0
spi_speed = 1000000  # 1 MHz

# Initialize SPI
spi = spidev.SpiDev()
spi.open(spi_bus, spi_device)
spi.max_speed_hz = spi_speed


try:
    spi.xfer2([0x01])
    time.sleep(0.001)
    while True:
        # Data to send (example: incrementing byte)
        data_to_send = [0x06, 0x00]

        spi.writebytes2(data_to_send)
        time.sleep(0.001)
        received_data = spi.readbytes(4)
        # Send and receive data
        #received_data = spi.xfer3(data_to_send, spi_speed, 1000, 32)
        #GPIO.output(CS, GPIO.HIGH)
        #time.sleep(1)

        # Print sent and received data 
        my_list = [10, 'hello', 3.14, 255, 42]
        received_data = [hex(item) if isinstance(item, int) else item for item in received_data]

        print(f"Sent: {data_to_send}, Received: {received_data}")

        # Wait before sending again
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    spi.close()
