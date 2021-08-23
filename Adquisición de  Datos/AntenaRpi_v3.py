import numpy as np
import serial
import os
import time
from programa2 import reorientacion
from MotorMPU import MotorMPU
from programa2 import motorNorte
from programa2 import inicializacionPines
from programa2 import obtener_mensajes
from parspyfunc_v2 import parspy
from firebase import firebase
from firebase_admin import credentials, initialize_app, storage, db
from calibracion import calibracion
from datetime import datetime, timedelta





while True:
    # setup
    pines = [11,12,13,15]
    inicializacionPines(pines)
    try:
#        ser = serial.Serial(port='/dev/ttyUSB0')
        ser = serial.Serial(port='/dev/ttyS0')
        print('Conectado con ', ' - GPS')
    except:
        ser = serial.Serial(port='/dev/ttyUSB0')
        print('Conectado con ', ' - USB')
    
    #Calibramos   
    x_m, y_m, z_m, pos_inicial = calibracion(pines, False) #True o False para plotear o no
    
    anteultimo =  reorientacion(x_m, y_m, z_m)
   
    #Iniciamos comunicacion con Firebase
    cred = credentials.Certificate('datosantenta-33dcb8157510.json')
    initialize_app(cred, {'storageBucket': 'datosantenta.appspot.com','databaseURL': 'https://datosantenta.firebaseio.com'})
    
    while True:
    #Leemos mensajes
            
        satint, fecha_sat, hora_sat, hora_final = obtener_mensajes()
        satstr = str(satint)
        hora_act = datetime.now().time()
        fecha_act = time.strftime("%d%m%y")    
        hora_sat = datetime.strptime(hora_sat, "%X").time()
        hora_final = datetime.strptime(hora_final, "%X").time()
        
       
        if fecha_act == fecha_sat and hora_sat <= hora_act <= hora_final:
                    
            f = open('prn.out', 'w') 
            g = open('prn_Azim.out', 'w')          
                              
            i = 0
            l = 0
            cantidad = 50
           
            while i < cantidad:
                
                linea = ser.readline()
                try:
                    linea = linea.decode('utf-8')
                    
                        #print(linea)                    
                    if linea[1:6] == 'GPGSV':                        
                        angElev, angAzim, intensidad = parspy(linea, satint)                        
                        if angAzim == []:  #Si no guarda ningun dato
                                
                            l += 1                           
                        else:
                            data = np.array([angElev, intensidad])     # juntamos los datos
                            ts = np.array2string(data, separator=',')   # pasamos a string
                            f.write(ts)
                            f.write('\n')                 
                            if angAzim > 180: #Conversion a escala (-180,180)
                                angAzim = angAzim - 360
                            else:
                                pass
                            g.write(str(angAzim))
                            print("Angulo azimutal ", angAzim)
                            print("Anteultimo ", anteultimo)
                            anteultimo = MotorMPU(angAzim, anteultimo, x_m, y_m, z_m, pines)
                    else:
                        pass
                            
                except:                    
                    print('Error en la línea')
                    pass
                
                i+=1
                
                if l == 20:
                    print('No está disponible el satelite')                
                    posAct = reorientacion(x_m,y_m,z_m)
                    motorNorte(pos_inicial, posAct,pines)
                    #ser.close()
                    time.sleep(10)
                    
                else:
                    pass
            
            f_size = f.seek(0, os.SEEK_END)   # tamaño del archivo
            
            f.close()       # cerramos archivo
            g.close()       # cerramos archivo                
            print(f_size)
            
            if f_size > 0:     # si el archivo contiene datos
                
                print("Mandamos datos...")
                fileName = "prn.out"
                bucket = storage.bucket()
                timestr = time.strftime("%y%m%d")
                timestr2 = time.strftime("%H,%M,%S")
                blob = bucket.blob(timestr+'prn'+satstr+timestr2+'.out')
                blob.upload_from_filename(fileName)
                time.sleep(2)
                
            else:
                print("No se adquirieron datos")
                    
        elif fecha_act != fecha_sat:
            print('Las fechas no coinciden')
            time.sleep(600) #Que espere 10min en caso de que no coincidan las fechas de satelite y actual
            
        elif fecha_act == fecha_sat and hora_act < hora_sat:
            h_a = int(hora_act.hour)            
            h_s = int(hora_sat.hour)
                
            h_a_s = h_a*3600 #Paso horas a segundos
            h_s_s = h_s*3600 #Paso horas a segundos
                
            m_a = int(hora_act.minute)
            m_s = int(hora_sat.minute)
                
            m_a_s = m_a*60 #Paso minutos a segundos
            m_s_s = m_s*60 #Paso minutos a segundos
                        
            s_a = int(hora_act.second)
            s_s = int(hora_sat.second)
                
            s_act = h_a_s+m_a_s+s_a
            s_sat = h_s_s+m_s_s+s_s
                    
            dif = s_sat-s_act
            if dif >=0:
                print('Tengo que esperar', dif, 'segundos')
                time.sleep(dif)
            elif dif <0:
                print('Ya pasó el satélite')
                posAct = reorientacion(x_m,y_m,z_m)
                motorNorte(pos_inicial, posAct,pines)
                f.close()         # cerramos todas las comunciaciones
                g.close()
                
                        
                time.sleep(600) #Si la diferencia es negativa significa que ya pasó el satélite        
            
            
    except:
        print('No estoy leyendo nada')             
        f.close()         # cerramos todas las comunciaciones
        g.close()         # y volvemos a empezar
            
        time.sleep(120) #Que espere 2 min en caso de que no tenga conexion        
        
                            
   
else:
    print('Esperando órdenes o conexión')
        
        
    
    