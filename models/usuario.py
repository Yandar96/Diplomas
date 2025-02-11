from flask import Blueprint, render_template, request, redirect, url_for, flash
import database
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id, username, password, rol):
        self.id = id
        self.username = username
        self.password = password
        self.rol = rol

def get_user_by_id(user_id):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, rol FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return Usuario(*user)
    return None

def get_user_by_username(username):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, rol FROM usuarios WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user:
        return Usuario(*user)
    return None

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

# 👇 Asegúrate de incluir esto para que `app.py` pueda importarlo correctamente
__all__ = ['usuario_bp', 'get_user_by_id', 'get_user_by_username', 'verify_password', 'Usuario']

class Usuario(UserMixin):
    def __init__(self, id, username, password, rol):
        self.id = id
        self.username = username
        self.password = password
        self.rol = rol

def get_user_by_id(user_id):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, rol FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return Usuario(*user)
    return None

def get_user_by_username(username):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, rol FROM usuarios WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user:
        return Usuario(*user)
    return None

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

usuario_bp = Blueprint('usuario', __name__, template_folder='templates')

@usuario_bp.route('/')
def listar_usuarios():
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, rol FROM usuarios")
    usuarios = cursor.fetchall()
    return render_template('usuarios/listar.html', usuarios=usuarios)

@usuario_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']
        hashed_password = generate_password_hash(password)

        conn = database.get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (%s, %s, %s)", 
                           (username, hashed_password, rol))
            conn.commit()
            flash('Usuario agregado con éxito', 'success')
            return redirect(url_for('usuario.listar_usuarios'))
        except:
            conn.rollback()
            flash('Error al agregar usuario', 'danger')
    return render_template('usuarios/agregar.html')

@usuario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    conn = database.get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nuevo_username = request.form['username']
        nuevo_rol = request.form['rol']
        try:
            cursor.execute("UPDATE usuarios SET username = %s, rol = %s WHERE id = %s", 
                           (nuevo_username, nuevo_rol, id))
            conn.commit()
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('usuario.listar_usuarios'))
        except:
            conn.rollback()
            flash('Error al actualizar el usuario', 'danger')

    cursor.execute("SELECT id, username, rol FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    return render_template('usuarios/editar.html', usuario=usuario)

@usuario_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    conn = database.get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()
        flash('Usuario eliminado con éxito', 'success')
    except:
        conn.rollback()
        flash('Error al eliminar el usuario', 'danger')
    return redirect(url_for('usuario.listar_usuarios'))
