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
    """ Verifica si el archivo tiene una extensión permitida (PDF) """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(directory, filename):
    """ Genera un nombre de archivo único si ya existe uno con el mismo nombre """
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}({counter}){ext}"
        counter += 1

    return new_filename

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
            filename = get_unique_filename(UPLOAD_FOLDER, filename)  # Asegurar que no se sobrescriba
            archivo.save(os.path.join(UPLOAD_FOLDER, filename))
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

    # Obtener el curso actual para conocer su PDF actual
    cursor.execute("SELECT diploma FROM curso WHERE codigo = %s", (codigo,))
    curso_actual = cursor.fetchone()
    ruta_pdf_anterior = curso_actual[0] if curso_actual else None

    if request.method == 'POST':
        nombre = request.form['nombre']
        archivo = request.files['diploma']
        ruta_pdf = ruta_pdf_anterior  # Mantener el archivo anterior si no se sube uno nuevo

        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)
            ruta_pdf = os.path.join(UPLOAD_FOLDER, filename)

            # Si el archivo ya existe, agregar un número al final para evitar conflictos
            contador = 1
            base, extension = os.path.splitext(filename)
            while os.path.exists(ruta_pdf):
                filename = f"{base}_{contador}{extension}"
                ruta_pdf = os.path.join(UPLOAD_FOLDER, filename)
                contador += 1

            archivo.save(ruta_pdf)
            ruta_pdf = f"pdf/{filename}"

            # Eliminar el PDF anterior si existía
            if ruta_pdf_anterior and os.path.exists(os.path.join("static", ruta_pdf_anterior)):
                os.remove(os.path.join("static", ruta_pdf_anterior))

        # Actualizar la base de datos con el nuevo PDF
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
