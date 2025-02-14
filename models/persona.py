from flask import Blueprint, request
import database

personas_bp = Blueprint('personas', __name__, template_folder='templates')


def insertar_persona(cursor, identificacion, nombreCompleto, pago):
    try:
        cursor.execute("SELECT identificacion FROM persona WHERE identificacion = %s", (identificacion,))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute(
                "INSERT INTO persona (identificacion, nombreCompleto, pago) VALUES (%s, %s, %s)",
                (identificacion, nombreCompleto, pago)
            )
    except Exception as e:
        print(f"Error al insertar persona: {e}")
