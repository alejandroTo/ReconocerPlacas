import cv2
import pytesseract
import pyodbc
from tkinter import *
from tkinter import messagebox
import imutils
def connect():
    direccion_servidor = 'DESKTOP-4GCAPQ1\SQLEXPRESS'
    nombre_bd = 'placas'
    try:
        conexion = pyodbc.connect(driver='{SQL Server Native Client 11.0}',
                        server=direccion_servidor, 
                        database=nombre_bd,               
                        trusted_connection='yes')
        return conexion
    except Exception as e:
        print("ocurrio un error al conectar a SQL Server: ", e)

def crearCarpeta():
    if not os.path.exists(Datos):
        os.makedirs(Datos)

def SelectData(parametro):
    c1 = connect()
    try:
        with c1.cursor() as cursor:
            consulta = 'select * from Usuario join Placa on id_usario = Usuario_id_usario where numero_placa = ?'
            adr = parametro
            # Podemos llamar muchas veces a .execute con datos distintos
            cursor.execute(consulta, parametro)     
            myresult = cursor.fetchall()
            for x in myresult:
                print(f'{x}')
    except Exception as e:
        print("Ocurrio un error al conectar a SQL Server: ", e)
def InsertData(nombre, paterno, materno, direccion):
    c1 = connect()
    try:
        with c1.cursor() as cursor:
            consulta = 'insert into usuario(nombre, paterno, materno, direccion) VALUES (?, ?, ?, ?)'
            #adr = parametro
            # Podemos llamar muchas veces a .execute con datos distintos
            cursor.execute(consulta,nombre, paterno, materno, direccion)   
        with c1.cursor() as cursor:
            lastdate = 'SELECT TOP 1 * FROM Usuario ORDER BY id_usario DESC'
            cursor.execute(lastdate)     
            myresult = cursor.fetchall()
            plate = input("Placa: ")
            InsertPlate(myresult[0][0],plate)
    except Exception as e:
        print("Ocurrio un error al conectar a SQL Server: ", e)

def InsertPlate(Usuario_id_usario,plate):
    c1 = connect()
    try:
        with c1.cursor() as cursor:
            consulta = 'insert into Placa(Usuario_id_usario, numero_placa) VALUES (?, ?)'
            #adr = parametro
            # Podemos llamar muchas veces a .execute con datos distintos
            cursor.execute(consulta,Usuario_id_usario, plate)     
    except Exception as e:
        print("Ocurrio un error al conectar a SQL Server: ", e)
def leer():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    placa = []
    image = cv2.imread('temporal/objeto_0.jpg')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray,(3,3))
    canny = cv2.Canny(gray,150,200)
    canny = cv2.dilate(canny,None,iterations=1)
    #cv2.imshow('Image',canny)
    #_,cnts,_ = cv2.findContours(canny,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    cnts,_ = cv2.findContours(canny,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(image,cnts,-1,(0,255,0),2)
    for c in cnts:
        area = cv2.contourArea(c)
        x,y,w,h = cv2.boundingRect(c)
        epsilon = 0.09*cv2.arcLength(c,True)
        approx = cv2.approxPolyDP(c,epsilon,True)
  
        if len(approx)==4 and area>500:
            print('area=',area)
            #cv2.drawContours(image,[approx],0,(0,255,0),3)
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
def captura():
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    count = 0
    while True:
        ret, frame = cap.read()
        if ret == False:  break
        imAux = frame.copy()
        cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)
        objeto = imAux[y1:y2,x1:x2]
        objeto = imutils.resize(objeto, width=300)
        cv2.imshow('frame',frame)
        #k = cv2.waitKey(1)
        if cv2.waitKey(1) == 27:
            break
    cv2.imwrite('temporal'+'/objeto_{}.jpg'.format(count),objeto)
   
    cap.release()
    cv2.destroyAllWindows()


def menu():
    try:
        opc = int(input("1.Crear usuario. \n2.Detectar Objetos. \n3.salir"))
        return opc
    except Exception as e:
      print("Ingresa una opcion valida", e)
def main():
    #captura()
    #a = connect()
    #interfaz()
    #leer()
    opc = menu()
    while(opc!=3):
        if opc==1:
            nombre = input("Nombre: ")
            paterno = input("Paterno: ")
            materno = input("Materno: ")
            direccion = input("direccion: ")
            InsertData(nombre, paterno, materno, direccion)
            #objeto Create Folder
            opc = menu()
        elif opc==2:
            leer()
            opc = menu()
        elif opc==3:
            print("saliendo...")
        else:
             print("Ingresa una opcion valida")
             opc = menu()

main()
