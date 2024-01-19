from machine import Pin, SPI, UART
from sdcard import SDCard
from uos import VfsFat, mount
from os import listdir
import onewire, ds18x20
import time
import os
import sdcard
import uos

cs = machine.Pin(5, machine.Pin.OUT)

spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
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
    
pinsensor= Pin(16)
 
sensor = ds18x20.DS18X20(onewire.OneWire(pinsensor))
 
direccion = sensor.scan()

uart = UART(0, baudrate=100000, tx=Pin(0), rx=Pin(1))

datos = []
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
            
        suma = sum(datos)
        cantidad_elementos = len(datos)
        promedio = suma / cantidad_elementos
        promedio=round(promedio,2)
        datoconvertido=str(promedio)
        datost.append(datoconvertido)
    
for dato in datost:
    uart.write(str(dato))
    print("Valor enviado: " + str(dato))
    time.sleep(1)


