import pandas as pd
import logging
import mysql.connector
from sqlalchemy import create_engine, text

# --- CONFIGURACIÓN DE LOGS ---
# Esto escribirá cualquier error en el archivo que ya tienes en tu estructura
logging.basicConfig(
    filename='logs/pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def conectar_y_cargar():
    # 1. Credenciales (Ajusta 'tu_password' por la tuya)
    USER = "root"
    PASS = "root"  # <-- PON AQUÍ TU CONTRASEÑA DE MYSQL
    HOST = "localhost"
    PORT = "3306"
    DB_NAME = "gestion" # Nombre de la base de datos que quieres
    
    # 2. CREAR LA BASE DE DATOS SI NO EXISTE
    # Usamos mysql-connector directamente para esta parte
    try:
        conn_previa = mysql.connector.connect(host=HOST, user=USER, password=PASS)
        cursor = conn_previa.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn_previa.close()
        print(f"✔ Base de datos '{DB_NAME}' verificada/creada.")
    except Exception as e:
        logging.error(f"Error conectando a MySQL: {e}")
        print("❌ No se pudo conectar a MySQL. Revisa tus credenciales.")
        return

    # 3. CONEXIÓN CON SQLALCHEMY PARA CARGA DE DATOS
    engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASS}@{HOST}:{PORT}/{DB_NAME}")

    try:
        # Cargar el archivo desde tu carpeta de datos procesados/validados
        # Ajusta el nombre del archivo según el que tengas en la imagen
        df = pd.read_csv("data/processed/vr_clean.csv")
        
        # --- VALIDACIÓN DE INTEGRIDAD (Ejemplo: No nulos en PK) ---
        if df.duplicated().any():
            logging.warning("Se detectaron duplicados en el CSV. Se filtrarán antes de la carga.")
            df = df.drop_duplicates()

        # 4. CARGA A LA TABLA
        # 'if_exists=append' respeta la estructura si ya existe
        df.to_sql(name='tabla_datos', con=engine, if_exists='append', index=False)
        
        msg_exito = f"✔ Carga exitosa: {len(df)} filas insertadas en '{DB_NAME}.tabla_datos'."
        print(msg_exito)
        logging.info(msg_exito)

    except Exception as e:
        error_msg = f"❌ ERROR EN LA CARGA: {str(e)}"
        print(error_msg)
        logging.error(error_msg)

if __name__ == "__main__":
    conectar_y_cargar()