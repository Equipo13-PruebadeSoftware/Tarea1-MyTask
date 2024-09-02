from pymongo import MongoClient
from datetime import datetime
from logger import log_info, log_warning, log_error
from datetime import datetime
import json
import re

# Conectar con base de datos
client = MongoClient('mongodb://mongo:27017/')
db = client['task_manager']
tasks_collection = db['tasks'] # Colección para tareas

# Función para cargar etiquetas desde un archivo JSON
def load_labels(filename="/data/labels.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            return data.get("labels", [])
    except FileNotFoundError:
        print("Archivo de etiquetas no encontrado. Usando etiquetas por defecto.")
        return ["urgente", "personal", "trabajo", "proyecto", "sin etiqueta"]
    except json.JSONDecodeError:
        print("Error al leer el archivo de etiquetas. Usando etiquetas por defecto.")
        return ["urgente", "personal", "trabajo", "proyecto", "sin etiqueta"]

# Función para cargar estados desde un archivo JSON
def load_statuses(filename="statuses.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            return data.get("statuses", [])
    except FileNotFoundError:
        print("Archivo de estados no encontrado. Usando estados por defecto.")
        return ["pendiente", "en progreso", "completada"]
    except json.JSONDecodeError:
        print("Error al leer el archivo de estados. Usando estados por defecto.")
        return ["pendiente", "en progreso", "completada"]

# Crear tarea  
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

# Función para actualizar datos de tareas
def update_task(username):
    tasks = list_tasks_with_indices(username)
    
    if not tasks:
        return

    labels = load_labels()  # Cargar las etiquetas desde el archivo

    try:
        task_num = int(input("Seleccione el número de la tarea que desea actualizar: "))
        selected_task = tasks[task_num - 1]
        
        updates = {}
        
        # Actualización de título
        title = input(f"Nuevo título (actual: {selected_task['title']}, dejar vacío para no cambiar): ")
        if title:
            updates['title'] = title
        
        # Actualización de descripción
        description = input(f"Nueva descripción (actual: {selected_task['description']}, dejar vacío para no cambiar): ")
        if description:
            updates['description'] = description
        
        # Actualización de fecha de vencimiento
        due_date = input(f"Nueva fecha de vencimiento (actual: {selected_task['due_date']}, dejar vacío para no cambiar): ")
        if due_date:
            updates['due_date'] = due_date
        
        # Actualización de etiqueta con opciones predefinidas
        print(f"Etiqueta actual: {selected_task['label']}")
        print("Seleccione una nueva etiqueta (dejar vacío para no cambiar):")
        
        for i, label in enumerate(labels, start=1):
            print(f"[{i}] {label}")

        label_choice = input("Seleccione una opción: ")
        
        if label_choice.isdigit() and 1 <= int(label_choice) <= len(labels):
            updates['label'] = labels[int(label_choice) - 1]
        
        # Actualización en la base de datos
        if updates:
            tasks_collection.update_one({'_id': selected_task['_id']}, {'$set': updates})
            log_info(f'Tarea actualizada: {selected_task["_id"]} por el usuario {username}')
            print("Tarea actualizada exitosamente.")
        else:
            print("No se realizaron cambios.")

    except (ValueError, IndexError):
        print("Selección inválida.")
        log_warning(f'Selección inválida en la actualización de tarea para el usuario {username}.')
    except Exception as e:
        log_error(f'Error al actualizar tarea para el usuario {username}: {e}')

# Función para borrar tarea
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

# Función para mostrar las tareas co indices y datos, se puede filtrar las tareas a mostrar.
# status -> utilizado para cambiar valores a mostrar
def list_tasks(username, filters=None):
    try:
        query = {"username": username}  # Filtrar por usuario

        # Aplicar filtros adicionales si se proporcionan
        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    if "$regex" in value:
                        # Aplicar filtro de expresión regular
                        regex = re.compile(value["$regex"], re.IGNORECASE)  # Insensible a mayúsculas
                        query[key] = {"$regex": regex}
                    elif "$gte" in value or "$lte" in value:
                        # Aplicar filtro de rango de fechas
                        date_range = {}
                        if "$gte" in value:
                            date_range["$gte"] = value["$gte"]
                        if "$lte" in value:
                            date_range["$lte"] = value["$lte"]
                        query[key] = date_range
                else:
                    # Aplicar otros tipos de filtros
                    query[key] = value

        # Consultar la base de datos con el filtro aplicado
        tasks = tasks_collection.find(query)

        task_list = list(tasks)  # Convertir el cursor en una lista
        
        if len(task_list) == 0:
            print("No se encontraron tareas.")
            log_info(f"No se encontraron tareas para el usuario {username} con filtros: {filters}.")
            return

        # Mostrar tareas
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
# Cambiar estado de las tareas
def change_task_status(username):
    try:
        # Listar tareas con índices
        tasks = list_tasks_with_indices(username)
        
        if not tasks:
            return  # Salir si no hay tareas para cambiar el estado

        # Cargar los estados desde el archivo JSON
        statuses = load_statuses()

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
        
        # Mostrar las opciones de estados disponibles
        print("Seleccione un nuevo estado:")
        for i, status in enumerate(statuses, start=1):
            print(f"[{i}] {status.capitalize()}")

        status_choice = input("Seleccione una opción: ")
        
        # Validar la elección del estado
        if status_choice.isdigit() and 1 <= int(status_choice) <= len(statuses):
            new_status = statuses[int(status_choice) - 1]
            # Actualizar el estado de la tarea si no es "completada"
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

# Función para mostrar y eliminar tareas completadas. Se tratan como archivadas.
def list_completed_tasks(username):
    try:
        while True:
            # Listar tareas archivadas con índice, solo con estado "completada"
            archived_tasks = list_tasks_with_indices(username, {"status": "completada"})
            
            if not archived_tasks:
                return  # Salir si no hay tareas archivadas

            # Opciones de eliminación
            print("\nOpciones de eliminación:")
            print("[1] Eliminar todas las tareas archivadas")
            print("[2] Eliminar una tarea específica")
            print("[3] Eliminar un rango de tareas por índice")
            print("   (Dejar vacío para salir)")

            choice = input("Seleccione una opción: ").strip()

            if choice == "":
                print("Saliendo del menú de eliminación de tareas archivadas.")
                break  # Salir del bucle y la función

            elif choice == "1":
                confirmation = input("¿Está seguro de que desea eliminar TODAS las tareas archivadas? (s/n): ").lower().strip()
                if confirmation == 's':
                    tasks_collection.delete_many({"status": "completada", "username": username})
                    log_info(f'Todas las tareas completadas fueron eliminadas para el usuario {username}.')
                    print("Todas las tareas completadas han sido eliminadas exitosamente.")
                else:
                    print("Eliminación cancelada.")

            elif choice == "2":
                try:
                    task_num = int(input("Seleccione el número de la tarea que desea eliminar: ").strip())
                    if 1 <= task_num <= len(archived_tasks):
                        selected_task = archived_tasks[task_num - 1]
                        tasks_collection.delete_one({'_id': selected_task['_id']})
                        log_info(f'Tarea completada eliminada: {selected_task["_id"]} por el usuario {username}')
                        print("Tarea completada eliminada exitosamente.")
                    else:
                        print("Selección inválida. Intente nuevamente.")
                except ValueError:
                    print("Entrada no válida. Intente nuevamente.")

            elif choice == "3":
                try:
                    start_index = int(input("Ingrese el índice inicial del rango de tareas a eliminar: ").strip())
                    end_index = int(input("Ingrese el índice final del rango de tareas a eliminar: ").strip())
                    if 1 <= start_index <= end_index <= len(archived_tasks):
                        task_ids_to_delete = [archived_tasks[i - 1]['_id'] for i in range(start_index, end_index + 1)]
                        tasks_collection.delete_many({'_id': {'$in': task_ids_to_delete}})
                        log_info(f'Tareas completadas eliminadas por rango para el usuario {username}')
                        print("Tareas completadas eliminadas exitosamente.")
                    else:
                        print("Rango de índices inválido. Intente nuevamente.")
                except ValueError:
                    print("Entrada no válida. Intente nuevamente.")

            else:
                print("Opción no válida. Intente nuevamente.")
            
    except Exception as e:
        log_error(f'Error al listar y eliminar tareas archivadas para el usuario {username}: {e}')
        print("Ocurrió un error al realizar la operación.")

# Lista de tareas abreviada, utilizada en delete, update y modificar estado. Es una vista simple de las tareas.
def list_tasks_with_indices(username, filters=None, mostrar="status"):
    try:
        # Asegurarse de que filters sea un diccionario, si no se pasa nada se crea un diccionario vacío
        query = filters if filters else {}
        query["username"] = username  # Filtrar por el nombre de usuario

        tasks = tasks_collection.find(query)

        task_list = list(tasks)  # Convertir el cursor en una lista

        if len(task_list) == 0:
            print("No se encontraron tareas.")
            log_info(f"No se encontraron tareas para el usuario {username}.")
            return []

        if mostrar == "status":
            # Mostrar tareas con índices
            for i, task in enumerate(task_list, start=1):
                print(f"{i}. Título: {task['title']}, Estado: {task['status']}, Fecha de vencimiento: {task['due_date']},\n   Descripción: {task['description']}")
        
        elif mostrar == "label":
            # Mostrar tareas con índices
            for i, task in enumerate(task_list, start=1):
                print(f"{i}. Título: {task['title']}, Etiqueta: {task['label']}, Fecha de vencimiento: {task['due_date']},\n   Descripción: {task['description']}")


        return task_list

    except Exception as e:
        log_error(f'Error al listar tareas para el usuario {username}: {e}')
        print("Ocurrió un error al listar las tareas.")
        return []

# Función que verifica la fecha de las tareas con la actual(local), para ver si una tarea esta atrasada
def check_and_update_overdue_tasks(username):
    try:
        current_date = datetime.now().date()
        # Buscar todas las tareas del usuario que no estén completadas
        tasks = tasks_collection.find({"username": username, "status": {"$ne": "completada"}})

        for task in tasks:
            # Convertir la fecha de vencimiento en un objeto date
            due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
            # Verificar si la tarea está atrasada
            if due_date < current_date and task['status'] != "atrasado":
                # Actualizar el estado de la tarea a "atrasado"
                tasks_collection.update_one(
                    {"_id": task["_id"]},
                    {"$set": {"status": "atrasado"}}
                )
                log_info(f"Estado de la tarea '{task['title']}' actualizado a 'atrasado' para el usuario {username}.")
                
    except Exception as e:
        log_error(f"Error al verificar y actualizar tareas atrasadas para el usuario {username}: {e}")
        print("Ocurrió un error al verificar y actualizar las tareas atrasadas.")

