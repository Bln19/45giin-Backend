#crear conexion a la base de datos de phpMyAdmin
import mysql.connector

#establecer los datos de acceso para conectarnos a la base de datos
database = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    database = 'inventarioberiestudio'
)