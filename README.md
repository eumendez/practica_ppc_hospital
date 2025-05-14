# Sistema de Simulación de Departamento de Emergencias Hospitalarias

Esta simulación implementa un departamento de emergencias hospitalarias completo utilizando múltiples paradigmas de programación: concurrente, paralelo y asíncrono. El proyecto muestra cómo aplicar diferentes enfoques de programación según las características de cada tarea.

## Descripción del Sistema

El sistema simula el flujo completo de pacientes a través de un hospital:

1. **Registro** (Concurrente - Threads)
   - Múltiples pacientes pueden registrarse simultáneamente
   - Sistema de prioridades basado en condiciones médicas
   - Utiliza `ThreadPoolExecutor` para operaciones concurrentes

2. **Diagnóstico** (Paralelo - Multiprocessing)
   - Simulación de procesamiento intensivo de modelos de IA
   - Aprovecha múltiples núcleos para procesar diagnósticos en paralelo
   - Implementa comunicación inter-proceso mediante colas

3. **Asignación de Recursos** (Asíncrono - Asyncio)
   - Simula APIs externas y latencia de red sin bloquear el sistema
   - Adquisición concurrente de múltiples recursos (doctores y camas)
   - Manejo asíncrono de tareas con dependencias

4. **Tratamiento y Alta** (Asíncrono/Concurrente)
   - Sistema de colas
   - Mecanismos robustos para liberación de recursos
   - Control de concurrencia para actualización de estadísticas

## Paradigmas Implementados

| Componente | Paradigma | Implementación | Justificación |
|------------|-----------|----------------|--------------|
| Registro | Concurrente | `ThreadPoolExecutor` | Operaciones ligeras de I/O que no requieren paralelismo real |
| Diagnóstico | Paralelo | `multiprocessing` | Tareas intensivas de CPU que se benefician del paralelismo verdadero |
| Asignación de Recursos | Asíncrono | `asyncio` | Operaciones de I/O con tiempos de espera donde el asincronismo evita bloqueos |
| Control de Recursos | Concurrencia | `Lock`, `Semaphore` | Gestión segura de recursos compartidos |
| Manejo de Errores | Todos | `try/except`, rollback | Garantiza robustez del sistema en casos excepcionales |

## Características Avanzadas

- **Control robusto de ciclo de vida**: Finalización adecuada de procesos mediante centinelas
- **Manejo de errores completo**: Rollback de recursos y recuperación de fallos
- **Sincronización precisa**: Distinción entre mecanismos de threading y asyncio
- **Monitoreo detallado**: Trazabilidad del flujo de pacientes y recursos
- **Escalabilidad**: Configuración ajustable de pacientes y recursos

## Requisitos

- Python 3.7+
- Dependencias:
  - matplotlib>=3.5.0 (para visualizaciones de rendimiento)
  - numpy>=1.20.0 (para análisis de datos)

## Ejecución

Para ejecutar la simulación básica:

```bash
python hospital_system.py
```

Para ejecutar pruebas de rendimiento y generar gráficos:

```bash
python test_performance.py
```

## Estructura del Proyecto

- `hospital_system.py`: Implementación principal del sistema
- `test_performance.py`: Pruebas de rendimiento y generación de gráficos
- `diagrama.excalidraw`: Diagrama del sistema
- `README.md`: Esta documentación
- `requirements.txt`: Dependencias del proyecto

## Personalización

Puedes ajustar la simulación modificando estos parámetros en `hospital_system.py`:

```python
# Configuración de la simulación
NUM_PATIENTS_TO_SIMULATE = 30  # Número de pacientes
NUM_DOCTORS = 5                # Número de doctores
NUM_BEDS = 10                  # Número de camas
```

## Documentación de Paradigmas

### Concurrencia vs Paralelismo vs Asincronía

- **Concurrencia (Threads)**: 
  - Permite que múltiples tareas progresen en intervalos superpuestos
  - Ideal para operaciones de I/O ligeras donde el paralelismo real no es necesario
  - Implementado con `ThreadPoolExecutor` y `threading.Lock`

- **Paralelismo (Multiprocessing)**:
  - Ejecuta múltiples tareas simultáneamente utilizando múltiples núcleos
  - Óptimo para tareas intensivas de CPU como procesamiento de diagnósticos
  - Implementado con `multiprocessing.Process` y comunicación mediante colas

- **Asincronía (Asyncio)**:
  - Permite que una tarea continúe mientras espera por operaciones de I/O
  - Perfecto para simulación de latencia en APIs y coordinación de tareas
  - Implementado con `asyncio.gather`, `asyncio.create_task` y `asyncio.Semaphore`

## Contribución al Informe

Este código y documentación están diseñados para ayudar con un proyecto académico. Recuerda:

1. Usar `test_performance.py` para generar datos y gráficos de rendimiento
2. Analizar la eficacia de cada paradigma según el tipo de tarea
3. Documentar los desafíos encontrados y soluciones implementadas
