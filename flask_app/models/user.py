from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash


import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Users:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.edad = data['edad']
        self.email = data['email']
        self.exam = data['exam']
        self.users_hospital_id = data['users_hospital_id']
        self.created_at = data['created_at']
        self.diagnostico = data['diagnostico']

    @classmethod
    def save(cls, formulario):
        query = "INSERT INTO users (first_name, last_name, edad, exam, email, users_hospital_id, diagnostico) VALUES (%(first_name)s,  %(last_name)s, %(edad)s, %(exam)s,%(email)s, %(users_hospital_id)s, %(diagnostico)s)"
        result = connectToMySQL('breast_cancer').query_db(query, formulario) #regresa el nuevo id de la persona registrada 
        return result

    @staticmethod
    def valida_usuario_paciente(formulario):
        es_valido = True
        #Validar que el nombre tenga al menos 3 caracteres
        if len(formulario['first_name']) < 2:
            flash('Debe ingresar el nombre', 'registro')
            es_valido = False
        
        if len(formulario['last_name']) < 2:
            flash('Debe ingresar el apellido', 'registro')
            es_valido = False

        if len(formulario['edad']) < 1:
            flash('Debe ingresar la edad', 'registro')
            es_valido = False

        #verificar que el email tenga formato correcto EXPRESIONES REGULARES
        if not EMAIL_REGEX.match(formulario['email']):
            flash("El correo es invalido", 'registro')
            es_valido = False
        
        return es_valido

    @classmethod
    def get_by_email(cls, formulario):
        query = "SELECT * FROM users_hospital WHERE email = %(email)s"
        result = connectToMySQL('breast_cancer').query_db(query, formulario) #Regresa una lista 
        if len(result) < 1: #se pregunta por el tamaño del diccionario que el query regresa, si es menor a 1 es porque no contiene datospor lo que el email no ha sido registrado previamente
            return False
        else:
            user = cls(result[0])
            return user


    @classmethod
    def get_by_all(cls):
        query = "SELECT * FROM users"
        result = connectToMySQL('breast_cancer').query_db(query)
        users = []
        for i in result:
            users.append(cls(i))
        return users
    

    @classmethod
    def get_by_id(cls, formulario):
        query = "SELECT * FROM users WHERE id = %(id)s"
        result = connectToMySQL('breast_cancer').query_db(query, formulario)
        user = cls(result[0])
        return user
