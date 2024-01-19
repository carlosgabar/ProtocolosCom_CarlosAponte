import time
from machine import Pin,I2C
from i2cSlave import i2c_slave
from ssd1306 import SSD1306_I2C

WIDTH=128
HEIGHT=64

i2c=I2C(1,scl=Pin(15),sda=Pin(14),freq=400000) 

oled=SSD1306_I2C(WIDTH,HEIGHT,i2c) 

i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=1000000)
s_i2c = i2c_slave(0,sda=0,scl=1,slaveAddress=0x41)
data_list=[]
datos=[]
nuevalistafloat=[]

try:
    while True:
    
        data = s_i2c.get()
        if chr(data)=="x":
            break

        data_list.append(chr(data))
       
        
except KeyboardInterrupt:
    pass

nueva_lista=[]
for i in range(0,len(data_list),5):
    nueva_lista.append("".join(data_list[i:i+5]))
    
nuevalistafloat = [float(dato) for dato in nueva_lista]  
print(nuevalistafloat)

if len(nuevalistafloat)!=0:
    
    maximo=max(nuevalistafloat)

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
            
    for k in range(len(nuevalistafloat)):
        
        oled.fill_rect(0,0,128,14,0)
        oled.text(str(nuevalistafloat[k])+"C",50,0)        
        if X<120:
            X = 8 + (k + 1) * 8
    
            Y = int(64-48*nuevalistafloat[k]*ratio/100)
                
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
            oled.text(str(nuevalistafloat[k])+"C",50,0)  
            
                    
        oled.rect(X, Y, 7, 63 - Y, 1, True)
       
        oled.show()
        time.sleep(1)
       
