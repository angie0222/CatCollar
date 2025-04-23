import spidev
import time

# SPI Commands
PWON_CMD = 0x04
RS_CMD = 0x06
CFG_RD_CMD = 0x0A
RD_CMD = 0x81
CFG_WR_CMD = 0x0C
WR_CMD = 0x0E

# Registers
SLAVE_TX_LEN_REG = 0x00000008
SLAVE_TX_BUF_REG = 0x00002000
SLAVE_RX_LEN_REG = 0x00000004
SLAVE_RX_BUF_REG = 0x00001000

# Status Flags
STA_SLV_ON = 0x01
STA_TXRX_FIFO_RDY = 0x04
STA_RDWR_FINISH = 0x20

class LC29H_SPI:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Use CE0
        self.spi.max_speed_hz = 1000000  # Start with 1MHz
        self.spi.mode = 0b00  # SPI Mode 0
        
        # Initialize module
        self.power_on()

    def power_on(self):
        """Send power on command and verify status"""
        self.spi.xfer2([PWON_CMD])
        time.sleep(0.01)
        
        retries = 10
        while retries > 0:
            status = self.read_status()
            if status & STA_SLV_ON:
                return True
            time.sleep(0.01)
            retries -= 1
        raise Exception("Failed to power on SPI interface")

    def read_status(self):
        """Read status register"""
        resp = self.spi.xfer2([RS_CMD, 0x00])
        time.sleep(0.001)  # 1ms delay
        return resp[1]

    def read_data(self):
        """Read available data from module"""
        # Step 1: Read available data length
        self._send_cfg_read(SLAVE_TX_LEN_REG, 4)
        
        # Check FIFO ready status
        if not self._wait_status(STA_TXRX_FIFO_RDY):
            return b''
            
        # Read data length
        length_bytes = self.spi.xfer2([RD_CMD] + [0]*4)[1:5]
        data_length = int.from_bytes(length_bytes, 'little')
        
        if data_length == 0:
            return b''
            
        # Step 2: Read actual data
        self._send_cfg_read(SLAVE_TX_BUF_REG, data_length)
        
        if not self._wait_status(STA_TXRX_FIFO_RDY):
            return b''
            
        # Read data
        dummy = [0]*(data_length + 1)
        resp = self.spi.xfer2([RD_CMD] + dummy)
        return bytes(resp[1:data_length+1])

    def write_data(self, data):
        """Write data to module"""
        # Step 1: Get free space
        self._send_cfg_read(SLAVE_RX_LEN_REG, 4)
        
        if not self._wait_status(STA_TXRX_FIFO_RDY):
            return False
            
        # Read free space
        free_bytes = self.spi.xfer2([RD_CMD] + [0]*4)[1:5]
        free_space = int.from_bytes(free_bytes, 'little')
        
        if free_space < len(data):
            return False
            
        # Step 2: Write data
        self._send_cfg_write(SLAVE_RX_BUF_REG, len(data))
        
        if not self._wait_status(STA_TXRX_FIFO_RDY):
            return False
            
        # Send write command + data
        self.spi.xfer2([WR_CMD] + list(data))
        return self._wait_status(STA_RDWR_FINISH)

    def _send_cfg_read(self, reg, length):
        """Helper to send CFG_RD_CMD"""
        cmd = [CFG_RD_CMD]
        cmd += list(reg.to_bytes(4, 'little'))
        cmd += list((length - 1).to_bytes(4, 'little'))
        self.spi.xfer2(cmd)

    def _send_cfg_write(self, reg, length):
        """Helper to send CFG_WR_CMD"""
        cmd = [CFG_WR_CMD]
        cmd += list(reg.to_bytes(4, 'little'))
        cmd += list((length - 1).to_bytes(4, 'little'))
        self.spi.xfer2(cmd)

    def _wait_status(self, flag, timeout=100):
        """Wait for specific status flag"""
        for _ in range(timeout):
            status = self.read_status()
            if status & flag:
                return True
            time.sleep(0.001)
        return False

# Example usage
if __name__ == "__main__":
    gps = LC29H_SPI()
    
    while True:
        # Read NMEA data
        data = gps.read_data()
        if data:
            print("Received:", data.decode())
        
        # Example write (send PMTK command)
        # gps.write_data(b'$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n')
        
        time.sleep(1)