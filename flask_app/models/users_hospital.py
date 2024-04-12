from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash


import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserHospital:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.email = data['email']
        self.password = data['password'] 
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save(cls, formulario):
        query = "INSERT INTO users_hospital (name, email, password) VALUES (%(name)s,  %(email)s, %(password)s)"
        result = connectToMySQL('breast_cancer').query_db(query, formulario) #regresa el nuevo id de la persona registrada 
        return result

    @staticmethod
    def valida_usuario(formulario):
        es_valido = True
        #Validar que el nombre tenga al menos 3 caracteres
        if len(formulario['name']) < 2:
            flash('Debe ingresar el nombre', 'registro')
            es_valido = False

        #verificar que el email tenga formato correcto EXPRESIONES REGULARES
        if not EMAIL_REGEX.match(formulario['email']):
            flash("Correo invalido", 'registro')
            es_valido = False

        #Password con al menos 3 caracteres
        if len(formulario['password']) < 6 :
            flash('La contraseña debe tener al menos 8 carcateres', 'registro')
            es_valido = False

        #Verificar que las contraseñas coincidan
        if formulario['password'] != formulario['confirma_password']:
            flash('Las contraseñas no coinciden','registro')

        query = "SELECT * FROM users_hospital WHERE email = %(email)s"
        results = connectToMySQL('breast_cancer').query_db(query, formulario)
        if len(results) >= 1:
            flash('E-mail registrado previamente', 'registro')
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
    def get_by_id(cls, formulario):
        query = "SELECT * FROM users_hospital WHERE id = %(id)s"
        result = connectToMySQL('breast_cancer').query_db(query, formulario)
        user = cls(result[0])
        return user

    @classmethod
    def get_by_all(cls):
        query = "SELECT * FROM users_hospital"
        result = connectToMySQL('breast_cancer').query_db(query)
        user = []
        for i in result:
            user.append(cls(i))
        return user

    @classmethod
    def eliminar_hospital(cls, formulario):
        query = "DELETE FROM users_hospital WHERE id = %(id)s"
        result = connectToMySQL('breast_cancer').query_db(query, formulario)
        return result