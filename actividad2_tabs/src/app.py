#importar modulos
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import database as db
from flask_cors import CORS
import logging
import qrcode

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

# Configuración básica del logger: escribe en consola y establece el nivel mínimo a DEBUG
logging.basicConfig(level=logging.DEBUG)


#acceder al archivo index.html
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
#unir src templates a la carpeta del proyecto
template_dir = os.path.join(template_dir, 'src', 'templates')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
QR_FOLDER = os.path.join(BASE_DIR, 'qrfolder')

#inicializar flask
app = Flask(__name__, template_folder = template_dir)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_FOLDER'] = QR_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 48 * 1024 * 1024
CORS(app)

#--------------------------------------------------------------------------------------------------------------------------------#
#RUTAS DE LA APLICACIÓN
#--------------------------------------------------------------------------------------------------------------------------------#
#ruta principal - VER EMPRESA
@app.route('/')
def home():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM empresa")
    myresult = cursor.fetchall()
    #Convertir datos a diccionario
    empresaData = []
    columnNames = [column [0] for column in cursor.description]
    for record in myresult:
        empresaData.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('index.html', empresaData=empresaData)

@app.route('/empresa', methods=['GET'])
def getEmpresa():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM empresa")
    myresult = cursor.fetchall()
    #Convertir datos a diccionario
    empresaData = []
    columnNames = [column [0] for column in cursor.description]
    for record in myresult:
        empresaData.append(dict(zip(columnNames, record)))
    cursor.close()
    return jsonify(empresaData)



#Ruta para AÑADIR EMPRESA en la BD
# @app.route('/empresa', methods=['POST'])
# def addEmpresa():
#     nombre = request.form['nombre']
#     direccion = request.form['direccion']
#     cif = request.form['cif']
#     email = request.form['email']
#     telefono = request.form['telefono']
    
#     if nombre and direccion and cif and email and telefono:
#         cursor = db.database.cursor()
#         sql = "INSERT INTO empresa (nombre, direccion, cif, email, telefono) VALUES (%s, %s, %s, %s, %s)"
#         data = (nombre, direccion, cif, email, telefono)
#         cursor.execute(sql, data)
#         db.database.commit()
#     return redirect(url_for('home'))


@app.route('/empresa', methods=['POST'])
def addEmpresa():
    data = request.json
    nombre = data['nombre']
    direccion = data['direccion']
    cif = data['cif']
    email = data['email']
    telefono = data['telefono']
    
    if nombre and direccion and cif and email and telefono:
        cursor = db.database.cursor()
        sql = "INSERT INTO empresa (nombre, direccion, cif, email, telefono) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (nombre, direccion, cif, email, telefono))
        db.database.commit()
        return jsonify("Empresa añadida")
    else:
        return jsonify("Datos incompletos"), 400


# #Ruta para ELIMINAR EMPRESA de la BD
# @app.route('/delete/<string:id>')
# def delete(id):
#     cursor = db.database.cursor()
#     sql = "DELETE FROM empresa WHERE id_empresa=%s"
#     data = (id,)
#     cursor.execute(sql, data)
#     return redirect(url_for('home'))

@app.route('/empresa/<id_empresa>', methods=['DELETE'])
def deleteEmpresa(id_empresa):
    try: 
        cursor = db.database.cursor()
        sql = "DELETE FROM empresa WHERE id_empresa = %s"
        cursor.execute(sql, (id_empresa,))
        db.database.commit()

        if cursor.rowcount == 0:
            return jsonify("Empresa no encontrada"), 404

        return jsonify("Empresa eliminada")
    except Exception as e:
        return jsonify(str(e)), 500


# #Ruta para EDITAR EMPRESA en la BD
    
# @app.route('/edit/<string:id>', methods=['POST'])
# def edit(id):
#     nombre = request.form['nombre']
#     direccion = request.form['direccion']
#     cif = request.form['cif']
#     email = request.form['email']
#     telefono = request.form['telefono']
    
