# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 17:36:07 2020

@author: belu
"""

import RPi.GPIO as GPIO
import MPU9250
from programa2 import motorNorte
from programa2 import reorientacion
from programa2 import inicializacionPines
import time
import sys

## Setup
pines = [11,12,13,15]
inicializacionPines(pines)

def MotorMPU(angAzim, anteultimo, x_m, y_m, z_m, pines):
    
    variacion = abs(anteultimo-angAzim)
    if  variacion >= 4:
        #Muevo al motor lo que corresponde                    
        motorNorte(angAzim, anteultimo, pines)
    
        #Se fija que efectivamente se movio al lugar indicado
        posicion_nueva = reorientacion(x_m, y_m, z_m) 
        desplazamiento = abs(posicion_nueva-angAzim)
        print("desplazamiento: ", desplazamiento)
        
        
        #Si el motor no llego a la posicion deseada lo mueve otra vez
        while desplazamiento > 4:
             motorNorte(angAzim, posicion_nueva, pines)   
             posicion_nueva = reorientacion(x_m, y_m, z_m)
             desplazamiento = abs(posicion_nueva-angAzim)
             print('desplazamiento: ', desplazamiento)
        anteultimo = posicion_nueva
        print("termine")
        
                        
    #Si la variacion es menor a 3 grados, pasa.
    else:
        pass
    return anteultimo

if __name__ == "__main__":
    ## Setup
    mpu9250 = MPU9250.MPU9250()
    pines = [11,12,13,15]
    inicializacionPines(pines)
    MotorMPU(150, 16, -1.404735135135135, 31.219810810810806, -37.1886, pines)
