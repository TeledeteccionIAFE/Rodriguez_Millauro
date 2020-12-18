import numpy as np
import RPi.GPIO as GPIO
import MPU9250
import sys
import serial, time
import re

mpu9250 = MPU9250.MPU9250()

#Correcion sobre grados calculados
def trunc(entrada):
    flot = entrada - int(entrada)
    if flot < 0.5:
        salida = int(entrada)
    elif flot >= 0.5:
        salida = int(entrada) + 1
    return salida


def reorientacion():
    cantidad = 0
    x, y, z = [], [], []
    while cantidad < 10: 
        # leo el magnetometro
        mag = mpu9250.readMagnet()

        x.append(mag[0])   #Intensidad del campo en cada eje
        y.append(mag[1])
        z.append(mag[2])	
        cantidad = cantidad + 1
        time.sleep(0.01)

    print("Resultados (microTesla):")

    mean_x =np.mean(x)
    mean_y =np.mean(y)
    print(mean_x,mean_y)
    print("Midiendo posicion relativa al norte")

    import math
    fi_rad = math.atan(mean_x/mean_y)
    fi_grad_1 = fi_rad*180/math.pi     
    if mean_x < 0:
        if mean_y> 0:
            fi_grad = fi_grad_1
        if mean_y < 0:
            fi_grad = fi_grad_1-180
    if mean_x > 0:
        if mean_y  < 0:
            fi_grad = fi_grad_1+180
        if mean_y > 0:
            fi_grad = fi_grad_1

    print("El norte esta a ", str(round(fi_grad)), "° respecto del eje x del IMU")

    return trunc(fi_grad)

def inicializacionPines(pines):
    #Motor paso a paso pines
    GPIO.setmode(GPIO.BOARD)

    # Declaro los pines
    for pin in pines:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)    # inicializo en cero

def motorNorte(angSat, angAct, pines):

    unidad = 512/360
    deltaGrado = angSat - angAct    
    grado = trunc(deltaGrado * unidad)

    if deltaGrado  < 0: #Si el satelite se movio positivamente
        print("llamo a motor, estado 2")
        motor(2, abs(grado), pines)        

    elif deltaGrado > 0: #Si el satelite se movio negativamente
        motor(3, abs(grado), pines)        
        print("llamo a motor, estado 2")
    time.sleep(3)
    print('Reorientando...')


def motor(estado, pasos, pines):
    inicializacionPines(pines)
    secuencia = [           
        [1,1,0,0],          # Matriz de encendido
        [0,1,1,0],
        [0,0,1,1],
        [1,0,0,1]
    ]

    print("Estado: ")
    print(estado)
    print("- Cantidad de pasos: ")
    print(pasos)
    print("\n")

    #estado 2: muevo el motor de forma positiva
    if estado == 2:        
        if pasos > 0:
            for i in range(pasos):
                for j in range(4):              # Encendido de bobina por bloques de pares
                    for pin in range(4):        # para maximizar el torque
                        GPIO.output(pines[pin], secuencia[j][pin])  
                    time.sleep(0.01)
	

            for pin in pines:                  # Apagado de todos los campos
                GPIO.output(pin, 0)           # para reducir consumo
            time.sleep(0.1)
            GPIO.cleanup()
	        
    #estado 3: muevo el motor de forma negativa
    elif estado == 3:	
        if pasos > 0:
            for i in range(pasos):
                for j in range(4):              # Encendido de bobina por bloques de pares
                    for pin in range(4):        # para maximizar el torque
                        GPIO.output(pines[3-pin], secuencia[j][pin])  
                    time.sleep(0.01)          
	       
            for pin in pines:                  # Apagado de todos los campos
                GPIO.output(pin, 0)           # para reducir consumo
            time.sleep(0.1)
            GPIO.cleanup()
    else:
        print("\n")
        print("Error, no esta definido el estado")
        print("\n")
	    

    time.sleep(0.001)         #Espera un milisegundo antes de recomenzar el ciclo


if __name__ == "__main__":
    ## Setup
    #Motor paso a paso pines
    GPIO.setmode(GPIO.BOARD)
    pines = [11,12,13,15]
    # Declaro los pines
    for pin in pines:
      GPIO.setup(pin, GPIO.OUT)
      GPIO.output(pin, 0)    # inicializo en cero
#    time.sleep(1)
    motorNorte(2, 30, pines)

"""
if __name__ == "__main__":
    mpu9250 = MPU9250.MPU9250()
    reorientacion()"""
