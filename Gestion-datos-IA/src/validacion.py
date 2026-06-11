import pandas as pd
import numpy as np
import os
import logging
from sklearn.preprocessing import StandardScaler

# Configuración de rutas y carpetas
base_path = os.path.dirname(__file__)
archivo_sucio = os.path.join(base_path, '..', 'data', 'raw', 'abandono_escolar_dataset.csv')
archivo_limpio = os.path.join(base_path, '..', 'data', 'processed', 'abandono_escolar_procesado.csv')
carpeta_reportes = os.path.join(base_path, '..', 'reports')
archivo_reporte = os.path.join(carpeta_reportes, 'reporte_validacion.txt')

# Asegurar que existan las carpetas
os.makedirs(carpeta_reportes, exist_ok=True)
os.makedirs(os.path.dirname(archivo_limpio), exist_ok=True)

def validar_y_reportar():
    errores_encontrados = []
    advertencias_semanticas = []
    
    print("--- INICIANDO PROCESO DE VALIDACIÓN: ABANDONO ESCOLAR ---")
    
    try:
        if not os.path.exists(archivo_sucio):
            print(f"❌ Error: No se encuentra el archivo en {archivo_sucio}")
            return

        df = pd.read_csv(archivo_sucio)
        
        # 1. VALIDACIÓN ESTRUCTURAL
        # Verificamos las variables clave mencionadas en las instrucciones
        columnas_requeridas = ['abandono', 'beca', 'apoyo_sociofamiliar']
        for col in columnas_requeridas:
            if col not in df.columns:
                errores_encontrados.append(f"Falta la columna obligatoria: {col}")

        if errores_encontrados:
            print("\n❌ ERRORES ESTRUCTURALES DETECTADOS:")
            for err in errores_encontrados: print(f"   - {err}")
            # Si faltan columnas vitales como 'abandono', detenemos el proceso
            if any('abandono' in err for err in errores_encontrados):
                print("Error crítico: Falta la variable objetivo. Abortando limpieza.")
                return
        else:
            print("✅ Estructura de columnas: OK")

        # 2. VALIDACIÓN SEMÁNTICA (Lógica de datos)
        # Chequeo de la variable objetivo 'abandono' (asumiendo que debe ser binaria: 0 o 1)
        if 'abandono' in df.columns:
            valores_validos = [0, 1, True, False, 0.0, 1.0]
            abandono_invalido = df[~df['abandono'].isin(valores_validos)]
            if not abandono_invalido.empty:
                advertencias_semanticas.append(f"Hay {len(abandono_invalido)} filas con valores de 'abandono' no binarios.")

        # Chequeo general de valores nulos
        filas_con_nulos = df.isnull().any(axis=1).sum()
        if filas_con_nulos > 0:
            advertencias_semanticas.append(f"Se detectaron {filas_con_nulos} filas con valores nulos o faltantes.")

        if advertencias_semanticas:
            print("\n⚠️ ADVERTENCIAS SEMÁNTICAS:")
            for adv in advertencias_semanticas: print(f"   - {adv}")
        else:
            print("✅ Lógica semántica: OK")

        # 3. PROCESAMIENTO Y LIMPIEZA
        df_clean = df.copy()
        df_clean = df_clean.drop_duplicates()
        
        # Elimina identificadores innecesarios
        if 'id' in df_clean.columns:
            df_clean = df_clean.drop(columns=['id'])
            
        # Rellenar nulos numéricos con la mediana y categóricos con la moda (prevención)
        for col in df_clean.columns:
            if df_clean[col].dtype in ['int64', 'float64']:
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            else:
                df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0])

        # Identifica y transforma variables categóricas
        cat_cols = ['beca', 'apoyo_sociofamiliar']
        cat_cols_present = [col for col in cat_cols if col in df_clean.columns]
        if cat_cols_present:
            df_clean = pd.get_dummies(df_clean, columns=cat_cols_present, drop_first=True)

        # Normaliza las variables numéricas (excluyendo la variable objetivo)
        target_col = 'abandono'
        num_cols = df_clean.select_dtypes(include=['int64', 'float64']).columns
        num_cols = [col for col in num_cols if col != target_col]
        
        if len(num_cols) > 0:
            scaler = StandardScaler()
            df_clean[num_cols] = scaler.fit_transform(df_clean[num_cols])

        # Guardar archivo limpio
        df_clean.to_csv(archivo_limpio, index=False)
        
        # 4. GENERAR ARCHIVO DE REPORTE
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            f.write("REPORTE FINAL DE VALIDACIÓN: PREVISIÓN DE ABANDONO\n")
            f.write("==================================================\n")
            f.write(f"Registros procesados: {len(df_clean)}\n")
            f.write(f"Errores críticos de estructura: {len(errores_encontrados)}\n")
            f.write(f"Advertencias semánticas: {len(advertencias_semanticas)}\n\n")
            if advertencias_semanticas:
                f.write("Detalle de advertencias mitigadas:\n")
                for adv in advertencias_semanticas: f.write(f"- {adv}\n")
            f.write("\nEstado final: ARCHIVO LIMPIADO, TRANSFORMADO Y PROCESADO EXITOSAMENTE")

        print(f"\n✨ Proceso terminado.")
        print(f"📂 Archivo limpio y listo para el modelo: {archivo_limpio}")
        print(f"📄 Reporte generado: {archivo_reporte}")

    except Exception as e:
        print(f"Error crítico durante la validación: {e}")

if __name__ == "__main__":
    validar_y_reportar()