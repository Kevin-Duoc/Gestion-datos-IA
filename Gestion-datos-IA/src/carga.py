import pandas as pd
import logging
import mysql.connector
from sqlalchemy import create_engine
import os

# --- 1. CONFIGURACIÓN DE RUTAS Y LOGS ---
base_path = os.path.dirname(__file__)
archivo_limpio = os.path.join(base_path, '..', 'data', 'processed', 'abandono_escolar_procesado.csv')
log_path = os.path.join(base_path, '..', 'logs', 'pipeline.log')

# Asegurar que la carpeta de logs exista
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def conectar_y_cargar():
    logging.info("--- Iniciando fase de Carga (Load) en Base de Datos ---")
    print("Iniciando proceso de carga a MySQL...")

    # --- 2. CREDENCIALES DE LA BASE DE DATOS ---
    # ¡Importante! Ajusta 'root' y 'tu_password' según tu configuración local (ej. XAMPP, Workbench)
    USER = "root"
    PASS = "root"  # <-- CAMBIA ESTO SI TU MYSQL TIENE OTRA CONTRASEÑA O DÉJALO VACÍO "" SI NO TIENE
    HOST = "localhost"
    PORT = "3306"
    DB_NAME = "educacion_db"  # Nombre adaptado a la temática
    TABLE_NAME = "abandono_escolar" # Nombre de la tabla
    
    # --- 3. CREAR LA BASE DE DATOS SI NO EXISTE ---
    try:
        conn_previa = mysql.connector.connect(host=HOST, user=USER, password=PASS)
        cursor = conn_previa.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn_previa.close()
        print(f"✔ Base de datos '{DB_NAME}' verificada/creada.")
        logging.info(f"Base de datos '{DB_NAME}' operativa.")
    except Exception as e:
        logging.error(f"Error conectando al servidor MySQL: {e}")
        print("❌ No se pudo conectar a MySQL. ¿Está encendido el servidor (ej. XAMPP/WAMP)? Revisa tus credenciales.")
        return

    # --- 4. CONEXIÓN CON SQLALCHEMY PARA CARGA DE DATOS ---
    # Se crea el motor de conexión apuntando directamente a la base de datos recién creada
    engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASS}@{HOST}:{PORT}/{DB_NAME}")

    try:
        # Cargar el archivo procesado
        if not os.path.exists(archivo_limpio):
            print(f"❌ Error: No se encontró el archivo procesado en {archivo_limpio}")
            logging.error("Archivo procesado no encontrado para la carga.")
            return

        df = pd.read_csv(archivo_limpio)
        
        # Validación de integridad de última línea (doble chequeo)
        if df.duplicated().any():
            logging.warning("Se detectaron duplicados antes de cargar. Filtrando...")
            df = df.drop_duplicates()

        # --- 5. CARGA A LA TABLA ---
        # 'if_exists='replace'' sobrescribe la tabla si ya existe. 
        # (Puedes cambiarlo a 'append' si prefieres agregar datos sin borrar los anteriores)
        df.to_sql(name=TABLE_NAME, con=engine, if_exists='replace', index=False)
        
        msg_exito = f"✔ Carga exitosa: {len(df)} filas insertadas en la tabla '{DB_NAME}.{TABLE_NAME}'."
        print(msg_exito)
        logging.info(msg_exito)

    except Exception as e:
        error_msg = f"❌ ERROR EN LA CARGA A LA TABLA: {str(e)}"
        print(error_msg)
        logging.error(error_msg)

if __name__ == "__main__":
    conectar_y_cargar()