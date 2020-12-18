# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal
"""
import numpy as np
import serial
import time
from programa2 import reorientacion
from MotorMPU import MotorMPU
from programa2 import motorNorte
from programa2 import inicializacionPines
from parspyfunc_v2 import parspy
from firebase import firebase
from firebase_admin import credentials, initialize_app, storage
   
while True:
    # setup
    pines = [11,12,13,15]
    inicializacionPines(pines)
    try:
        ser = serial.Serial(port='/dev/ttyUSB0')
        print('Conectado con ', ' - USB0')
    except:
        ser = serial.Serial(port='/dev/ttyUSB1')
        print('Conectado con ', ' - USB1')    
    anteultimo =  reorientacion()
#    motorNorte(0, anteultimo, pines)
    satint = 25
    satstr = str(satint)

    cred = credentials.Certificate('datosantenta-33dcb8157510.json')
    initialize_app(cred, {'storageBucket': 'datosantenta.appspot.com'})

    while True:
        try:
                      
            #Crea las tiras de datos con los valores medidos
            f = open('prn.out', 'w') 
            g = open('prn_Azim.out', 'w')             
            
            i = 0
            cantidad = 50
            while i < cantidad: 
                linea = ser.readline()
                try:
                    linea = linea.decode('utf-8')
                    print(linea)
            
                    if linea[1:6] == 'GPGSV':
                        angElev, angAzim, intensidad = parspy(linea, satint)
                        print("Tipo ")
                        data = np.array([angElev, intensidad])     # juntamos los datos
                        ts = np.array2string(data, separator=',')   # pasamos a string
                        f.write(ts)
#                        f.write('\n')
                        if angAzim == []: 
                            pass
                        else:
                            print(angAzim)
                            g.write(str(angAzim))
                            if angAzim > 180: #Conversion a escala (-180,180)
                                angAzim = angAzim - 360
                            else:
                                pass
                            print("Angulo azimutal ", angAzim)
                            print("Anteultimo ", anteultimo)
                            anteultimo = MotorMPU(angAzim, anteultimo, pines)
       
                    else:
                        pass                    
                except:
                    print("Error en la linea, pasando a la siguiente")
                    pass
                i+=1
            f.close()
            g.close()
            time.sleep(2)
            print("Mandamos datos...")
            fileName = "prn.out"
            bucket = storage.bucket()
            timestr = time.strftime("%y%m%d")
            timestr2 = time.strftime("%H,%M,%S")
            blob = bucket.blob(timestr+'prn'+satstr+timestr2+'.out')
            blob.upload_from_filename(fileName)
            time.sleep(2)
        except:
            f.close()         # cerramos todas las comunciaciones
            g.close()         # y volvemos a empezar
            ser.close()
            