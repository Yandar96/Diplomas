import os
import database
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

curso_bp = Blueprint('curso', __name__, template_folder='templates')

UPLOAD_FOLDER = "static/pdf"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@curso_bp.route('/cursos', methods=['GET'])
def listar_cursos():
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM curso")
    cursos = cursor.fetchall()
    return render_template('cursos/listar.html', cursos=cursos)

@curso_bp.route('/cursos/crear', methods=['GET', 'POST'])
def crear_curso():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        archivo = request.files['diploma']

        ruta_pdf = ""
        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)
            ruta_pdf = os.path.join(UPLOAD_FOLDER, filename)
            archivo.save(ruta_pdf)
            ruta_pdf = f"pdf/{filename}"  # Guardamos solo la ruta relativa

        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO curso (codigo, nombre, diploma) VALUES (%s, %s, %s)", (codigo, nombre, ruta_pdf))
        conn.commit()
        flash('Curso creado con éxito', 'success')
        return redirect(url_for('curso.listar_cursos'))

    return render_template('cursos/agregar.html')

@curso_bp.route('/cursos/editar/<int:codigo>', methods=['GET', 'POST'])
def editar_curso(codigo):
    conn = database.get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        archivo = request.files['diploma']
        ruta_pdf = request.form['ruta_actual']  # Mantener el archivo anterior si no se sube uno nuevo

        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)
            ruta_pdf = os.path.join(UPLOAD_FOLDER, filename)
            archivo.save(ruta_pdf)
            ruta_pdf = f"pdf/{filename}"

        cursor.execute("UPDATE curso SET nombre = %s, diploma = %s WHERE codigo = %s", (nombre, ruta_pdf, codigo))
        conn.commit()
        flash('Curso actualizado con éxito', 'success')
        return redirect(url_for('curso.listar_cursos'))

    cursor.execute("SELECT * FROM curso WHERE codigo = %s", (codigo,))
    curso = cursor.fetchone()
    return render_template('cursos/editar.html', curso=curso)

@curso_bp.route('/cursos/eliminar/<int:codigo>', methods=['POST'])
def eliminar_curso(codigo):
    conn = database.get_db()
    cursor = conn.cursor()
    
    # Obtener la ruta del archivo antes de eliminar el curso
    cursor.execute("SELECT diploma FROM curso WHERE codigo = %s", (codigo,))
    curso = cursor.fetchone()
    if curso and curso[0]:
        try:
            os.remove(os.path.join("static", curso[0]))  # Eliminar archivo PDF si existe
        except FileNotFoundError:
            pass

    cursor.execute("DELETE FROM curso WHERE codigo = %s", (codigo,))
    conn.commit()
    flash('Curso eliminado con éxito', 'success')
    return redirect(url_for('curso.listar_cursos'))

# Ruta para ver el PDF desde la carpeta static/pdf/
@curso_bp.route('/ver_pdf/<filename>')
def ver_pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
