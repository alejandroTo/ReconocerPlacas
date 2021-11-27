import cv2
import pytesseract
import pyodbc
from tkinter import *
from tkinter import messagebox
import imutils
def connect():
    direccion_servidor = 'DESKTOP-LR7HVFP\SQLEXPRESS'
    nombre_bd = 'placas'
    try:
        conexion = pyodbc.connect(driver='{SQL Server Native Client 11.0}',
                        server=direccion_servidor, 
                        database=nombre_bd,               
                        trusted_connection='yes')
        return conexion
    except Exception as e:
        print("ocurrió un error al conectar a SQL Server: ", e)
def SelectData(parametro):
    c1 = connect()
    try:
        with c1.cursor() as cursor:
            consulta = 'select nombre,paterno,materno,direccion,numero_placa  from Usuario join Placa on id_usario = Usuario_id_usario where numero_placa = ?'
            adr = parametro
            cursor.execute(consulta, parametro)     
            myresult = cursor.fetchall()
            if len(myresult)>0:
                print(f'Nombre: {myresult[0][0]} \nApellido Paterno: {myresult[0][1]} \nApellido Materno: {myresult[0][2]}')
                print(f'Direccion: {myresult[0][3]} \nnumero_placa: {myresult[0][4]}')
            else:
                print(f'Usuario con Placa: {parametro} no encontrado')
    except Exception as e:
        print("Ocurrió un error al conectar a SQL Server: ", e)
def InsertData(nombre, paterno, materno, direccion):
    c1 = connect()
    try:
        with c1.cursor() as cursor:
            consulta = 'insert into usuario(nombre, paterno, materno, direccion) VALUES (?, ?, ?, ?)'
            cursor.execute(consulta,nombre, paterno, materno, direccion)   
        with c1.cursor() as cursor:
            lastdate = 'SELECT TOP 1 * FROM Usuario ORDER BY id_usario DESC'
            cursor.execute(lastdate)     
            myresult = cursor.fetchall()
            plate = input("Placa: ")
            InsertPlate(myresult[0][0],plate)
    except Exception as e:
        print("Ocurrió un error al conectar a SQL Server: ", e)

def InsertPlate(Usuario_id_usario,plate):
    c1 = connect()
    try:
        with c1.cursor() as cursor:
            consulta = 'insert into Placa(Usuario_id_usario, numero_placa) VALUES (?, ?)'
            cursor.execute(consulta,Usuario_id_usario, plate)     
    except Exception as e:
        print("Ocurrió un error al conectar a SQL Server: ", e)
def leer():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    placa = []
    image = cv2.imread('temporal/objeto_04.jpg')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray,(3,3))
    canny = cv2.Canny(gray,150,200)
    canny = cv2.dilate(canny,None,iterations=1)
    cnts,_ = cv2.findContours(canny,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        area = cv2.contourArea(c)
        x,y,w,h = cv2.boundingRect(c)
        epsilon = 0.09*cv2.arcLength(c,True)
        approx = cv2.approxPolyDP(c,epsilon,True)
  
        if len(approx)==4 and area>500:
            print('area=',area)
            aspect_ratio = float(w)/h
            if aspect_ratio>0.1:
                placa = gray[y:y+h,x:x+w]
                text = pytesseract.image_to_string(placa,config='--psm 11')
                #limpiar texto de la placa
                text_clean = text.strip().replace(" ", "")
                text_clean = text_clean.replace("-", "")
                print('PLACA: ',text_clean)
                cv2.imshow('PLACA',placa)
                SelectData(text_clean)
                cv2.moveWindow('PLACA',780,10)
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),3)
                cv2.putText(image,text,(x-20,y-10),1,2.2,(0,255,0),3)
      
    cv2.imshow('Image',cv2.drawContours(image,cnts,-1,(0,255,0),2))
    cv2.moveWindow('Image',45,10)
    cv2.waitKey(0)
        
x1, y1 = 190, 80
x2, y2 = 490, 380
def menu():
    try:
        opc = int(input("1.Crear usuario. \n2.Detectar Placa. \n3.salir"))
        return opc
    except Exception as e:
      print("Ingresa una opcion valida", e)
def main():

    opc = menu()
    while(opc!=3):
        if opc==1:
            nombre = input("Nombre: ")
            paterno = input("Paterno: ")
            materno = input("Materno: ")
            direccion = input("Dirección: ")
            InsertData(nombre, paterno, materno, direccion)
            opc = menu()
        elif opc==2:
            leer()
            opc = menu()
        elif opc==3:
            print("Saliendo...")
        else:
             print("Ingresa una opción valida")
             opc = menu()

main()
