import pandas as pd
import numpy as np
import os
import logging
from sklearn.preprocessing import StandardScaler

# 1. Configurar los logs
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def limpiar_datos_abandono(ruta_entrada, ruta_salida):
    try:
        logging.info("--- Iniciando fase de limpieza: Abandono Escolar ---")
        print("Cargando y procesando el dataset de Abandono Escolar...")
        
        # Lee el csv [cite: 5]
        df = pd.read_csv(ruta_entrada)
        
        # 1. Elimina identificadores innecesarios 
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
            logging.info("Columna 'id' eliminada correctamente.")
            
        # Elimina duplicados (buena práctica heredada de tu script)
        df = df.drop_duplicates()
        
        # 2. Identifica y transforma variables categóricas 
        cat_cols = ['beca', 'apoyo_sociofamiliar']
        cat_cols_present = [col for col in cat_cols if col in df.columns]
        if cat_cols_present:
            df = pd.get_dummies(df, columns=cat_cols_present, drop_first=True)
            logging.info(f"One-hot encoding aplicado (get_dummies) a: {cat_cols_present} ")
            
        # 3. Normaliza las variables numéricas 
        target_col = 'abandono'
        if target_col in df.columns:
            # Selecciona columnas numéricas excluyendo la variable objetivo
            num_cols = df.select_dtypes(include=['int64', 'float64']).columns
            num_cols = [col for col in num_cols if col != target_col]
            
            if len(num_cols) > 0:
                scaler = StandardScaler()
                df[num_cols] = scaler.fit_transform(df[num_cols])
                logging.info(f"Variables numéricas normalizadas: {list(num_cols)} ")

        # 4. Guarda el archivo limpio en processed
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        df.to_csv(ruta_salida, index=False)
        
        logging.info(f"Limpieza y preprocesamiento exitosos. Archivo guardado en {ruta_salida}")
        print(f"Datos limpios, transformados y guardados en {ruta_salida}!")

    except Exception as e:
        logging.error(f"Error en la limpieza: {e}")
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    # Ruta al archivo que tenemos en raw [cite: 5]
    archivo_sucio = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'abandono_escolar_dataset.csv')
    
    # Ruta donde guardaremos el archivo listo para el modelo
    archivo_limpio = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'abandono_escolar_procesado.csv')
    
    limpiar_datos_abandono(archivo_sucio, archivo_limpio)