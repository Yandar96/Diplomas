import io
import fitz  
import database
from flask import Blueprint, send_file, jsonify
from datetime import datetime
import locale


locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
# Crear el Blueprint
generar_pdf_bp = Blueprint('generar_pdf', __name__, template_folder='templates')

def calcular_tamano_fuente_max(texto, rect, fontname="helv"):
    """Ajusta automáticamente el tamaño de fuente para que el texto encaje en el área."""
    x0, y0, x1, y1 = rect
    ancho_max = x1 - x0
    alto_max = y1 - y0

    fontsize = 5  # Tamaño inicial
    while True:
        ancho_texto = fitz.get_text_length(texto, fontsize=fontsize, fontname=fontname)
        alto_texto = fontsize * 1.2  # Estimación de altura del texto

        if ancho_texto > ancho_max or alto_texto > alto_max:
            fontsize -= 1
            break
        fontsize += 1

    return max(5, fontsize - 2)  # Reducimos un poco por seguridad

@generar_pdf_bp.route('/generar_pdf/<int:codDetalle>', methods=['GET'])
def generar_pdf(codDetalle):
    conn = database.get_db()
    cursor = conn.cursor()

    # Obtener los datos del estudiante y el curso
    cursor.execute("""
        SELECT p.nombreCompleto, dp.idPersona, c.nombre AS curso, c.diploma 
        FROM detallePersona dp
        JOIN persona p ON dp.idPersona = p.identificacion
        JOIN curso c ON dp.codCurso = c.codigo
        WHERE dp.codigo = %s
    """, (codDetalle,))
    
    datos = cursor.fetchone()

    if not datos:
        return jsonify({"error": "No se encontraron datos para el estudiante"}), 404

    nombre, idPersona, nombre_curso, ruta_pdf = datos  
    ruta_pdf_original = f"static/{ruta_pdf}"

    try:
        # Cargar el PDF en memoria
        doc = fitz.open(ruta_pdf_original)

        # Datos a modificar
        nombre, idPersona, nombre_curso, ruta_pdf = datos  # Orden correcto

        modificaciones = {
            "modificar nombre": nombre,
            "modificar programa": nombre_curso,
            "modificar documento": str(idPersona), 
            "modificar fecha": datetime.now().strftime("%d de %B de %Y"),
        }


        for page in doc:
            for palabra_original, nuevo_texto in modificaciones.items():
                areas = page.search_for(palabra_original)

                if not areas:
                    print(f"⚠ No se encontró el texto: {palabra_original}")
                    continue

                for rect in areas:
                    x0, y0, x1, y1 = rect
                    print(f"📌 Texto '{palabra_original}' encontrado en coordenadas: {rect}")

                    # Limpiar la zona (borrar cualquier residuo del texto)
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

                    # Ajustar el tamaño de la fuente
                    fontsize = calcular_tamano_fuente_max(nuevo_texto, rect)

                    # Calcular la posición centrada
                    ancho_texto = fitz.get_text_length(nuevo_texto, fontsize=fontsize, fontname="helv")
                    x_centrado = x0 + (x1 - x0 - ancho_texto) / 2
                    y_centrado = y0 + (y1 - y0 - fontsize) / 2 + fontsize

                    # Insertar el texto centrado
                    page.insert_text((x_centrado, y_centrado), nuevo_texto, fontsize=fontsize, fontname="helv", color=(0, 0, 0))

                    print(f"✅ Modificado: '{palabra_original}' → '{nuevo_texto}' (Tamaño final: {fontsize})")

        # Guardar el PDF en memoria
        output_pdf = io.BytesIO()
        doc.save(output_pdf)
        doc.close()
        output_pdf.seek(0)

    except FileNotFoundError:
        return jsonify({"error": "El diploma original no se encuentra"}), 404

    # Enviar el PDF modificado como descarga
    return send_file(output_pdf, as_attachment=True, download_name=f"diploma_{codDetalle}.pdf", mimetype="application/pdf")
