import pandas as pd
import numpy as np
import os
import logging

# Configuración de rutas y carpetas
base_path = os.path.dirname(__file__)
archivo_sucio = os.path.join(base_path, '..', 'data', 'raw', 'data.csv')
archivo_limpio = os.path.join(base_path, '..', 'data', 'processed', 'vr_clean.csv')
carpeta_reportes = os.path.join(base_path, '..', 'reports')
archivo_reporte = os.path.join(carpeta_reportes, 'reporte_validacion.txt')

# Asegurar que existan las carpetas
os.makedirs(carpeta_reportes, exist_ok=True)
os.makedirs(os.path.dirname(archivo_limpio), exist_ok=True)

def validar_y_reportar():
    errores_encontrados = []
    advertencias_semanticas = []
    
    print("--- INICIANDO PROCESO DE VALIDACIÓN ---")
    
    try:
        if not os.path.exists(archivo_sucio):
            print(f"❌ Error: No se encuentra el archivo en {archivo_sucio}")
            return

        df = pd.read_csv(archivo_sucio)
        
        # 1. VALIDACIÓN ESTRUCTURAL
        columnas_requeridas = ['Age', 'Gender', 'VRHeadset', 'Duration', 'MotionSickness']
        for col in columnas_requeridas:
            if col not in df.columns:
                errores_encontrados.append(f"Falta la columna obligatoria: {col}")

        if errores_encontrados:
            print("\n❌ ERRORES ESTRUCTURALES DETECTADOS:")
            for err in errores_encontrados: print(f"   - {err}")
        else:
            print("✅ Estructura de columnas: OK")

            # 2. VALIDACIÓN SEMÁNTICA (Lógica de datos)
            # Chequeo de edades
            edades_invalidas = df[(df['Age'] < 0) | (df['Age'] > 110)]
            if not edades_invalidas.empty:
                advertencias_semanticas.append(f"Hay {len(edades_invalidas)} filas con edades imposibles.")

            # Chequeo de escala de mareo (0-10)
            mareo_invalido = df[(df['MotionSickness'] < 0) | (df['MotionSickness'] > 10)]
            if not mareo_invalido.empty:
                advertencias_semanticas.append(f"Hay {len(mareo_invalido)} filas con MotionSickness fuera de rango.")

            if advertencias_semanticas:
                print("\n⚠️ ADVERTENCIAS SEMÁNTICAS:")
                for adv in advertencias_semanticas: print(f"   - {adv}")
            else:
                print("✅ Lógica semántica: OK")

            # 3. PROCESAMIENTO Y LIMPIEZA
            df_clean = df.copy()
            df_clean = df_clean.drop_duplicates()
            df_clean['Age'] = pd.to_numeric(df_clean['Age'], errors='coerce').fillna(df_clean['Age'].median()).astype(int)
            df_clean['Gender'] = df_clean['Gender'].str.strip().str.capitalize()
            df_clean['VRHeadset'] = df_clean['VRHeadset'].str.strip().str.title()
            df_clean['Riesgo_Mareo'] = np.where(df_clean['MotionSickness'] >= 6, 'Alto Riesgo', 'Bajo Riesgo')

            # Guardar archivo limpio
            df_clean.to_csv(archivo_limpio, index=False)
            
            # 4. GENERAR ARCHIVO DE REPORTE
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                f.write("REPORTE FINAL DE VALIDACIÓN\n")
                f.write("===========================\n")
                f.write(f"Registros procesados: {len(df)}\n")
                f.write(f"Errores críticos: {len(errores_encontrados)}\n")
                f.write(f"Advertencias: {len(advertencias_semanticas)}\n\n")
                if advertencias_semanticas:
                    f.write("Detalle de advertencias:\n")
                    for adv in advertencias_semanticas: f.write(f"- {adv}\n")
                f.write("\nEstado final: ARCHIVO PROCESADO EXITOSAMENTE")

            print(f"\n✨ Proceso terminado.")
            print(f"📂 Archivo limpio: {archivo_limpio}")
            print(f"📄 Reporte generado: {archivo_reporte}")

    except Exception as e:
        print(f"❌ Error crítico durante la validación: {e}")

if __name__ == "__main__":
    validar_y_reportar()