# --- spi_slave.py - 17.10.2021
#
#     Ein SPI-Slave, der genau 1-8 Words (je 32-Bit) erwartet
#     und genau die gleiche Anzahl von Bits zurücksendet.
#     Die Anzahl der Words wird festgelegt mit dem Parameter "spi_words".
#     Die empfangenen Daten konnen ausgelesen werden (müssen nicht),
#     aber es müssen nach jeder Sendeung wieder die gleiche Anzahl Words
#     in die TX-Fifos transferiert werden - sonst blockt der Transmitter !

from machine import Pin
from micropython import const
import uarray as arr
from rp2 import PIO, StateMachine, asm_pio

EMPTY_WORD = const(0xAAAA_AAAA)  # wird als Platzhalter für leere Daten verwendet

# --- csel ---------------------------------------------

# Hilfsfunktion, die Anfang und Ende der Übertragung
# anhand des Pegels von Chip-Select erkennt.
# An der fallenden Flanke werden die Statemachines sm1 und sm2
# freigegeben, an der steigenden Flanke wird ein Interrupt ausgelöst,
# der das Einlesen der RX-Daten und das Nachfüllen des TX-Buffers auslöst.
@asm_pio()

def _csel():    
    wrap_target()
    
    wait(0, pin, 0)    # 1 Warten auf fallende Flanke Chip-Select
    irq(4)             # 2 Starten des SPI-Slave
    irq(5)
    wait(1, pin, 0)    # 3 warten auf steigende Flanke Chip Select
    irq(rel(0))        # 4 Interrupt wenn Clock-Sel auf high geht
    
    wrap()

# ---- SPI-Read/ ----------------------------------------------

@asm_pio(fifo_join=PIO.JOIN_RX, autopush=True, push_thresh=32)

def _spi_in():                       
                        #     Nach einem restart() gehts hier los
    wait(1, irq, 4)     #   1 warten auf irq für csel = LOW
    wrap_target()
 
    wait(0, pin, 1)     #   2 warten auf clk, falling edge
    wait(1, pin, 1)     #   3 warten auf clk, rising edge
    in_(pins, 1)        #   4 mosi

    wrap()
    
# ---- SPI-Write ----------------------------------------------

@asm_pio(out_init=PIO.OUT_HIGH, fifo_join=PIO.JOIN_TX,
    out_shiftdir=PIO.SHIFT_LEFT, autopull=True, pull_thresh=32)

def _spi_out():
                        #  Im Reguster Y steht die Anzahl der
                        #  zu übertragenden Bits - 1
                        #  Y wird bei der Initialisierung geschreiben
    wrap_target()
    mov(x, y)           #  1 127 nach X laden
    
    wait(1, irq, 5)     #  2 warten auf irq für csel = LOW
    label("next")
 
    wait(0, pin, 0)     #  3 warten auf clk, falling edge
    out(pins, 1)        #  4 miso
    wait(1, pin, 0)     #  5 warten auf clk, rising edge

    jmp(x_dec, "next")  #  6
    irq(rel(0))         #  7 Interrupt am Ende der Übertragung
    
    wrap()

# ----------------------------------------------------------

