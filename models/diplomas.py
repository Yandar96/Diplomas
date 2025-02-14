from flask import Blueprint, render_template,request
from models.detalle_persona import detalle_persona_bp
import database
diplomas_bp = Blueprint('diplomas', __name__, template_folder='templates')

@diplomas_bp.route('/descargar')
def descargar_diplomas():
    return render_template('diplomas/descargar.html')

@diplomas_bp.route('/ver')
def ver_diplomas():
    conn = database.get_db()
    cursor = conn.cursor()

    # Obtener parámetro de búsqueda  
    search_query = request.args.get('q', '').strip()

    # Query base para obtener los diplomas
    query = """
        SELECT dp.codigo, p.nombreCompleto, c.nombre AS curso
        FROM detallePersona dp
        JOIN persona p ON dp.idPersona = p.identificacion
        JOIN curso c ON dp.codCurso = c.codigo
    """

    params = ()
    # Agregar filtro de búsqueda si hay un query
    if search_query:
        query += " WHERE p.nombreCompleto LIKE %s OR p.matricula LIKE %s"
        params = (f"%{search_query}%", f"%{search_query}%")

    cursor.execute(query, params)
    diplomas = cursor.fetchall()
    return render_template('diplomas/ver_diplomas.html', diplomas=diplomas)
