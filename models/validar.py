# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
# import io
# from PIL import Image, ImageDraw, ImageFont, ImageFilter
# import random
# import string
# from database import get_db  # Importamos la función para conectar a la base de datos

# validar_bp = Blueprint('validar', __name__, template_folder='templates')

# @validar_bp.route('/captcha')
# def captcha():
#     # Generar una cadena aleatoria para el CAPTCHA con mayúsculas y minúsculas
#     captcha_text = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
#     session['captcha_answer'] = captcha_text

#     # Crear la imagen del CAPTCHA con fondo blanco
#     image_width = 310
#     image_height = 60
#     image = Image.new('RGB', (image_width, image_height), color=(255, 255, 255))
#     draw = ImageDraw.Draw(image)

#     # Usar una fuente TrueType (debes asegurarte de que la fuente esté disponible)
#     try:
#         font = ImageFont.truetype("arial.ttf", 28)
#     except IOError:
#         font = ImageFont.load_default()

#     x_position = 10
#     for char in captcha_text:
#         font_size = random.randint(15, 35)
#         try:
#             font = ImageFont.truetype("arial.ttf", font_size)
#         except IOError:
#             font = ImageFont.load_default()

#         angle = random.randint(-20, 40)
#         letter = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
#         letter_draw = ImageDraw.Draw(letter)
#         letter_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
#         letter_draw.text((10, 10), char, font=font, fill=letter_color)

#         letter = letter.rotate(angle, resample=Image.BICUBIC)
#         image.paste(letter, (x_position, random.randint(0, 20)), letter)
#         x_position += random.randint(40, 60)

#     # Añadir un filtro de desenfoque ligero
#     image = image.filter(ImageFilter.GaussianBlur(radius=1))

#     # Guardar la imagen en un buffer
#     img_io = io.BytesIO()
#     image.save(img_io, 'PNG')
#     img_io.seek(0)

#     return send_file(img_io, mimetype='image/png')


# @validar_bp.route('/validar', methods=['GET', 'POST'])
# def validar_id():
#     if request.method == 'POST':
#         user_answer = request.form.get('captcha_answer', '').strip()
#         correct_answer = session.get('captcha_answer')

#         if not user_answer or user_answer != correct_answer:
#             flash('Respuesta CAPTCHA incorrecta. Intenta de nuevo.', 'error')
#             return render_template('validar/validar.html')

#         id_ingresado = request.form['identificacion']

#         # Conectarse a la base de datos y hacer la consulta
#         conn = get_db()
#         cursor = conn.cursor(dictionary=True)

#         try:
#             cursor.execute("SELECT identificacion, nombreCompleto, pago FROM persona WHERE identificacion = %s", (id_ingresado,))
#             resultado = cursor.fetchone()
#         except Exception as e:
#             flash(f'Error al consultar la base de datos: {e}', 'error')
#             resultado = None
#         finally:
#             cursor.close()
#             conn.close()

#         if resultado:
#             return redirect(url_for('validar.filtro', identificacion=id_ingresado))
#         else:
#             flash('ID no encontrado. Intenta de nuevo.', 'error')
#             return redirect(url_for('validar.validar_id'))

#     return render_template('validar/validar.html')
# @validar_bp.route('/filtro', methods=['GET'])
# def filtro():
#     """
#     Muestra la información filtrada de la tabla 'informacion' según el ID ingresado.
#     """
#     id_ingresado = request.args.get('identificacion')

#     # Usamos la función get_db() para obtener la conexión
#     conn = get_db()
#     cur = conn.cursor()

#     if id_ingresado:
#         query = """SELECT dp.codigo, p.nombreCompleto, c.nombre AS curso
#         FROM detallePersona dp
#         JOIN persona p ON dp.idPersona = p.identificacion
#         JOIN curso c ON dp.codCurso = c.codigo WHERE dp.idpersona = %s"""
#         cur.execute(query, (id_ingresado,))
#     else:
#         query = "SELECT * FROM detallepersona"
#         cur.execute(query)

#     datos = cur.fetchall()
#     cur.close()
#     conn.close()  # Cerramos la conexión después de obtener los datos

#     return render_template('validar/filtro.html', datos=datos, id_ingresado=id_ingresado)