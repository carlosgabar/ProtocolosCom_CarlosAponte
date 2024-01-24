# --- spi_master.py -- 17.10.2021
#
# SPI-Master zum Testen des asm_pio SPI-Slaves

from machine import SPI, Pin
from micropython import const
import uarray as arr
import time

EMPTY_BYTE = const(0xAA)    # wird zu EMPTY_WORD 0xAAAA_AAAA erweitert

# ----- SPI-Master ---------------------------------------

class SPI_Master(object):
    def __init__(self, mosi_pin, miso_pin, sck_pin, csel_pin,
                 id=0, spi_words=4, F_SPI=4_000_000):
        
        if not (spi_words > 0 and spi_words < 9):
            raise ValueError("spi_words must in [1...8], is {} !".format(spi_words))
        self.spi = SPI(id=1, baudrate=F_SPI,
              miso=Pin(miso_pin),
              sck=Pin(sck_pin),
              mosi=Pin(mosi_pin),
              polarity=1, phase=1, firstbit=SPI.MSB)
        self.read_buffer  = arr.array("B", [0] * spi_words * 4)
        self.write_buffer = arr.array("B", [0] * spi_words * 4)
        self.tmp = self.write_buffer
        self.recv_words   = arr.array("I", [0] * spi_words)
        self.SPI_WORDS    = const(spi_words)
        self.SPI_BYTES    = const(spi_words * 4)
 
        # Chip_Select
        self.csel = Pin(csel_pin, Pin.OUT, Pin.PULL_UP)
        self.csel.on()
    
    @micropython.native
    def read(self):
        # Der Master schreibt als Platzhalter "0xAA"
        # und liest Daten vom SPI-Slave ein
        for i in range(self.SPI_BYTES):
            self.write_buffer[i] = EMPTY_BYTE
        self.tmp = self.write_buffer
        self.__spi_write()
        
    @micropython.native
    def write(self, data):
        # Der Master schreibt die übergebenen Daten raus
        # und liest eine gleiche Anzahl von Bytes ein.
        if not type(data) in (arr.array, list, bytearray):
            raise ValueError("unsupported type {} !".format(type(data)))
        
        if len(data) == self.SPI_WORDS:
            for i in range(self.SPI_WORDS):
                 for j in range(3, -1, -1):
                    self.write_buffer[i * 4 + j] =  data[i] & 0xFF
                    data[i] >>= 8
            self.tmp = self.write_buffer

        elif len(data) == self.SPI_BYTES:
            self.tmp = data
        else:
            raise ValueError("Type {}, Len({}) must be {} or {}, is {} !".format(
                type(data), data, self.spi_words, self.spi_words * 4, len(data)))
        self.__spi_write()
        
    @micropython.native
    def __spi_write(self):
        self.csel.off()        # Chip-Select auf low
        self.spi.write_readinto(self.tmp, self.read_buffer)  
        self.csel.on()
    
    @micropython.native
    def rx_bytes(self):
        # Gibt eine Referenz auf den das Array read_buffer[] -> Bytes zurück 
        return self.read_buffer
    
    @micropython.native
    def rx_words(self):
        # gibt eine Referenz auf das Array recv_words[] -> Words zurück
        # Jeweils 4 Bytes zu Words zusammenfassen
        for i in range(self.SPI_WORDS):
            for j in range(4):
                self.recv_words[i] <<= 8
                self.recv_words[i] |= self.read_buffer[i * 4 + j]      
        return self.recv_words
    
if __name__ == "__main__":
    print("Modul is: 'spi_master.py'")
