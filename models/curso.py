from flask import Blueprint, render_template, request, redirect, url_for, flash
import database

curso_bp = Blueprint('curso', __name__, template_folder='templates')

@curso_bp.route('/')
def listar_cursos():
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nombre FROM curso")  # ❌ No uses `id`
    cursos = cursor.fetchall()
    return render_template('cursos/listar.html', cursos=cursos)



@curso_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_curso():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        conn = database.get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO curso (codigo, nombre) VALUES (%s, %s)", 
                           (codigo, nombre))
            conn.commit()
            flash('Curso agregado con éxito', 'success')
            return redirect(url_for('curso.listar_cursos'))
        except:
            conn.rollback()
            flash('Error al agregar curso', 'danger')

    return render_template('cursos/agregar.html')

@curso_bp.route('/editar/<int:codigo>', methods=['GET', 'POST'])
def editar_curso(codigo):
    conn = database.get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        try:
            cursor.execute("UPDATE curso SET nombre = %s WHERE codigo = %s", 
                           (nuevo_nombre, codigo))
            conn.commit()
            flash('Curso actualizado correctamente', 'success')
            return redirect(url_for('curso.listar_cursos'))
        except:
            conn.rollback()
            flash('Error al actualizar el curso', 'danger')

    cursor.execute("SELECT codigo, nombre FROM curso WHERE codigo = %s", (codigo,))
    curso = cursor.fetchone()
    return render_template('cursos/editar.html', curso=curso)

@curso_bp.route('/eliminar/<int:codigo>', methods=['POST'])
def eliminar_curso(codigo):
    conn = database.get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM curso WHERE codigo = %s", (codigo,))
        conn.commit()
        flash('Curso eliminado correctamente', 'success')
    except:
        conn.rollback()
        flash('Error al eliminar el curso', 'danger')

    return redirect(url_for('curso.listar_cursos'))


# Asegurar que el módulo exporta `curso_bp`
__all__ = ['curso_bp']
