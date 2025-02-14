import fitz  # PyMuPDF

def calcular_tamano_fuente_max(texto, rect, fontname="helv"):
    x0, y0, x1, y1 = rect
    ancho_max = x1 - x0
    alto_max = y1 - y0

    fontsize = 5  # Tamaño inicial
    while True:
        ancho_texto = fitz.get_text_length(texto, fontsize=fontsize, fontname=fontname)
        alto_texto = fontsize * 1.2  # Estimación de altura del texto

        if ancho_texto > ancho_max or alto_texto > alto_max:
            fontsize -= 1  # Reducimos si el texto se pasa
            break
        fontsize += 1

    return max(5, fontsize - 2)  # Reducimos un poco por seguridad

def modificar_texto_pdf(input_path, output_path, modificaciones):
    try:
        doc = fitz.open(input_path)

        for page in doc:
            for palabra_original, nuevo_texto in modificaciones.items():
                areas = page.search_for(palabra_original)

                if not areas:
                    print(f"⚠ No se encontró el texto: {palabra_original}")
                    continue

                for rect in areas:
                    x0, y0, x1, y1 = rect
                    print(f"📌 Texto '{palabra_original}' encontrado en coordenadas: {rect}")

                    # Limpiar la zona (borrar cualquier residuo del texto rojo)
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

        doc.save(output_path)
        doc.close()
        print(f"✅ PDF modificado guardado en: {output_path}")

    except Exception as e:
        print(f"❌ Error al modificar el PDF: {e}")

# 🔹 **Ejemplo de uso**
ruta_original = r"C:\Users\LENOVO\Documents\Proyectos Python\Proyecto_Diplomas\static\pdf\Diseno_diploma.pdf"
ruta_modificada = r"C:\Users\LENOVO\Documents\Proyectos Python\Proyecto_Diplomas\static\pdf\Diseno_diploma_modificado.pdf"

modificaciones = {
    "modificar nombre": "Yerson López",
    "modificar programa": "Análisis y Desarrollo de Software",
    "modificar fecha": "12 de febrero de 2025"
}

modificar_texto_pdf(ruta_original, ruta_modificada, modificaciones)
