import time
import psutil
import subprocess
import os

# Rutas a tus scripts (ajusta los nombres si los guardaste diferente)
# Rutas a tus scripts apuntando a la carpeta correcta
scripts_pipeline = [
    "src/limpieza.py", 
    "src/carga.py",
    "src/ingesta.py"
]

def registrar_metricas(etiqueta, inicio_tiempo, cpu_ini, ram_ini):
    fin_tiempo = time.time()
    cpu_fin = psutil.cpu_percent(interval=1)
    ram_fin = psutil.virtual_memory().percent
    
    tiempo_total = round(fin_tiempo - inicio_tiempo, 4)
    dif_cpu = round(cpu_fin - cpu_ini, 2)
    dif_ram = round(ram_fin - ram_ini, 2)
    
    print(f"\n--- Resultados para: {etiqueta} ---")
    print(f"⏱️ Tiempo de ejecución: {tiempo_total} segundos")
    print(f"⚙️ Variación CPU: {dif_cpu}% (Fin: {cpu_fin}%)")
    print(f"🧠 Variación RAM: {dif_ram}% (Fin: {ram_fin}%)")
    print("-" * 40)

def ejecutar_pipeline_completo():
    print("🚀 INICIANDO ANÁLISIS DE RENDIMIENTO DEL PIPELINE 🚀")
    
    # Medición global inicial
    cpu_global_ini = psutil.cpu_percent(interval=1)
    ram_global_ini = psutil.virtual_memory().percent
    tiempo_global_ini = time.time()
    
    # Ejecutar cada script y medir individualmente
    for script in scripts_pipeline:
        print(f"\nEjecutando: {script}...")
        if not os.path.exists(script):
            print(f"❌ Error: No se encontró el script {script}")
            continue
            
        t_ini = time.time()
        c_ini = psutil.cpu_percent(interval=0.5)
        r_ini = psutil.virtual_memory().percent
        
        try:
            # Ejecuta el script como si lo llamaras por consola
            subprocess.run(["python", script], check=True)
            registrar_metricas(script, t_ini, c_ini, r_ini)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al ejecutar {script}: {e}")
    
    # Medición global final
    print("\n=========================================")
    registrar_metricas("PIPELINE COMPLETO", tiempo_global_ini, cpu_global_ini, ram_global_ini)
    print("=========================================")

if __name__ == "__main__":
    ejecutar_pipeline_completo()