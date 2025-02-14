from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
from models.usuario import usuario_bp, get_user_by_id, get_user_by_username, verify_password
from models.curso import curso_bp
from models.diplomas import diplomas_bp  
from models.importar import importar_bp  
from models.persona import personas_bp
import database
from werkzeug.security import check_password_hash
from models.detalle_persona import detalle_persona_bp
from models.generar_pdf import generar_pdf_bp  # Importa el Blueprint del módulo generar_pdf
# from models.validar import validar_bp  Importa el Blueprint del módulo validar


app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'your_secret_key'

database.init_db()

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# Registrar los Blueprints
app.register_blueprint(usuario_bp, url_prefix='/usuarios')
app.register_blueprint(curso_bp, url_prefix='/cursos')
app.register_blueprint(diplomas_bp, url_prefix='/diplomas')
app.register_blueprint(importar_bp, url_prefix='/importar')  
app.register_blueprint(personas_bp, url_prefix='/personas')
app.register_blueprint(detalle_persona_bp, url_prefix='/detalle_persona')
app.register_blueprint(generar_pdf_bp,url_prefix='/generar_pdf')
# app.register_blueprint(validar_bp, url_prefix='/validar')



class Usuario(UserMixin):
    def __init__(self, id, username, password, rol):
        self.id = id
        self.username = username
        self.password = password
        self.rol = rol

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and verify_password(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
