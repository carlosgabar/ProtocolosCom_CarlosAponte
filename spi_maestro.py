from spi_master import SPI_Master
from machine import Pin, SPI, I2C
from sdcard import SDCard
from uos import VfsFat, mount
from os import listdir
import array
import sdcard
import uos
import os
from time import sleep

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

master = SPI_Master(mosi_pin=11, miso_pin=12, sck_pin=10, csel_pin=13, spi_words=1, F_SPI=1_000_000)

datost = []
contenido=[]

for ruta in os.listdir("/sd"):
   
    if ruta[:4] == "2023":
        with open("/sd/"+ruta, "r") as file:
            for linea in file:
                contenido.append(linea.strip())

        obtenerdato=[elemento.split(":")[1] for elemento in contenido]
   
        if len(obtenerdato)!=0:
            datos = [float(dato) for dato in obtenerdato]
          
        suma = sum(datos)
        cantidad_elementos = len(datos)
        promedio = suma / cantidad_elementos
        promedio=round(promedio,2)
        promedio=promedio*100
        promedio=int(promedio)
        datoconvertido=str(promedio)
        datost.append(promedio)
        
for dato in datost:
    paquete = array.array("I", [int("0x"+"{:04d}".format(dato).encode("utf-8").hex())])
    master.write(paquete)
    print("Data:", dato)
    sleep(0.1)
    
paquete = array.array("I", [int("0x"+"X".encode("utf-8").hex())])
master.write(paquete)


