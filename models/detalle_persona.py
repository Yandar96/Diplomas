from flask import Blueprint, render_template, request
import database

detalle_persona_bp = Blueprint('detalle_persona', __name__, template_folder='templates')

diplomas_bp = Blueprint('diplomas', __name__, template_folder='templates')

def insertar_detalle_persona(cursor, idPersona, codCurso):
    try:
        cursor.execute(
            "INSERT INTO detallePersona (idPersona, codCurso) VALUES (%s, %s)",
            (idPersona, codCurso)
        )
    except Exception as e:
        print(f"Error al insertar en detallePersona: {e}")