class SPI_Slave(object):
    def __init__(self, mosi, miso, sck, csel, spi_words=4, F_PIO=60_000_000):
        if not (spi_words > 0 and spi_words < 9):
            raise ValueError("spi-Words must in [1...8], is {} !".format(spi_word))
        self.sm0 = StateMachine(0, _csel,
            in_base=Pin(csel, Pin.IN, Pin.PULL_UP), freq=F_PIO)

        self.sm0.restart()
        self.sm0.active(1)
        self.sm0.irq(self.irq_handler_1)

        self.sm1 = StateMachine(1, _spi_in,
            in_base=Pin(mosi, Pin.IN, Pin.PULL_UP), freq=F_PIO)

        self.sm1.restart()
        self.sm1.active(1)
 
        self.sm2 = StateMachine(2, _spi_out, out_base=Pin(miso),
            in_base=Pin(sck, Pin.IN, Pin.PULL_UP), freq=F_PIO)
        
        # Ins Y-Register die Anzahl der zu (übertrgenden Bits - 1) schreiben
        self.sm2.put(spi_words * 32 - 1)
        self.sm2.exec("pull()")
        self.sm2.exec("mov(y, osr)")
        self.sm2.restart()
        self.sm2.irq(self.irq_handler_2)
        self.sm2.active(1)

        self.rx_data = arr.array("I", [0] * spi_words)
        self.tx_data = arr.array("I", [0] * spi_words)
        
        self.SPI_WORDS = const(spi_words)
        self.irq_flag = 0
        
        self.__clear_fifos()
        
        # Die TX-Fitos mit der Signatur für leere Daten initialisieren
        for _ in range(spi_words):
            self.sm2.put(EMPTY_WORD)

    @micropython.native
    def irq_handler_1(self, _):
        # IRQ-Handler, wird aufgerufen, wenn eine Übertragung beendet ist,
        # was an der steigenden Flanke des Chip-Select Signals erkannt wird.
        self.irq_flag = True
    
    @micropython.native
    def irq_handler_2(self, _):
        # IRQ-Handler, wird aufgerufen, wenn alle Bits geschrieben sind.
        self.irq_flag = True
        
    @micropython.native
    def received(self):
        # liest eingeangene Words aus den RX-Ffos in das Array rx_data[] ein.
         
        if not self.irq_flag:
            return False
        else:
            cnt = self.sm1.rx_fifo()
            if cnt > self.SPI_WORDS:
                # Mögkicherweise ist mehrfach gesendet bzw. der PUffer noch nicht ausgelesen ???
                raise IndexError("Expecting {} Words, got {} !".format(self.SPI_WORDS, cnt))
            if cnt:
                for i in range(cnt):
                    self.rx_data[i] = self.sm1.get()
                self.irq_flag = False
                return True
            
            else:
                # wenn keine Daten empfangen wurden, dann hat nur der IRQ von sm0 ausgelöst
                # Chip-Select hat wurde erkannt, aber es sind keine oder zu wenig Daten empfangen
                self.sm1.restart()
                self.sm2.restart()
                self.irq_flag = False
                return False
            
    @micropython.native          
    def rx_words(self):
        # Referenz auf Array mit den empfangenen Words zurückgeben
        return self.rx_data
    
    @micropython.native
    def tx_words(self):
        # Referenz auf das Array mit den zu sendenden Words zurückgeben
        return self.tx_data
 
    @micropython.native
    def __clear_fifos(self):
        # Die Fifo-Register zurücksetzen
        for _ in range(self.sm2.tx_fifo()):
            self.sm2.exec("out(null, 32)")
            self.sm2.exec("pull()")
        self.sm2.restart()
        
        for _ in range(self.sm1.rx_fifo()):
            self.sm1.get()
         
    @micropython.native
    def put_words(self, data = None):
        # schreibt das Array rx_data[] in die TX-Fifos
        # das muss geschehen sein, bevor die nächste SPI-Transaktion
        # gestartet wird - sonst blockt der SPI-Slave
        # Wenn icht die Daten in Ttx_data versandt werdeen sollen, kann alternativ
        # die Referenz auf ein beliebiges Array als Parameter übergeben werden
        
        if data is not None:
            #print(type(data))
            if not type(data) in (tuple, list, bytearray, arr.array):
                raise ValueError("unsupported Type {}".format(type(data)))
            if not len(data) == self.SPI_WORDS:
                raise ValueError("Len({}) must be {}, is {} !".format(data, self.SPI_WORDS, len(data)))
        else:
            data = self.tx_data

        if self.sm2.tx_fifo():
            self.__clear_fifos()
        for i in range(self.SPI_WORDS):
            self.sm2.put(data[i])

# ---------------------------------------------------
if __name__ == "__main__":
     print("Modul is: 'spi_slave.py'")