#     if nombre and direccion and cif and email and telefono:
#         cursor = db.database.cursor()
#         sql = "UPDATE empresa SET nombre = %s, direccion = %s, cif = %s, email=%s, telefono=%s WHERE id_empresa = %s"
#         data = (nombre, direccion, cif, email, telefono, id)
#         cursor.execute(sql, data)
#         db.database.commit()
#     return redirect(url_for('home'))

@app.route('/edit_empresa/<id_empresa>', methods=['GET'])
def editEmpresa(id_empresa):
    logging.info('Entra en EDIT Empresa')
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM empresa WHERE id_empresa = %s", (id_empresa,))

    # Obtiene los resultados de la consulta
    myresult = cursor.fetchall()
    db.database.commit()

    empresaData = []
    columnNames = [column [0] for column in cursor.description]
    for record in myresult:
        empresaData.append(dict(zip(columnNames, record)))
        logging.info(empresaData)
    cursor.close()
    return jsonify(empresaData)


@app.route('/update_empresa/<id_empresa>', methods=['POST'])
def updateEmpresa(id_empresa):
    try:
        # Obtén los datos enviados desde el frontend
        data = request.get_json()
        nombre = data['nombre']
        direccion = data['direccion']
        cif = data['cif']
        email = data['email']
        telefono = data['telefono']

        # Crea una conexión a la base de datos y un cursor
        cursor = db.database.cursor()

        # Escribe la consulta SQL para actualizar los datos
        query = """
        UPDATE empresa 
        SET nombre = %s, direccion = %s, cif = %s, email = %s, telefono = %s 
        WHERE id_empresa = %s
        """
        cursor.execute(query, (nombre, direccion, cif, email, telefono, id_empresa))

        # Aplica los cambios en la base de datos
        db.database.commit()
        cursor.close()

        return jsonify({'message': 'Empresa actualizada con éxito'}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al actualizar la empresa'}), 500




#--------------------------------------------------------------------------------------------------------------------------------#

######      PROVEEDORES     #########

#--------------------------------------------------------------------------------------------------------------------------------#
#Ruta para VER PROVEEDORES
# @app.route('/proveedores')
# def proveedores():
#     app.logger.info("Entra en proveedores")
#     cursor = db.database.cursor()
#     cursor.execute("SELECT * FROM proveedor")
#     myresult = cursor.fetchall()
#     #Convertir datos a diccionario
#     proveedorData = []
#     columnNames = [column [0] for column in cursor.description]
#     #app.logger.info("proveedorData")
#     for record in myresult:
#         proveedorData.append(dict(zip(columnNames, record)))
#     app.logger.info(proveedorData)    
#     cursor.close()
#     return jsonify(proveedorData)


@app.route('/proveedores', methods=['GET'])
def getProveedor():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM proveedor")
    myresult = cursor.fetchall()
    #Convertir datos a diccionario
    proveedorData = []
    columnNames = [column [0] for column in cursor.description]
    for record in myresult:
        proveedorData.append(dict(zip(columnNames, record)))
    cursor.close()
    return jsonify(proveedorData)

#Ruta para AÑADIR PROVEEDOR
# @app.route('/proveedores', methods=['POST'])
# def add_proveedor():
#     # Obtener los datos del formulario
#     nombre = request.form['nombre']
#     cif = request.form['cif']
#     direccion = request.form['direccion']
#     telefono = request.form['telefono']
#     email = request.form['email']

#     return {}
#     # Verificar que los datos necesarios están presentes
#     if nombre and cif and direccion and telefono and email:
#         cursor = db.database.cursor()
#         sql = "INSERT INTO proveedor (nombre, cif, direccion, telefono, email) VALUES (%s, %s, %s, %s, %s)"
#         data = (nombre, cif, direccion, telefono, email)
#         cursor.execute(sql, data)
#         db.database.commit()
#         cursor.close()
#     return jsonify({"success": True, "message": "Proveedor añadido correctamente"})

@app.route('/add_proveedor', methods=['POST'])
def add_proveedor():
    data = request.json
    nombre = data['nombre']
    cif = data['cif']
    direccion = data['direccion']
    telefono = data['telefono']
    email = data['email']
    
    if nombre and cif and direccion and telefono and email:
        cursor = db.database.cursor()
        sql = "INSERT INTO proveedor (nombre, cif, direccion, telefono, email) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (nombre, cif, direccion, telefono, email))
        db.database.commit()
        return jsonify("Proveedor añadido")
    else:
        return jsonify("Datos incompletos"), 400
    

#Ruta para ELIMINAR PROVEEDOR de la BD
@app.route('/delete_proveedor/<string:id>', methods=['DELETE'])
def delete_proveedor(id):
    try:
        cursor = db.database.cursor()
        sql = "DELETE FROM proveedor WHERE id_proveedor=%s"
        cursor.execute(sql, (id,))
        db.database.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Proveedor eliminado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

#Ruta para EDITAR PROVEEDOR en la BD

# @app.route('/edit_proveedor/<string:id>', methods=['POST'])
# def edit_proveedor(id):
#     # Extracción de datos del formulario
#     logging.info("Entra dentro de edit")
#     logging.info(id)
#     logging.info(request)
#     nombre = request.form['nombre']
#     cif = request.form['cif']
#     direccion = request.form['direccion']
#     telefono = request.form['telefono']
#     email = request.form['email']

#     try:
#         cursor = db.database.cursor()
#         sql = "UPDATE proveedor SET nombre=%s, cif=%s, direccion=%s, telefono=%s, email=%s WHERE id_proveedor=%s"
#         cursor.execute(sql, (nombre, cif, direccion, telefono, email, id))
#         db.database.commit()
#         cursor.close()
#         return jsonify({"success": True, "message": "Proveedor actualizado correctamente"})
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)})

