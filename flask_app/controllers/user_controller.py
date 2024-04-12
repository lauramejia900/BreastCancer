
from flask_app import app
import cv2
from flask import render_template, redirect, request, session, flash, jsonify, url_for
import tensorflow.keras.models as models
import tensorflow as tf
from PIL import Image
import numpy as np
from flask_app.models.users_hospital import UserHospital
from flask_app.models.user import Users
from flask import flash

#Para subir imagenes
from werkzeug.utils import secure_filename #para obtener el nombre del archivo
import os

#Importar bcrypt para codificar la contraseña
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app) # se crea una instancia de bcrypt


modelo = tf.keras.models.load_model('flask_app/static/script/vgg.h5')

def preprocess_image(urlImagen, IMG_SIZE = 224):
    imagen = cv2.imread(urlImagen, 1)
    # Redimensionar la imagen al tamaño requerido por el modelo
    imagen_redimensionada = cv2.resize(imagen, (IMG_SIZE,IMG_SIZE))
    # Convertir la imagen a un array NumPy
    # imagen_array = np.array(imagen_redimensionada)
    # Normalizar los valores de los píxeles entre 0 y 1
    # Agregar una dimensión adicional al array de la imagen
    return np.array([imagen_redimensionada])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hospital')
def hospital():
    return render_template('hospital.html')


@app.route('/registrate', methods=['POST'])
def registrate():
    #Validar la información ingresada
    if UserHospital.valida_usuario(request.form) == False:
        return redirect('/signup')

    pwd = bcrypt.generate_password_hash(request.form['password']) #Encriptamos el password del usuario

    formulario = {
        "name": request.form['name'],
        "email": request.form['email'],
        "password": pwd
    }

    #request.form = FORMULARIO HTML
    id = UserHospital.save(formulario) #Recibo el identificador de mi nuevo usuario
    return redirect('/hospitales')

@app.route('/login', methods=['POST'])
def login():
    #Verificar que el email EXISTA
    #request.form RECIBIMOS DE HTML
    #request.form = {email: elena@cd.com, password: 123}
    user = UserHospital.get_by_email(request.form) #Recibiendo una instancia de usuario o Falso
    if not user:
        flash('E-mail no encontrado', 'login')
        return redirect('/hospital')

    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash('Password incorrecto', 'login')
        return redirect('/hospital')
    session['user_id'] = user.id
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/hospital')
    formulario = {
        'id': session['user_id']
    }
    user = UserHospital.get_by_id(formulario)
    return render_template('dashboard.html',  user = user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/hospital')

@app.route('/paciente')
def paciente():
    return render_template('paciente.html')

@app.route('/cancer')
def cancer():
    return render_template('cancer.html')

@app.route('/tratamiento')
def tratamiento():
    return render_template('tratamiento.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/nosotros2')
def nosotros2():
    return render_template('nosotros2.html')

@app.route('/formulario')
def formulario():
    hospitales = UserHospital.get_by_all()
    return render_template('formulario.html', hospitales = hospitales)

@app.route('/formulario2')
def formulario2():
    id = session['user_id']
    return render_template('formulario2.html', id = id)


@app.route('/exam', methods=['POST'])
def exam():
    #Validar la información ingresada
    if 'user_id' not in session:
        if Users.valida_usuario_paciente(request.form) == False:
            return redirect('/formulario')
    else:
        if Users.valida_usuario_paciente(request.form) == False:
            return redirect('/formulario2')

    if 'exam' not in request.files:
        flash('Imagen no subida', 'registro')
        return redirect('/formulario')

    exam = request.files['exam']

    if exam.filename == '':
        flash('Nombre de imagen vacio', 'registro')
        return redirect('/formulario')

    nombre_exam = secure_filename(exam.filename)
    exam.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_exam))  

    imagen = (os.path.join(app.config['UPLOAD_FOLDER'], nombre_exam))
    imagen_preprocesada = preprocess_image(imagen)
    resultado = modelo.predict(imagen_preprocesada)[0]
    
    if resultado[0] >= 0.6:
        resultados =  'N'
        valor = resultado[0]
    if resultado[1] >= 0.6:
        resultados =  'B'
        valor = resultado[1]
    if resultado[2] >= 0.6:
        resultados =  'M'
        valor = resultado[2]

    image = Image.open(imagen).convert('L')
    # image = Image.eval(image, lambda x: 255 - x)
    name_before_dot = nombre_exam.split(".")[0]
    nombreExam = name_before_dot + ".png"
    image_path_png = (os.path.join(app.config['UPLOAD_FOLDER'], nombreExam))
    examDef = image.save(image_path_png, 'PNG')

    formulario = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "edad": request.form['edad'],
        "email": request.form['email'],
        "exam": nombreExam,
        "users_hospital_id": request.form['users_hospital_id'],
        "diagnostico": resultados
    }  
    id = Users.save(formulario) #Recibo el identificador de mi nuevo usuario
    if 'user_id' not in session:
        return redirect(url_for('resultados', respuesta = resultados, valor = valor, id = id))
    else:
        return redirect(url_for('resultados2', respuesta = resultados, valor = valor, id = id))

@app.route('/resultados/<respuesta>/<valor>/<id>')
def resultados(respuesta, valor, id):
    resultado = respuesta
    valor = valor
    id = id
    formulario ={
        "id": id
    }
    user = Users.get_by_id(formulario)

    return render_template('resultados.html', resultado = resultado, valor = valor, user = user)

@app.route('/resultados2/<respuesta>/<valor>/<id>')
def resultados2(respuesta, valor, id):
    resultado = respuesta
    valor = valor
    id = id
    id_hospital = session['user_id']
    formulario ={
        "id": id
    }
    user = Users.get_by_id(formulario)
    return render_template('resultados2.html', resultado = resultado, valor = valor, user = user, id_hospital = id_hospital)

@app.route('/signup')
def signup():
    return render_template('sing.html')

@app.route('/hospitales')
def hospitales():
    hospitales = UserHospital.get_by_all()
    return render_template('listaHospitales.html', hospitales = hospitales)

@app.route('/pacientes')
def pacientes():
    id = session['user_id']
    pacientes = Users.get_by_all()
    return render_template('listaPacientes.html', pacientes = pacientes, id = id)

@app.route("/delete/<int:id>")
def eliminar(id):
    if 'user_id' not in session: #pregunta si user_id esta guardado en la session 
        return redirect('/hospital')
    formulario =  {
        "id": id
    }
    UserHospital.eliminar_hospital(formulario)
    return redirect('/hospitales')


