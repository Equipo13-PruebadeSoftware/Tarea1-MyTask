from pymongo import MongoClient
from datetime import datetime
from logger import log_info, log_warning, log_error

client = MongoClient('mongodb://localhost:27017/')
db = client['task_manager']
tasks_collection = db['tasks']

def create_task(title, description, due_date, label):
    try:
        task = {
            'title': title,
            'description': description,
            'due_date': due_date,
            'label': label,
            'status': 'pendiente',
            'created_at': datetime.now()
        }
        tasks_collection.insert_one(task)
        log_info(f'Tarea creada: {title}')
    except Exception as e:
        log_error(f'Error al crear tarea: {e}')

def update_task():
    tasks = list_tasks_with_indices()
    
    if not tasks:
        print(f"No hay tareas")
        return

    try:
        task_num = int(input("Seleccione el número de la tarea que desea actualizar: "))
        selected_task = tasks[task_num - 1]
        
        updates = {}
        title = input(f"Nuevo título (actual: {selected_task['title']}, dejar vacío para no cambiar): ")
        if title:
            updates['title'] = title
        description = input(f"Nueva descripción (actual: {selected_task['description']}, dejar vacío para no cambiar): ")
        if description:
            updates['description'] = description
        due_date = input(f"Nueva fecha de vencimiento (actual: {selected_task['due_date']}, dejar vacío para no cambiar): ")
        if due_date:
            updates['due_date'] = due_date
        label = input(f"Nueva etiqueta (actual: {selected_task['label']}, dejar vacío para no cambiar): ")
        if label:
            updates['label'] = label
        
        tasks_collection.update_one({'_id': selected_task['_id']}, {'$set': updates})
        log_info(f'Tarea actualizada: {selected_task["_id"]}')
        print("Tarea actualizada exitosamente.")
    except (ValueError, IndexError):
        print("Selección inválida.")
        log_warning('Selección inválida en la actualización de tarea.')
    except Exception as e:
        log_error(f'Error al actualizar tarea: {e}')


def delete_task():
    tasks = list_tasks_with_indices()
    
    if not tasks:
        print(f"No hay tareas")
        return

    try:
        task_num = int(input("Seleccione el número de la tarea que desea eliminar: "))
        selected_task = tasks[task_num - 1]
        
        tasks_collection.delete_one({'_id': selected_task['_id']})
        log_info(f'Tarea eliminada: {selected_task["_id"]}')
        print("Tarea eliminada exitosamente.")
    except (ValueError, IndexError):
        print("Selección inválida.")
        log_warning('Selección inválida en la eliminación de tarea.')
    except Exception as e:
        log_error(f'Error al eliminar tarea: {e}')


def list_tasks(filters=None):
    try:
        query = filters if filters else {}
        tasks = tasks_collection.find(query)

        task_list = list(tasks)  # Convertimos el cursor en una lista

        if len(task_list) == 0:
            print("No se encontraron tareas.")
            log_info("No se encontraron tareas para listar.")
            return

        for task in task_list:
            print(f"\n{'-'*40}")
            print(f"ID: {task['_id']}")
            print(f"Título: {task['title']}")
            print(f"Descripción: {task['description']}")
            print(f"Fecha de vencimiento: {task['due_date']}")
            print(f"Etiqueta: {task['label']}")
            print(f"Estado: {task['status']}")
            print(f"Creado en: {task['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'-'*40}\n")
        
        log_info('Listado de tareas consultado')
    except Exception as e:
        log_error(f'Error al listar tareas: {e}')
        print("Ocurrió un error al listar las tareas.")



def change_task_status():
    tasks = list_tasks_with_indices()
    
    if not tasks:
        print(f"No hay tareas")
        return

    try:
        task_num = int(input("Seleccione el número de la tarea que desea cambiar de estado: "))
        selected_task = tasks[task_num - 1]
        
        print(f"Estado actual: {selected_task['status']}")
        new_status = input("Ingrese el nuevo estado (pendiente/en progreso/completada): ").strip().lower()

        if new_status in ['pendiente', 'en progreso', 'completada']:
            tasks_collection.update_one({'_id': selected_task['_id']}, {'$set': {'status': new_status}})
            log_info(f'Status de la tarea {selected_task["_id"]} cambiado a {new_status}')
            print("Estado de la tarea actualizado exitosamente.")
        else:
            print("Estado no válido.")
            log_warning('Intento de cambio a un estado no válido.')
    except (ValueError, IndexError):
        print("Selección inválida.")
        log_warning('Selección inválida en el cambio de estado de tarea.')
    except Exception as e:
        log_error(f'Error al cambiar estado de la tarea: {e}')


def list_tasks_with_indices(filters=None):
    query = filters if filters else {}
    tasks = tasks_collection.find(query)
    task_list = list(tasks)  # Convertimos el cursor en una lista para reutilizarla
    
    if len(task_list) == 0:
        print("No se encontraron tareas.")
        return []
    
    for idx, task in enumerate(task_list, start=1):
        print(f"[{idx}] {task['title']} (Estado: {task['status']})")
    
    return task_list


