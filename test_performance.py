import time
import asyncio
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Matplotlib no encontrado. Instalando...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
        import matplotlib.pyplot as plt
        print("Matplotlib instalado")
    except Exception as e:
        print(f"Error instalando Matplotlib")
        print("Por favor instala Matplotlib manualmente: pip install matplotlib")
try:
    import numpy as np
except ImportError:
    print("NumPy no encontrado. Instalando")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
        import numpy as np
        print("NumPy instalado")
    except Exception as e:
        print(f"Error instalando numpy: {e}")
        print("Por favor instala numpy manualmente: pip install numpy")
from hospital_system import HospitalResources, hospital_simulation
import subprocess
import sys
import os

async def run_simulation_with_params(num_patients, num_doctors, num_beds):
    """Ejecuta una simulación con parámetros específicos y devuelve métricas"""
    start_time = time.time()
    
    resources = HospitalResources(num_doctors=num_doctors, num_beds=num_beds)
    await hospital_simulation(num_patients, resources)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return {
        "total_time": total_time,
        "avg_wait_time": resources.avg_wait_time,
        "patients": num_patients,
        "doctors": num_doctors,
        "beds": num_beds,
        "throughput": num_patients / total_time
    }

async def test_patient_scaling():
    """Prueba el rendimiento con diferente número de pacientes"""
    results = []
    
    # Probar con diferentes cantidades de pacientes
    patient_counts = [5, 10, 15, 20, 30]
    
    for count in patient_counts:
        print(f"\n--- Prueba con {count} pacientes ---")
        result = await run_simulation_with_params(count, 5, 10)
        results.append(result)
        print(f"Tiempo total: {result['total_time']:.2f}s, Tiempo promedio por paciente: {result['avg_wait_time']:.2f}s")
    
    return results

async def test_resource_scaling():
    """Prueba el rendimiento con diferentes cantidades de recursos"""
    results = []
    
    # Número fijo de pacientes
    num_patients = 20
    
    # Diferentes configuraciones de recursos (doctores, camas)
    resource_configs = [(2, 4), (3, 6), (5, 10), (8, 16), (10, 20)]
    
    for doctors, beds in resource_configs:
        print(f"\n--- Prueba con {doctors} doctores y {beds} camas ---")
        result = await run_simulation_with_params(num_patients, doctors, beds)
        results.append(result)
        print(f"Tiempo total: {result['total_time']:.2f}s, Tiempo promedio por paciente: {result['avg_wait_time']:.2f}s")
    
    return results

def visualize_results(patient_results, resource_results):
    """Visualiza los resultados de las pruebas de rendimiento"""
    plt.figure(figsize=(15, 10))
    
    # Gráfico 1: Escalabilidad de pacientes
    plt.subplot(2, 2, 1)
    patients = [r['patients'] for r in patient_results]
    times = [r['total_time'] for r in patient_results]
    
    plt.plot(patients, times, 'o-', label='Tiempo Total')
    plt.xlabel('Número de Pacientes')
    plt.ylabel('Tiempo Total (s)')
    plt.title('Escalabilidad con Número de Pacientes')
    plt.grid(True)
    
    # Gráfico 2: Tiempo promedio por paciente
    plt.subplot(2, 2, 2)
    avg_times = [r['avg_wait_time'] for r in patient_results]
    
    plt.plot(patients, avg_times, 'o-', label='Tiempo Promedio')
    plt.xlabel('Número de Pacientes')
    plt.ylabel('Tiempo Promedio por Paciente (s)')
    plt.title('Tiempo de Espera Promedio por Paciente')
    plt.grid(True)
    
    # Gráfico 3: Impacto de recursos en tiempo total
    plt.subplot(2, 2, 3)
    resources = [f"{r['doctors']}D/{r['beds']}C" for r in resource_results]
    times = [r['total_time'] for r in resource_results]
    
    plt.bar(resources, times)
    plt.xlabel('Configuración de Recursos (Doctores/Camas)')
    plt.ylabel('Tiempo Total (s)')
    plt.title('Impacto de Recursos en Tiempo Total')
    
    # Gráfico 4: Throughput
    plt.subplot(2, 2, 4)
    throughput_patients = [r['throughput'] for r in patient_results]
    throughput_resources = [r['throughput'] for r in resource_results]
    
    plt.plot(patients, throughput_patients, 'o-', label='Por Pacientes')
    plt.xlabel('Número de Pacientes')
    plt.ylabel('Pacientes por segundo')
    plt.title('Throughput del Sistema')
    plt.grid(True)
    
    plt.tight_layout()
    os.makedirs('images', exist_ok=True)
    plt.savefig('images/performance_results.png')
    plt.close()
    
    print("Gráficos de rendimiento guardados en 'performance_results.png'")

async def main():
    print("Iniciando pruebas de rendimiento del sistema hospitalario...")
    
    print("\n=== PRUEBAS DE ESCALABILIDAD DE PACIENTES ===")
    patient_results = await test_patient_scaling()
    
    print("\n=== PRUEBAS DE ESCALABILIDAD DE RECURSOS ===")
    resource_results = await test_resource_scaling()
    
    print("\n=== GENERANDO VISUALIZACIONES ===")
    visualize_results(patient_results, resource_results)
    
    print("\nPruebas de rendimiento completadas.")

if __name__ == "__main__":
    asyncio.run(main()) 