@app.route('/edit_proveedor/<id_proveedor>', methods=['GET'])
def editProveedor(id_proveedor):
    logging.info('Entra en EDIT Proveedor')
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM proveedor WHERE id_proveedor = %s", (id_proveedor,))

    # Obtiene los resultados de la consulta
    myresult = cursor.fetchall()
    db.database.commit()

    proveedorData = []
    columnNames = [column [0] for column in cursor.description]
    for record in myresult:
        proveedorData.append(dict(zip(columnNames, record)))
        logging.info(proveedorData)
    cursor.close()
    return jsonify(proveedorData)


@app.route('/update_proveedor/<id_proveedor>', methods=['POST'])
def updateProveedor(id_proveedor):
    try:
        # Obtén los datos enviados desde el frontend
        data = request.get_json()
        nombre = data['nombre']
        cif = data['cif']
        direccion = data['direccion']
        telefono = data['telefono']
        email = data['email']

        # Crea una conexión a la base de datos y un cursor
        cursor = db.database.cursor()

        # Escribe la consulta SQL para actualizar los datos
        query = """
        UPDATE proveedor 
        SET nombre = %s, cif = %s, direccion = %s, telefono = %s,  email = %s  
        WHERE id_proveedor = %s
        """
        cursor.execute(query, (nombre, cif, direccion, telefono, email, id_proveedor))

        # Aplica los cambios en la base de datos
        db.database.commit()
        cursor.close()

        return jsonify({'message': 'Proveedor actualizado con éxito'}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al actualizar el proveedor'}), 500




#--------------------------------------------------------------------------------------------------------------------------------#

######      PRODUCTO     #########

#--------------------------------------------------------------------------------------------------------------------------------#

#Ruta para VER PRODUCTOS

@app.route('/producto', methods=['GET'])
def getProducto():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM producto")
    myresult = cursor.fetchall()
    #Convertir datos a diccionario
    proveedorData = []
    columnNames = [column [0] for column in cursor.description]
    for record in myresult:
        proveedorData.append(dict(zip(columnNames, record)))
    cursor.close()
    return jsonify(proveedorData)


#Ruta para ELIMINAR PRODUCTO de la BD

@app.route('/delete_producto/<id_producto>', methods=['DELETE'])
def delete_producto(id_producto):
    try:
        cursor = db.database.cursor()
        sql = "DELETE FROM producto WHERE id_producto=%s"
        cursor.execute(sql, (id_producto,))
        db.database.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Producto eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


#RUTA PARA CARGAR/SERVIR IMAGENES
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    logging.info(send_from_directory(app.config['UPLOAD_FOLDER'], filename))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#RUTA PARA CARGAR/SERVIR QT
    
@app.route('/qrfolder/<filename>')
def uploaded_qr(filename):
    return send_from_directory(app.config['QR_FOLDER'], filename)
   

#Ruta para AÑADIR PRODUCTO de la BD

@app.route('/add_producto', methods=['POST'])
def addProducto():
    logging.info(request)
    # Verifica si se envió un archivo en la solicitud
    logging.info("Request files: %s", request.files)
    if 'imagen' not in request.files:
        logging.info("HOLA")
        return jsonify("No se encontró el archivo de imagen"), 400

    imagen = request.files.get('imagen')

    if imagen.filename == '':
        logging.info("No se seleccionó ningún archivo")
        return "No se seleccionó ningún archivo", 400

    if imagen and imagen.read() == b'':
        logging.info("El archivo de imagen está vacío")
        return "El archivo de imagen está vacío", 400
    imagen.seek(0)



    logging.info('imagen')
    logging.info(imagen)

    if imagen.filename == '':
        return jsonify("No se seleccionó ninguna imagen"), 400

    
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Crea la carpeta si no existe
    
    if imagen:
        filename = secure_filename(imagen.filename)
        imagen_path = os.path.join(upload_folder, filename).replace("\\", "/")
        try:
            imagen.save(imagen_path)
            relative_imagen_path = os.path.join('uploads', filename).replace("\\", "/")
            logging.info(relative_imagen_path)
        except Exception as e:
                logging.error("No se ha guardado la imagen: %s", str(e))
                return jsonify(str(e)), 500

    data = request.form
    logging.info(data)

    referencia = data.get('referencia')
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    tamano = data.get('tamano')
    color = data.get('color')
    material = data.get('material')
    precio = data.get('precio')
    logging.info("DESPUES DE PRECIO")
    
    if referencia and nombre and descripcion and tamano and color and material and precio:
        logging.info("ENTRA EN EL IF")


        # Buscar código QR no usado
        try:

            cursor = db.database.cursor()
            qr_folder = app.config['QR_FOLDER']
            logging.info('QR_FOLDER')
            logging.info(qr_folder)

            if not os.path.exists(qr_folder):
                logging.info('No existe el PATH')
                os.makedirs(qr_folder)

            qr_filename = 'qr_code_' + referencia + '.png'
            qr_path = os.path.join(qr_folder, qr_filename).replace("\\", "/")
            relative_qr_path = os.path.join('qrfolder', qr_filename).replace("\\", "/")
            logging.info(qr_path)

            # Generar un nuevo código QR
            qr = qrcode.make(referencia) 
            qr.save(qr_path)
            logging.info('QR SALVADO')

            try:
                # Ejecutar la inserción
                cursor.execute("INSERT INTO codigo_qr (codigo_qr, estado, imagen) VALUES (%s, %s, %s)", (referencia, True, relative_qr_path))
                db.database.commit()  # Confirma la transacción después de la inserción

                # Obtener el último ID insertado
                cursor.execute("SELECT LAST_INSERT_ID()")
                id_codigoqr = cursor.fetchone()[0]


            except Exception as e:
                logging.error("Error al insertar el código QR: %s", str(e))
                return jsonify(str(e)), 500

            
            try:
                logging.info('imagen_path')
                logging.info(imagen_path)
                sql = ("INSERT INTO producto (id_codigoqr, referencia, nombre, descripcion, tamano, color, material, precio, imagen) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
                cursor.execute(sql, (id_codigoqr, referencia, nombre, descripcion, tamano, color, material, precio, relative_imagen_path))
        
                # Marcar el código QR como usado
                cursor.execute("UPDATE codigo_qr SET estado = True WHERE id_codigoqr = %s", (id_codigoqr,))
            
                db.database.commit()
                
                return jsonify("Producto añadido con código QR")
            
            except Exception as e:
                logging.error("Error al añadir el producto a la base de datos: %s", str(e))
                return jsonify(str(e)), 500
        except Exception as e:
            return jsonify(str(e)), 500
    else:
        return jsonify("Datos incompletos"), 400
    
#Ruta para EDITAR PRODUCTO de la BD

@app.route('/edit_producto/<id_producto>', methods=['GET'])
def editProducto(id_producto):
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM producto WHERE id_producto = %s", (id_producto,))

    # Obtiene los resultados de la consulta
    myresult = cursor.fetchall()
    db.database.commit()

    productoData = []
    columnNames = [column [0] for column in cursor.description]
    for record in myresult:
        productoData.append(dict(zip(columnNames, record)))
    cursor.close()
    return jsonify(productoData)

@app.route('/update_producto/<id_producto>', methods=['POST'])
def updateProducto(id_producto):
    try:
        referencia = request.form.get('referencia')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        tamano = request.form.get('tamano')
        color = request.form.get('color')
        material = request.form.get('material')
        precio = request.form.get('precio')

        imagen = request.files.get('imagen')
        imagen_actual=request.form.get('imagenActual')
        if imagen:
            upload_folder = app.config['UPLOAD_FOLDER']
            filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(upload_folder, filename).replace("\\", "/")
            imagen.save(imagen_path)
            relative_imagen_path = os.path.join('uploads', filename).replace("\\", "/")
        else:
            # Omitir la actualización de la imagen
            relative_imagen_path = imagen_actual
            

        # Conexión a la base de datos y cursor
        cursor = db.database.cursor()

        # Consulta SQL para actualizar los datos
        query = """
        UPDATE producto
        SET referencia = %s, nombre = %s, descripcion = %s, tamano = %s, color = %s, material = %s, precio = %s, imagen = %s
        WHERE id_producto = %s
        """
        cursor.execute(query, (referencia, nombre, descripcion, tamano, color, material, precio, relative_imagen_path, id_producto))

        # Aplicar cambios en la base de datos
        db.database.commit()
        cursor.close()

        return jsonify({'message': 'Producto actualizado con éxito'}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al actualizar el producto'}), 500



#--------------------------------------------------------------------------------------------------------------------------------#

######      CODIGO QR     #########

#--------------------------------------------------------------------------------------------------------------------------------#


#Ruta para OBTENER CODIGO QR de la BD
@app.route('/get_qr_image/<int:id_codigoqr>')
def get_qr_image(id_codigoqr):
    try:
        cursor = db.database.cursor()
        cursor.execute("SELECT imagen FROM codigo_qr WHERE id_codigoqr = %s", (id_codigoqr,))
        result = cursor.fetchone()
        logging.info("HOOOLAAA")
        logging.info(result)
        cursor.close()

        if result:
            logging.info("DENTRO DE IF")
            imagen_path = result[0]
            logging.info(imagen_path)

            if os.path.isfile(os.path.join(app.config['QR_FOLDER'], imagen_path)):
                return send_from_directory(app.config['QR_FOLDER'], imagen_path)
            else:
                return jsonify({'message': 'Archivo de imagen no encontrado'}), 404
        else:
            return jsonify({'message': 'Código QR no encontrado'}), 404

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error al obtener la imagen del código QR'}), 500
    

    
#--------------------------------------------------------------------------------------------------------------------------------#

# LANZAR APLICACION

#--------------------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    app.run(debug=True, port=4000)