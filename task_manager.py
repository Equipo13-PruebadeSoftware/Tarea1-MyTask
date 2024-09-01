from pymongo import MongoClient
from datetime import datetime
from logger import log_info, log_warning, log_error

client = MongoClient('mongodb://localhost:27017/')
db = client['task_manager']
tasks_collection = db['tasks']

def create_task(title, description, due_date, label, username):
    task = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "label": label,
        "status": "pendiente",  # Estado inicial
        "created_at": datetime.now(),
        "username": username  # Asociar la tarea al usuario
    }
    try:
        tasks_collection.insert_one(task)
        log_info(f'Tarea creada para el usuario {username}')
        print("Tarea creada exitosamente.")
    except Exception as e:
        log_error(f'Error al crear tarea: {e}')


def update_task(username):
    tasks = list_tasks_with_indices(username)
    
    if not tasks:
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
        log_info(f'Tarea actualizada: {selected_task["_id"]} por el usuario {username}')
        print("Tarea actualizada exitosamente.")
    except (ValueError, IndexError):
        print("Selección inválida.")
        log_warning(f'Selección inválida en la actualización de tarea para el usuario {username}.')
    except Exception as e:
        log_error(f'Error al actualizar tarea para el usuario {username}: {e}')


def delete_task(username):
    try:
        # Listar tareas con índices
        tasks = list_tasks_with_indices(username)
        
        if not tasks:
            return  # Salir si no hay tareas para eliminar

        # Solicitar al usuario que seleccione una tarea para eliminar
        task_num = int(input("Seleccione el número de la tarea que desea eliminar: "))
        
        # Validar selección
        if task_num < 1 or task_num > len(tasks):
            print("Selección inválida.")
            return

        selected_task = tasks[task_num - 1]
        task_id = selected_task['_id']
        
        # Confirmar eliminación
        confirmation = input(f"¿Está seguro de que desea eliminar la tarea '{selected_task['title']}'? (s/n): ").lower()
        if confirmation == 's':
            tasks_collection.delete_one({'_id': task_id})
            log_info(f'Tarea eliminada: {task_id} por el usuario {username}')
            print("Tarea eliminada exitosamente.")
        else:
            print("Eliminación cancelada.")
    except (ValueError, IndexError):
        print("Selección inválida.")
        log_warning(f'Selección inválida en la eliminación de tarea para el usuario {username}.')
    except Exception as e:
        log_error(f'Error al eliminar tarea para el usuario {username}: {e}')
        print("Ocurrió un error al eliminar la tarea.")



def list_tasks(username, filters=None):
    try:
        query = filters if filters else {}
        query["username"] = username  # Filtrar por usuario
        tasks = tasks_collection.find(query)

        task_list = list(tasks)  # Convertir el cursor en una lista
        
        if len(task_list) == 0:
            print("No se encontraron tareas.")
            log_info(f"No se encontraron tareas para el usuario {username}.")
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
        
        log_info(f'Listado de tareas consultado para el usuario {username}')
    except Exception as e:
        log_error(f'Error al listar tareas para el usuario {username}: {e}')
        print("Ocurrió un error al listar las tareas.")



def change_task_status(username):
    try:
        # Listar tareas con índices
        tasks = list_tasks_with_indices(username)
        
        if not tasks:
            return  # Salir si no hay tareas para cambiar el estado

        # Solicitar al usuario que seleccione una tarea para cambiar su estado
        task_num = int(input("Seleccione el número de la tarea cuyo estado desea cambiar: "))
        
        # Validar selección
        if task_num < 1 or task_num > len(tasks):
            print("Selección inválida.")
            return

        selected_task = tasks[task_num - 1]
        task_id = selected_task['_id']
        
        # Mostrar el estado actual y solicitar el nuevo estado
        print(f"Estado actual de '{selected_task['title']}': {selected_task['status']}")
        new_status = input("Ingrese el nuevo estado (pendiente, en progreso, completada): ").lower()

        if new_status in ['pendiente', 'en progreso', 'completada']:
            tasks_collection.update_one({'_id': task_id}, {'$set': {'status': new_status}})
            log_info(f'Estado de tarea actualizado: {task_id} por el usuario {username} a {new_status}')
            print("Estado de la tarea actualizado exitosamente.")
        else:
            print("Estado no válido.")
            log_warning(f'Intento de actualizar a un estado no válido para la tarea {task_id} por el usuario {username}.')
    except (ValueError, IndexError):
        print("Selección inválida.")
        log_warning(f'Selección inválida en el cambio de estado de tarea para el usuario {username}.')
    except Exception as e:
        log_error(f'Error al cambiar el estado de la tarea para el usuario {username}: {e}')
        print("Ocurrió un error al cambiar el estado de la tarea.")



def list_tasks_with_indices(username, filters=None):
    try:
        # Asegurarse de que filters sea un diccionario, si no se pasa nada se crea un diccionario vacío
        query = filters if filters else {}
        query["username"] = username  # Filtrar por el nombre de usuario

        tasks = tasks_collection.find(query)

        task_list = list(tasks)  # Convertimos el cursor en una lista

        if len(task_list) == 0:
            print("No se encontraron tareas.")
            log_info(f"No se encontraron tareas para el usuario {username}.")
            return []

        # Mostrar tareas con índices
        for i, task in enumerate(task_list, start=1):
            print(f"{i}. Título: {task['title']}, Descripción: {task['description']}, Estado: {task['status']}")

        return task_list

    except Exception as e:
        log_error(f'Error al listar tareas para el usuario {username}: {e}')
        print("Ocurrió un error al listar las tareas.")
        return []



