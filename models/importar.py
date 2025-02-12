import os
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import database

importar_bp = Blueprint('importar', __name__, template_folder='templates')

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # Carpeta dentro del proyecto
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@importar_bp.route('/importar_estudiantes', methods=['GET', 'POST'])
def importar_estudiantes():
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nombre FROM curso")
    cursos = cursor.fetchall()
    cursos = [(curso[0], curso[1]) for curso in cursos]  # Asegurar estructura correcta
    return render_template('diplomas/importar.html', cursos=cursos)

@importar_bp.route('/procesar_excel', methods=['POST'])
def procesar_excel():
    if 'archivo' not in request.files:
        flash('No se seleccionó ningún archivo', 'danger')
        return redirect(url_for('importar.importar_estudiantes'))

    archivo = request.files['archivo']
    curso_seleccionado = request.form['curso']

    if archivo.filename == '':
        flash('No se seleccionó ningún archivo', 'danger')
        return redirect(url_for('importar.importar_estudiantes'))

    # Guardar el archivo en la carpeta del proyecto
    filename = secure_filename(archivo.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    archivo.save(filepath)

    try:
        # Leer archivo Excel y limpiar datos
        df = pd.read_excel(filepath, dtype=str)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df.replace('', None, inplace=True)
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)

        # Filtrar filas que tengan al menos 5 valores no vacíos
        df_filtrado = df.dropna(thresh=5)
        if df_filtrado.empty:
            flash("El archivo no contiene suficientes datos válidos.", "danger")
            return redirect(url_for('importar.importar_estudiantes'))

        # Omitir la primera fila útil después del filtrado
        df_filtrado = df_filtrado.iloc[1:]

        # Seleccionar solo las columnas 0, 5 y 11
        try:
            df_final = df_filtrado.iloc[:, [0, 5, 11]]
        except IndexError:
            flash("Error: El archivo no tiene suficientes columnas.", "danger")
            return redirect(url_for('importar.importar_estudiantes'))

        # Guardar en CSV dentro del proyecto (sobrescribiendo si ya existe)
        csv_path = os.path.join(UPLOAD_FOLDER, "datos_filtrados.csv")
        if os.path.exists(csv_path):
            os.remove(csv_path)

        df_final.to_csv(csv_path, index=False, header=False, encoding='utf-8-sig')

        flash('El archivo ha sido procesado y guardado automáticamente en la carpeta "uploads".', 'success')
        return redirect(url_for('importar.importar_estudiantes'))

    except Exception as e:
        flash(f'Error procesando el archivo: {str(e)}', 'danger')
        return redirect(url_for('importar.importar_estudiantes'))
