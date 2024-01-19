from machine import Pin,I2C
import sdcard
import uos
import machine
import os
import time

cs = machine.Pin(5, machine.Pin.OUT)

spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  #bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))


sd = sdcard.SDCard(spi, cs)

vol = uos.VfsFat(sd)
uos.mount(vol, "/sd")

file_list = uos.listdir("/sd")
for file_name in file_list:
    print(file_name)
    
i2c=I2C(0,scl=Pin(1),sda=Pin(0),freq=1000000)
print(i2c.scan())
device_address = 0x41

datost=[]
contenido=[]

for ruta in os.listdir("/sd"):
  
    if ruta[:4]=="2023":
 
        with open("/sd/"+ruta, "r") as file:
            for linea in file:
                contenido.append(linea.strip())

        obtenerdato=[elemento.split(":")[1] for elemento in contenido]
    

        if len(obtenerdato)!=0:
            datos = [float(dato) for dato in obtenerdato]
            print(datos)
            
        cont=cont+1
        
        suma = sum(datos)
        cantidad_elementos = len(datos)
        promedio = suma / cantidad_elementos
        promedio=round(promedio,2)
        datoconvertido=str(promedio)
        datost.append(datoconvertido)

print(datost)

for dato in datost:
   
    byte_array = bytearray(str(dato),"utf-8")
    print(byte_array)
    i2c.writeto(device_address,byte_array)
    time.sleep(1)

enviar="x"
enviar=bytearray(enviar,"utf-8")
i2c.writeto(device_address, enviar)
print("listo")
        