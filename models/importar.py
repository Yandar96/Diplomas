import os
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import database

importar_bp = Blueprint('importar', __name__, template_folder='templates')

UPLOAD_FOLDER = "uploads"
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
    if archivo.filename == '':
        flash('No se seleccionó ningún archivo', 'danger')
        return redirect(url_for('importar.importar_estudiantes'))

    filename = secure_filename(archivo.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    archivo.save(filepath)

    try:
        # Cargar sin saltar filas y ver qué hay en el archivo
        df = pd.read_excel(filepath)

        # Mostrar todas las columnas y las primeras filas para depuración
        print("Columnas del archivo Excel:", df.columns)
        print("Primeras filas antes del filtrado:")
        print(df.head(10))  # Muestra 10 filas para ver la estructura

        # Si solo hay una columna, el Excel no está estructurado correctamente
        if len(df.columns) == 1:
            flash("El archivo parece no tener columnas estructuradas. Verifica el formato.", "danger")
            return redirect(url_for('importar.importar_estudiantes'))

        # Eliminar columnas sin nombre
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Filtrar filas con menos de 3 valores válidos (ajustar si es necesario)
        df_filtrado = df.dropna(thresh=3)

        # Si después del filtrado queda vacío, mostrar error
        if df_filtrado.empty:
            flash("El archivo no contiene datos válidos después del filtrado.", "danger")
            return redirect(url_for('importar.importar_estudiantes'))

        # Eliminar espacios en blanco en todas las celdas
        df_filtrado = df_filtrado.map(lambda x: x.strip() if isinstance(x, str) else x)

        # Mostrar las primeras filas después del filtrado
        print("Primeras filas después del filtrado:")
        print(df_filtrado.head())

        # Seleccionar solo las columnas necesarias
        try:
            df_final = df_filtrado.iloc[:, [0, 5, 10]]  # Ajusta según sea necesario
            df_final.columns = ["Nombre", "Número", "Estado"]
        except IndexError as e:
            flash(f"Error seleccionando columnas: {str(e)}", "danger")
            return redirect(url_for('importar.importar_estudiantes'))

        # Guardar en CSV
        csv_path = os.path.join(UPLOAD_FOLDER, "datos_filtrados.csv")
        df_final.to_csv(csv_path, index=False)

        flash('Archivo procesado con éxito', 'success')
        return send_file(csv_path, as_attachment=True)

    except Exception as e:
        flash(f'Error procesando el archivo: {str(e)}', 'danger')
        return redirect(url_for('importar.importar_estudiantes'))
