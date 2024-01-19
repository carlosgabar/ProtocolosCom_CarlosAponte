from spi_slave import SPI_Slave
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import time
     
WIDTH=128
HEIGHT=64
i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq=400000)
oled = SSD1306_I2C(WIDTH, HEIGHT,i2c)


def Leer_SPI():
    read = slave.rx_words()
    write = slave.tx_words()
    write[0] = read[0]
    
    try:
        dato = read[0].to_bytes(4, "big").decode("utf-8")
    except:
        return ""
    
    slave.put_words()
    
    return dato

slave = SPI_Slave(csel=28, mosi=26, sck=27, miso=22, spi_words=1, F_PIO=10_000_000)
slave.put_words()


datos = []

inicio = Pin(13,Pin.OUT)
inicio.value(1)
inicio.value(0)

while True:
     if slave.received():
        dato = Leer_SPI()
        
        if dato == "X":
            break
        
        print("Valor recibido:",int(dato)
        datonuevo=(int(dato))/100
        datos.append(datonuevo)
                         
if len(datos)!=0:
    
    maximo=max(datos)

    if not maximo==0:
        ratio=100/maximo
    else:
        ratio=0
        
    oled.line(16,43,128,43,1)
    oled.line(16,55,128,55,1)
    oled.line(16,29,128,29,1)
    oled.line(16,16,128,16,1)
    oled.line(16,16,16,63,1)
    oled.fill_rect(0,8,16,64,0)
    oled.text("{medio:02d}".format(medio=int(maximo/2)),0,36)
    oled.text("{max:02d}".format(max=int(maximo)),0,16)
    oled.show()
    
    X=0
   
    for k in range(len(datos)):
        oled.fill_rect(0,0,128,14,0)
        oled.text(str(datos[k]),50,0)
        if X<120:
            X = 8 + (k + 1) * 8
    
            Y = int(64-48*datos[k]*ratio/100)
                
        if X>=120:
            print(X)
                    
            X=112
                    
            oled.fill_rect(0,16,24,63,0)
            oled.fill_rect(0,0,128,14,0)
            oled.scroll(-8,0)
            oled.line(16,43,128,43,1)
            oled.line(16,55,128,55,1)
            oled.line(16,29,128,29,1)
            oled.line(16,16,128,16,1)
            oled.line(16,16,16,63,1)
            oled.text("{medio:02d}".format(medio=int(maximo/2)),0,36)
            oled.text("{max:02d}".format(max=int(maximo)),0,16)
            oled.text(str(datos[k])+"C",50,0)
            
                    
        oled.rect(X, Y, 7, 63 - Y, 1, True)
       
        oled.show()
        time.sleep(1)
       