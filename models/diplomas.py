from flask import Blueprint, render_template

diplomas_bp = Blueprint('diplomas', __name__, template_folder='templates')

@diplomas_bp.route('/descargar')
def descargar_diplomas():
    return render_template('diplomas/descargar.html')

@diplomas_bp.route('/ver')
def ver_diplomas():
    return render_template('diplomas/ver.html')
