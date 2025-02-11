from flask import Blueprint, render_template, request
import database

personas_bp = Blueprint('personas', __name__, template_folder='templates')

@personas_bp.route('/ver_diplomas')
def ver_diplomas():
    conn = database.get_db()
    cursor = conn.cursor()

    # Obtener parámetro de búsqueda
    search_query = request.args.get('q', '').strip()

    # Query base
    query = """
        SELECT dp.codigo, p.identificacion AS idPersona, p.nombreCompleto AS nombrePersona, 
        c.codigo AS codigoCurso, c.nombre AS nombreCurso
        FROM detallePersona dp
        JOIN persona p ON dp.idPersona = p.identificacion
        JOIN curso c ON dp.codCurso = c.codigo;

    """
    params = ()

    # Agregar filtro de búsqueda
    if search_query:
        query += " WHERE p.nombre LIKE %s OR c.nombre LIKE %s OR dp.codigo LIKE %s"
        params = (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%")

    cursor.execute(query, params)
    diplomas = cursor.fetchall()

    return render_template('diplomas/ver_diplomas.html', diplomas=diplomas)
