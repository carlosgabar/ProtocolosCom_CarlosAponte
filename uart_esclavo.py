from machine import Pin, I2C, UART
from ssd1306 import SSD1306_I2C
from time import localtime
import time

uart = UART(0, baudrate=100000, tx=Pin(0), rx=Pin(1),timeout=1)

WIDTH=128
HEIGHT=64
i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq=400000)
oled = SSD1306_I2C(WIDTH, HEIGHT,i2c)

datos = []
cont=0
while True:
    if uart.any():
        data = str(uart.readline(), 'utf-8')
        print("Data", data)

        data=float(data)
        data=round(data,2)
        datos.append(float(data))
        
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
                oled.text("Temp N:{}".format(cont),0,0)
                oled.text(str(data),74, 0)
                if X<120:
                    X = 8 + (k + 1) * 8
    
                Y = int(64-48*datos[k]*ratio/100)
                
                if X>=120:
                  
                    X=112
                    
                    oled.fill_rect(0,16,24,63,0)
                    oled.scroll(-8,0)
                    oled.line(16,43,128,43,1)
                    oled.line(16,55,128,55,1)
                    oled.line(16,29,128,29,1)
                    oled.line(16,16,128,16,1)
                    oled.line(16,16,16,63,1)
                    oled.fill_rect(0,8,16,64,0)
                    oled.text("{medio:02d}".format(medio=int(maximo/2)),0,36)
                    oled.text("{max:02d}".format(max=int(maximo)),0,16)
            
                    
                oled.rect(X, Y, 7, 63 - Y, 1, True)
       
                oled.show()
                time.sleep(1)
        
            cont=cont+1
        