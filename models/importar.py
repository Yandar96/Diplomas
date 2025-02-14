import os
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import database
from models.persona import insertar_persona
from models.detalle_persona import insertar_detalle_persona

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
    return render_template('diplomas/importar.html', cursos=cursos)

@importar_bp.route('/procesar_excel', methods=['POST'])
def procesar_excel():
    if 'archivo' not in request.files:
        flash('No se seleccionó ningún archivo', 'danger')
        return redirect(url_for('importar.importar_estudiantes'))

    archivo = request.files['archivo']
    curso_seleccionado = request.form['curso'].split(" - ")[0]  # Extraer solo el código del curso

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
            df_final = df_filtrado.iloc[:, [0, 5, 11]]  # Asegúrate de seleccionar bien las columnas
            df_final.columns = [ 'nombreCompleto','identificacion', 'pago']  # Orden correcto
            df_final['identificacion'] = df_final['identificacion'].astype(str).str.strip()  # Asegurar que sean strings limpios
            df_final['pago'] = df_final['pago'].astype(str).str.strip()

        except IndexError:
            flash("Error: El archivo no tiene suficientes columnas.", "danger")
            return redirect(url_for('importar.importar_estudiantes'))

        conn = database.get_db()
        cursor = conn.cursor()

        # Insertar datos en la tabla persona
        for index, row in df_final.iterrows():
            insertar_persona(cursor, row['identificacion'], row['nombreCompleto'], row['pago'])

        # Insertar datos en la tabla detallePersona
        for index, row in df_final.iterrows():
            insertar_detalle_persona(cursor, row['identificacion'], curso_seleccionado)

        conn.commit()
        flash('Los datos han sido importados con éxito.', 'success')
        return redirect(url_for('importar.importar_estudiantes'))

    except Exception as e:
        flash(f'Error procesando el archivo: {str(e)}', 'danger')
        return redirect(url_for('importar.importar_estudiantes'))