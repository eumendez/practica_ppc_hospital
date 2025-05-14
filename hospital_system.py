import asyncio
import time
import random
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

# Definición de estados de los pacientes
class PatientStatus(Enum):
    WAITING_REGISTRATION = 0
    REGISTERED = 1
    WAITING_DIAGNOSIS = 2
    DIAGNOSED = 3
    WAITING_RESOURCE = 4
    IN_TREATMENT = 5
    READY_FOR_DISCHARGE = 6
    DISCHARGED = 7

# Definición de prioridades
class Priority(Enum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1
    CRITICAL = 0

@dataclass(order=True)
class Patient:
    priority: Priority = field(compare=True)
    id: int = field(compare=False)
    name: str = field(compare=False)
    symptoms: List[str] = field(compare=False, default_factory=list)
    status: PatientStatus = field(compare=False, default=PatientStatus.WAITING_REGISTRATION)
    registration_time: float = field(compare=False, default_factory=time.time)
    diagnosis: Dict[str, Any] = field(compare=False, default_factory=dict)
    assigned_resources: Dict[str, Any] = field(compare=False, default_factory=dict)
    
    def __str__(self):
        return f"Paciente {self.id} ({self.name}): {self.status.name}, Prioridad: {self.priority.name}"

# Recursos compartidos
class HospitalResources:
    def __init__(self, num_doctors=5, num_beds=10):
        # Locks y Semáforos para threading
        self.registration_lock = threading.Lock() 
        self.stats_lock = threading.Lock()

        # Locks y Semáforos para asyncio
        self.resource_lock = asyncio.Lock()
        self.doctors_semaphore = asyncio.Semaphore(num_doctors)
        self.beds_semaphore = asyncio.Semaphore(num_beds)
        
        # Colas
        self.diagnosis_queue = multiprocessing.Queue()
        self.discharge_queue = asyncio.Queue()
        
        # Contadores para estadísticas
        self.total_patients = 0
        self.processed_patients = 0
        self.avg_wait_time = 0.0

# 1. Proceso de Registro (Concurrente con Threads)
def register_patient(patient: Patient, resources: HospitalResources) -> None:
    """Registra al paciente en el sistema hospitalario (implementación concurrente)"""
    processing_time = random.uniform(0.5, 1.5)
    time.sleep(processing_time)
    
    with resources.registration_lock: # Protege total_patients y la asignación inicial
        resources.total_patients += 1
        severity = random.choice([p for p in Priority])
        patient.priority = severity
        patient.status = PatientStatus.REGISTERED
        print(f"Registrado: {patient}. Tiempo: {processing_time:.2f}s")
        
        resources.diagnosis_queue.put(patient)
    
    print(f"Paciente {patient.id} esperando diagnóstico. Prioridad: {patient.priority.name}")

# 2. Proceso de Diagnóstico (Paralelo con multiprocessing)
def run_diagnosis_worker(diagnosis_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):
    """Proceso trabajador para ejecutar diagnósticos en paralelo"""
    print(f"Worker de diagnóstico {multiprocessing.current_process().name} iniciado.")
    while True:
        try:
            patient = diagnosis_queue.get(timeout=1) # Timeout para permitir finalización
            if patient is None: # Terminar el proceso
                print(f"Worker de diagnóstico {multiprocessing.current_process().name} recibiendo centinela y terminando.")
                break
            
            patient.status = PatientStatus.WAITING_DIAGNOSIS # Actualizar estado
            processing_time = random.uniform(1, 3)
            time.sleep(processing_time)
            
            diagnosis = {
                'condition': random.choice(['Gripe', 'Fractura', 'Apendicitis', 'COVID-19', 'Migraña']),
                'severity': random.randint(1, 10),
                'recommended_treatment': random.choice(['Medicamentos', 'Cirugía', 'Observación', 'Terapia']),
                'processing_time': processing_time
            }
            
            patient.diagnosis = diagnosis
            patient.status = PatientStatus.DIAGNOSED
            
            result_queue.put(patient)
            print(f"Diagnóstico completado: Paciente {patient.id}, Condición: {diagnosis['condition']}")
        
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error en worker de diagnóstico {multiprocessing.current_process().name}: {e}")
            # Considerar si se debe re-encolar el paciente o manejar el error de otra forma
            time.sleep(0.1)
    print(f"Worker de diagnóstico {multiprocessing.current_process().name} finalizado.")


# 3. Asignación de Recursos (Asíncrono con asyncio)
async def allocate_resources(patient: Patient, resources: HospitalResources) -> None:
    """Asigna recursos como camas y médicos de forma asíncrona"""
    print(f"Intentando asignar recursos para paciente {patient.id} (Prioridad: {patient.priority.name})...")
    patient.status = PatientStatus.WAITING_RESOURCE
    
    # Simular solicitud a sistema externo (API) para verificar disponibilidad
    await asyncio.sleep(random.uniform(0.2, 0.8))
    
    assigned_doctor = None
    assigned_bed = None
    try:
        # Adquirir recursos necesarios
        print(f"Paciente {patient.id} esperando por doctor...")
        await resources.doctors_semaphore.acquire()
        assigned_doctor = {'id': random.randint(1000, 9999), 'speciality': random.choice(['General', 'Urgencias', 'Cirugía'])}
        print(f"Doctor {assigned_doctor['id']} asignado a Paciente {patient.id}.")

        print(f"Paciente {patient.id} esperando por cama...")
        await resources.beds_semaphore.acquire()
        assigned_bed = {'id': random.randint(100, 999), 'ward': random.choice(['General', 'Intensivos', 'Recuperación'])}
        print(f"Cama {assigned_bed['id']} asignada a Paciente {patient.id}.")

        async with resources.resource_lock:
            patient.assigned_resources = {
                'doctor': assigned_doctor,
                'bed': assigned_bed,
                'assignment_time': time.time()
            }
            patient.status = PatientStatus.IN_TREATMENT
        
        print(f"Recursos asignados: Paciente {patient.id}, Doctor {assigned_doctor['id']}, Cama {assigned_bed['id']}")
        
        # Simular tratamiento
        treatment_time = random.uniform(2, 5) # Reducido
        print(f"Paciente {patient.id} iniciando tratamiento ({treatment_time:.2f}s)...")
        await asyncio.sleep(treatment_time)
        
        patient.status = PatientStatus.READY_FOR_DISCHARGE
        await resources.discharge_queue.put(patient)
        print(f"Paciente {patient.id} listo para alta después de {treatment_time:.2f}s de tratamiento")

    except Exception as e:
        print(f"Error asignando recursos o durante tratamiento para Paciente {patient.id}: {e}")
        # Lógica de rollback: si se adquirieron algunos recursos, liberarlos
        if assigned_doctor: # Implica que el semáforo de doctor fue adquirido
            resources.doctors_semaphore.release()
            print(f"Doctor liberado para Paciente {patient.id} debido a error.")
        if assigned_bed: # Implica que el semáforo de cama fue adquirido
            resources.beds_semaphore.release()
            print(f"Cama liberada para Paciente {patient.id} debido a error.")
        

# 4. Proceso de Alta (Asíncrono con asyncio)
async def process_discharge(resources: HospitalResources) -> None:
    """Procesa altas de pacientes de forma asíncrona"""
    while True:
        try:
            patient = await resources.discharge_queue.get()
            
            discharge_time = random.uniform(0.5, 1)
            await asyncio.sleep(discharge_time)
            
            # Liberar recursos
            if 'doctor' in patient.assigned_resources and patient.assigned_resources['doctor']:
                resources.doctors_semaphore.release()
            if 'bed' in patient.assigned_resources and patient.assigned_resources['bed']:
                resources.beds_semaphore.release()
            
            patient.status = PatientStatus.DISCHARGED
            total_time_in_system = time.time() - patient.registration_time
            
            # Actualizar estadísticas
            with resources.stats_lock:
                resources.processed_patients += 1
                # Cálculo de media móvil
                resources.avg_wait_time = (
                    (resources.avg_wait_time * (resources.processed_patients - 1)) + total_time_in_system
                ) / resources.processed_patients
            
            print(f"Paciente {patient.id} dado de alta. Tiempo total en sistema: {total_time_in_system:.2f}s. Stats: {resources.processed_patients}/{resources.total_patients}, AvgTime: {resources.avg_wait_time:.2f}s")
            resources.discharge_queue.task_done()
        except asyncio.CancelledError:
            print("Proceso de alta cancelado.")
            break
        except Exception as e:
            print(f"Error en proceso de alta: {e}")
            


# Función principal para orquestar todo el flujo
async def hospital_simulation(num_patients: int, resources: HospitalResources):
    """Coordina toda la simulación del hospital"""
    diagnosis_result_queue = multiprocessing.Queue()
    num_processors = int(multiprocessing.cpu_count()*0.8) # 80% de los procesadores
    
    diagnosis_processes = []
    
    print(f"Iniciando {num_processors} procesos de diagnóstico...")
    for i in range(num_processors):
        p = multiprocessing.Process(
            target=run_diagnosis_worker, 
            args=(resources.diagnosis_queue, diagnosis_result_queue),
            name=f"DiagWorker-{i}"
        )
        
        p.start()
        diagnosis_processes.append(p)
    
    discharge_task = asyncio.create_task(process_discharge(resources))
    
    patients_to_register = [
        Patient(
            priority=Priority.MEDIUM,
            id=i,
            name=f"Paciente_{i}",
            symptoms=[random.choice(["Fiebre", "Dolor", "Tos", "Mareo", "Fractura"])]
        ) for i in range(1, num_patients + 1)
    ]
    
    # Iniciar proceso de registro (concurrente con ThreadPoolExecutor)
    print(f"Registrando {num_patients} pacientes...")
    with ThreadPoolExecutor(max_workers=5, thread_name_prefix="RegWorker") as executor:
        for patient in patients_to_register:
            executor.submit(register_patient, patient, resources)
    

    print("Todos los pacientes han sido enviados a registro. Esperando diagnósticos...")

    # Procesar resultados de diagnóstico y asignar recursos
    allocation_tasks = []
    diagnosis_collected_count = 0
    while diagnosis_collected_count < num_patients:
        try:
            # Esperar por resultados de diagnóstico (no bloqueante en el bucle de asyncio)
            if not diagnosis_result_queue.empty():
                diagnosed_patient = diagnosis_result_queue.get_nowait()
                diagnosis_collected_count += 1
                print(f"Recogido paciente diagnosticado: {diagnosed_patient.id} ({diagnosis_collected_count}/{num_patients})")
                # Asignar recursos de manera asíncrona
                task = asyncio.create_task(allocate_resources(diagnosed_patient, resources))
                allocation_tasks.append(task)
            else:
                # Si no hay nada en la cola, ceder control para que otras tareas asyncio puedan ejecutarse
                await asyncio.sleep(0.1) 
        except queue.Empty:
             await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error procesando cola de diagnóstico o iniciando asignación: {e}")
            await asyncio.sleep(0.1) # Pequeña pausa en caso de error
    
    print("Todos los diagnósticos recogidos y tareas de asignación de recursos creadas.")
    
    # Esperar a que todas las tareas de asignación de recursos y tratamiento terminen
    if allocation_tasks:
        await asyncio.gather(*allocation_tasks, return_exceptions=True)
    print("Todas las tareas de asignación de recursos y tratamiento completadas.")

    # Esperar a que todos los pacientes sean dados de alta
    print("Esperando a que todos los pacientes sean dados de alta...")
    # Esto se puede hacer esperando a que la cola de alta se vacíe y todas las tareas terminen
    await resources.discharge_queue.join() 
    print(f"Cola de alta vacía. Pacientes procesados: {resources.processed_patients}/{num_patients}")
    
    # Asegurar que la tarea de alta termine si aún no lo ha hecho
    if not discharge_task.done():
        discharge_task.cancel()
        try:
            await discharge_task
        except asyncio.CancelledError:
            print("Tarea de alta confirmada como cancelada.")

    # Limpiar procesos de diagnóstico
    print("Enviando centinelas a los workers de diagnóstico...")
    for _ in range(num_processors):
        resources.diagnosis_queue.put(None)
    
    print("Esperando a que los procesos de diagnóstico terminen...")
    for p in diagnosis_processes:
        p.join(timeout=5) # Esperar a que terminen limpiamente
        if p.is_alive():
            print(f"Proceso {p.name} no terminó, forzando terminación.")
            p.terminate() # Como último recurso

    # Mostrar estadísticas
    print("\n--- Estadísticas Finales del Hospital ---")
    print(f"Pacientes totales registrados: {resources.total_patients}")
    print(f"Pacientes totalmente procesados (dados de alta): {resources.processed_patients}")
    if resources.processed_patients > 0 :
        print(f"Tiempo promedio en sistema: {resources.avg_wait_time:.2f}s")
    else:
        print("No se procesaron pacientes para calcular tiempo promedio.")
    print("--------------------------------")

# Punto de entrada
if __name__ == "__main__":
    start_time = time.time()
    print("Iniciando simulación del sistema hospitalario...")
    
    # Configuración de la simulación
    NUM_PATIENTS_TO_SIMULATE = 30
    NUM_DOCTORS = 5
    NUM_BEDS = 10

    hospital_resources = HospitalResources(num_doctors=NUM_DOCTORS, num_beds=NUM_BEDS)
    
    asyncio.run(hospital_simulation(NUM_PATIENTS_TO_SIMULATE, hospital_resources))
    
    end_time = time.time()
    print(f"Simulación completada en {end_time - start_time:.2f} segundos.")