import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 1)
spi.max_speed_hz = 250000
spi.mode = 0b00

RS_CMD = 0x06
RD_CMD = 0x81
WR_CMD = 0x0E
PWON_CMD = 0x04
MAX_ERROR_NUMBER = 100
FAIL_MAX_TIME = 5
SPI_MAX_BUFF_LENGTH = 0x1000
CFG_RD_CMD = 0x0A
CFG_WR_CMD = 0x0C
WS_CMD = 0x08
PWOFF_CMD = 0x02
SLAVE_TX_LEN_REG = 0x08
SLAVE_TX_BUF_REG = 0x2000
SLAVE_RX_LEN_REG = 0x04
SLAVE_RX_BUF_REG = 0x1000
          
def check_spi_response(CMD, bytes):
    # Send RS_CMD followed by dummy byte
    tx = [CMD]
    for byte in bytes:
        tx += bytes[byte]

    rx = spi.xfer3(tx, 16)
    time.sleep(0.1)
    print(f"TX: {tx} RX: {rx}")
    return rx

print("Checking LC29HBSMD SPI status...")

try:
    spi.xfer2([PWON_CMD])
    while True:
        response = check_spi_response(RS_CMD, [0x00])
        if response[1] != 0xFF:
            print("LC29H SPI active. Response:", hex(response[1]))
            if response[1] == 0x1:
                print("LC29H STA_SLV_ON is on: ", hex(response[1]))
                write_rd_cmd = check_spi_response(CFG_RD_CMD, [SLAVE_TX_LEN_REG, 0x00000003])
                send_rs_cmd = check_spi_response(RS_CMD, [0x00])
                if send_rs_cmd[1] == 0x4:
                    print("----!!Error!!----")
            if response[1] == 0x8 or response[1] == 0x10:
                print("LC29H STA_ERROR!!!")

        else:
            print("No response or SPI not ready (0xFF).", hex(response[1]))
        time.sleep(1)
except KeyboardInterrupt:
    print("Done.")
finally:
    spi.close()

