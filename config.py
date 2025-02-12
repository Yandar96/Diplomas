import os

# Configuración general de Flask
SECRET_KEY = 'tu_clave_secreta'  # Cambia esto por una clave más segura

# Configuración de la base de datos MySQL
DB_HOST = 'localhost'  # Cambia esto si usas un servidor remoto
DB_USER = 'root'       # Usuario de MySQL
DB_PASSWORD = 'utilizar'  # Pon aquí la contraseña real
DB_NAME = 'diplomas'

# URI de conexión para MySQL
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuración de Flask-Login
REMEMBER_COOKIE_DURATION = 3600  # 1 hora de duración para la sesión

