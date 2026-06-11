import os
import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

# --- 1. Configuración de Logs ---
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("=== Iniciando Pipeline de Procesamiento y Modelado ===")

# --- 2. Carga de datos ---
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'abandono_escolar_dataset.csv')
logging.info(f"Cargando datos desde: {file_path}")

try:
    df = pd.read_csv(file_path)
    logging.info(f"Datos cargados exitosamente. Forma del dataset: {df.shape}")
    
    # --- 3. Exploración preliminar ---
    logging.info(f"Proporción de la variable objetivo (abandono):\n{df['abandono'].value_counts(normalize=True).to_string()}")

    # --- 4. Preprocesamiento de datos ---
    logging.info("Iniciando preprocesamiento de datos...")
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
        logging.info("Columna 'id' eliminada.")

    cat_cols = ['beca', 'apoyo_sociofamiliar']
    cat_cols_present = [col for col in cat_cols if col in df.columns]
    if cat_cols_present:
        df = pd.get_dummies(df, columns=cat_cols_present, drop_first=True)
        logging.info(f"One-hot encoding aplicado a: {cat_cols_present}")

    X = df.drop(columns=['abandono'])
    y = df['abandono']

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    logging.info("Variables numéricas normalizadas.")

    # --- 5. División del conjunto de datos ---
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
    logging.info(f"Datos divididos: Entrenamiento ({X_train.shape[0]} filas), Prueba ({X_test.shape[0]} filas)")

    # --- 6. Construcción del modelo de clasificación ---
    logging.info("Entrenando el modelo de Regresión Logística...")
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    logging.info("Entrenamiento finalizado.")

    # --- 7. Evaluación del modelo ---
    logging.info("Evaluando el modelo con el conjunto de prueba...")
    y_pred = model.predict(X_test)

    matriz_conf = confusion_matrix(y_test, y_pred)
    reporte_clas = classification_report(y_test, y_pred)

    # Registramos los resultados en el log
    logging.info(f"Matriz de Confusión:\n{matriz_conf}")
    logging.info(f"Reporte de Clasificación:\n{reporte_clas}")
    
    # También lo imprimimos en consola para que lo veas al ejecutar
    print("¡Proceso completado con éxito! Revisa el archivo pipeline.log para ver los resultados.")
    print("\n--- Resumen Rápido ---")
    print(reporte_clas)

except Exception as e:
    logging.error(f"Ocurrió un error durante la ejecución: {e}")
    print(f"Error: {e}")