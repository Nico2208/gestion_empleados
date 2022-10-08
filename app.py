from flask import Flask
from flask import render_template, request, redirect, url_for, flash #Redirect nos va a permitir redireccionar una vez que eliminemos un registro de la bd, es decir regresar ala URL desde donde vino
from flaskext.mysql import MySQL
from datetime import datetime
import os
from flask import send_from_directory

app = Flask(__name__)

app.secret_key = "ClaveSecreta"

#Conexion con la base de datos: sabemos que datos tenemos para nuestra conexion.

mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema'

mysql.init_app(app)


CARPETA = os.path.join('uploads')

app.config['CARPETA'] = CARPETA


# La / indica el host con puerto 5000 y de forma automatica se accede al index.html que ya esta siendo renderizado por flask.
#Sirve para llamar a nuestro template para que se muestre
#Consultamos datos de tabla empleados y los mostramos en la terminal.


@app.route('/')
def index():

    sql = "SELECT * FROM `sistema`.`empleados`;"

    conn = mysql.connect()

    cursor = conn.cursor()

    cursor.execute( sql )

    empleados = cursor.fetchall() #Recuperamos la informacion de la DB y la mostramos en la terminal como una tupla de tuplas

    print( empleados ) 

    conn.commit()

    return render_template('empleados/index.html', empleados = empleados) #Hacemos el envio de informacion a traves del render_template

#Llamamos a nuestro template para que se muestre. Hacemos referencia al archivo create.html
@app.route('/create')
def create():
    return render_template('empleados/create.html')


#Generamos el acceso a la carpeta Uploads. Nos dirige a la carpeta y nos muestra la foto guardada en la variable nombreFoto
@app.route('/uploads/<nombreFoto>')  #uploads/{{empleado[3]}}
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)
    


#Tomo los datos ingresados desde el formulario y los guardo en la base de datos    

@app.route('/store', methods=['POST'])

def storage():
    #Estas instrucciones me permiten conectarme a la BD, insertar la informacion y despues redireccionar
    _nombre = request.form['txtNombre']

    _correo = request.form['txtCorreo']

    _foto = request.files['txtFoto']

    if _nombre == '' or _correo == '' or _foto == '':
        flash( 'Recuerda llenar los datos de los campos.' )
        return redirect( url_for( 'create' ) )

    now = datetime.now() #Realizo las siguientes operaciones para no pisar imagenes que tengan el mismo nombre; agrego la fecha en que son subidas las imagenes. Nos aseguramos que el nombre de la foto ingresada sea siempre distinto.

    tiempo = now.strftime("%Y%H%M%S") 

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save( "uploads/" + nuevoNombreFoto )

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);" #Con %s reemplazo los valores fijos por los valores que el usuario ingresa en el formulario

    datos = ( _nombre, _correo, nuevoNombreFoto )

    conn = mysql.connect()

    cursor = conn.cursor()

    cursor.execute(sql, datos) #Uno los datos recibidos del formulario con la base de datos

    conn.commit()

    return redirect('/')


#Ruteo para eliminar registros de la base de datos
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute( "SELECT foto FROM `sistema`.`empleados` WHERE id = %s;", id ) #Seleccionamos los datos
    fila = cursor.fetchall() #Tomamos toda la informacion
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) #Removemos la foto
    cursor.execute(f"DELETE FROM `sistema`.`empleados` WHERE id={id};")
    conn.commit()
    return redirect('/')










#Ruteo para editar un registro de la base de datos
@app.route('/edit/<int:id>')
def edit( id ):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `sistema`.`empleados` WHERE id={id};")
    empleados = cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleados = empleados)





#Ruteo para recibir la informacion del formulario de actualizacion de registros. RUTEO UPDATE
@app.route('/update', methods = ['POST'])
def update():

    #Recibo los datos enviados desde el formulario
    
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtID']

    sql = "UPDATE `sistema`.`empleados` SET `nombre`= %s, `correo`= %s WHERE id = %s;"

    datos = ( _nombre, _correo, id )

    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now() 
    tiempo = now.strftime( "%Y%H%M%S" ) 

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save( "uploads/" + nuevoNombreFoto )
        cursor.execute( "SELECT foto FROM `sistema`.`empleados` WHERE id = %s;", id ) #Actualizamos la tabla solo para  el id seleccionado y cerramos conexion.
        fila = cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute( "UPDATE `sistema`.`empleados` SET foto = %s WHERE id = %s;", ( nuevoNombreFoto, id ) )
        conn.commit()

    cursor.execute( sql, datos )

    conn.commit()

    return redirect('/')

    

if __name__ == "__main__":
    app.run(debug=True)