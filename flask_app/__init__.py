from flask import Flask

app = Flask(__name__)
app.secret_key = 'mi llave super secreta'
#Secret key

app.config['UPLOAD_FOLDER'] = 'flask_app/static/exam/'

