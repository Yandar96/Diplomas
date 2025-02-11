import mysql.connector
import config

def get_db():
    """Conexión a la base de datos"""
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )

def init_db():
    """Verifica la conexión a la base de datos"""
    try:
        conn = get_db()
        print("✅ Conexión a la base de datos establecida correctamente")
        conn.close()
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
