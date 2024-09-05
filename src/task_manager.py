import json
import os
import re
from datetime import datetime
from logger import log_info, log_warning, log_error


TASKS_FILE = 'data/tasks.json'

def _read_tasks():
    try:
        if not os.path.exists(TASKS_FILE):
            return []
        with open(TASKS_FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        log_error(f'Error al leer el archivo de tareas: {e}')

def _write_tasks(tasks):
    try:
        with open(TASKS_FILE, 'w') as file:
            json.dump(tasks, file, indent=9)
    except Exception as e:
        log_error(f'Error al escribir en el archivo de tareas: {e}')

# Función para cargar etiquetas desde un archivo JSON
def load_labels(filename="labels.json"):
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

# Función  para agregar tarea
def create_task(title, description, due_date, label, username):
    tasks = _read_tasks()
    task = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "label": label,
        "status": "pendiente",  # Estado inicial
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username
    }
    try:
        tasks.append(task)
        _write_tasks(tasks)
        log_info(f'Tarea creada para el usuario {username}')
        print("Tarea creada exitosamente.")
    except Exception as e:
        log_error(f'Error al crear tarea: {e}')

# Función para actualizar datos de tareas
def update_task(username):
    tasks = _read_tasks()
    user_tasks = [task for task in tasks if task['username'] == username]

    if not user_tasks:
        print("No tienes tareas para actualizar.")
        return

    labels = load_labels()  # Cargar las etiquetas desde el archivo

    try:
        for idx, task in enumerate(user_tasks, start=1):
            print(f"{idx}. {task['title']} - {task['status']}")

        task_num = int(input("Seleccione el número de la tarea que desea actualizar: "))
        selected_task = user_tasks[task_num - 1]
        
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
        
        # Actualización en el archivo JSON
        if updates:
            for task in tasks:
                if task['title'] == selected_task['title'] and task['username'] == username:
                    task.update(updates)
            _write_tasks(tasks)
            log_info(f'Tarea actualizada por el usuario {username}')
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
        tasks = _read_tasks()
        user_tasks = [task for task in tasks if task['username'] == username]
        
        if not user_tasks:
            print("No tienes tareas para eliminar.")
            return

        # Listar tareas con índices
        for idx, task in enumerate(user_tasks, start=1):
            print(f"{idx}. {task['title']} - {task['status']}")

        # Solicitar al usuario que seleccione una tarea para eliminar
        task_num = int(input("Seleccione el número de la tarea que desea eliminar: "))
        
        # Validar selección
        if task_num < 1 or task_num > len(user_tasks):
            print("Selección inválida.")
            return

        selected_task = user_tasks[task_num - 1]
        
        # Confirmar eliminación
        confirmation = input(f"¿Está seguro de que desea eliminar la tarea '{selected_task['title']}'? (s/n): ").lower()
        if confirmation == 's':
            # Eliminar la tarea
            tasks = [task for task in tasks if not (task['title'] == selected_task['title'] and task['username'] == username)]
            _write_tasks(tasks)
            log_info(f'Tarea eliminada por el usuario {username}')
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
def list_tasks_with_indices(username, filters=None, mostrar="status"):
    try:
        # Leer tareas desde el archivo JSON
        tasks = _read_tasks()
        # Filtrar tareas por usuario
        user_tasks = [task for task in tasks if task['username'] == username]
        
        # Aplicar filtros adicionales
        if filters:
            for key, value in filters.items():
                user_tasks = [task for task in user_tasks if task.get(key) == value]
        
        if len(user_tasks) == 0:
            print("No se encontraron tareas.")
            log_info(f"No se encontraron tareas para el usuario {username}.")
            return []

        if mostrar == "status":
            # Mostrar tareas con índices
            for i, task in enumerate(user_tasks, start=1):
                print(f"{i}. Título: {task['title']}, Estado: {task['status']}, Fecha de vencimiento: {task['due_date']},\n   Descripción: {task['description']}")
        
        elif mostrar == "label":
            # Mostrar tareas con índices
            for i, task in enumerate(user_tasks, start=1):
                print(f"{i}. Título: {task['title']}, Etiqueta: {task['label']}, Fecha de vencimiento: {task['due_date']}, \n   Descripción: {task['description']}")

        return user_tasks

    except Exception as e:
        log_error(f'Error al listar tareas para el usuario {username}: {e}')
        print("Ocurrió un error al listar las tareas.")
        return []

# Función para mostrar y eliminar tareas completadas. Se tratan como archivadas.
def list_completed_tasks(username):
    try:
        while True:
            # Listar tareas archivadas con índice, solo con estado "completada"
            archived_tasks = list_tasks_with_indices(username, {"status": "completada"})

            if not archived_tasks:
                print("No hay tareas archivadas para eliminar.")
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
                    # Eliminar todas las tareas completadas del archivo JSON
                    tasks = _read_tasks()
                    tasks = [task for task in tasks if not (task['status'] == 'completada' and task['username'] == username)]
                    _write_tasks(tasks)
                    log_info(f'Todas las tareas completadas fueron eliminadas para el usuario {username}.')
                    print("Todas las tareas completadas han sido eliminadas exitosamente.")
                else:
                    print("Eliminación cancelada.")

            elif choice == "2":
                try:
                    task_num = int(input("Seleccione el número de la tarea que desea eliminar: ").strip())
                    if 1 <= task_num <= len(archived_tasks):
                        selected_task = archived_tasks[task_num - 1]
                        # Eliminar tarea específica
                        tasks = _read_tasks()
                        tasks = [task for task in tasks if not (task['title'] == selected_task['title'] and task['username'] == username)]
                        _write_tasks(tasks)
                        log_info(f'Tarea completada eliminada: {selected_task["title"]} por el usuario {username}')
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
                        task_titles_to_delete = [archived_tasks[i - 1]['title'] for i in range(start_index, end_index + 1)]
                        # Eliminar rango de tareas
                        tasks = _read_tasks()
                        tasks = [task for task in tasks if task['title'] not in task_titles_to_delete or task['username'] != username]
                        _write_tasks(tasks)
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

# Función para cambiar los estados de las tareas
def change_task_status(username):
    try:
        # Listar tareas con índices
        tasks = list_tasks_with_indices(username)
        
        if not tasks:
            print("No hay tareas disponibles para cambiar el estado.")
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
        task_title = selected_task['title']
        
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
            # Actualizar el estado de la tarea
            tasks = _read_tasks()
            for task in tasks:
                if task['title'] == task_title and task['username'] == username:
                    task['status'] = new_status
            _write_tasks(tasks)
            log_info(f'Estado de tarea actualizado: {task_title} por el usuario {username} a {new_status}')
            print("Estado de la tarea actualizado exitosamente.")
        else:
            print("Estado no válido.")
            log_warning(f'Intento de actualizar a un estado no válido para la tarea {task_title} por el usuario {username}.')
    except (ValueError, IndexError):
        print("Selección inválida.")
        log_warning(f'Selección inválida en el cambio de estado de tarea para el usuario {username}.')
    except Exception as e:
        log_error(f'Error al cambiar el estado de la tarea para el usuario {username}: {e}')
        print("Ocurrió un error al cambiar el estado de la tarea.")

# Función para mostrar toda la informacion de las tareas
# Se utiliza en Filtrar tareas
def list_tasks(username, filters=None):
    try:
        # Leer tareas desde el archivo JSON
        tasks = _read_tasks()
        
        # Filtrar tareas por usuario y otros filtros
        filtered_tasks = [task for task in tasks if task['username'] == username]
        
        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    if "$regex" in value:
                        # Aplicar filtro de expresión regular
                        regex = re.compile(value["$regex"], re.IGNORECASE)  # Considerar opciones insensibles a mayúsculas
                        filtered_tasks = [task for task in filtered_tasks if regex.search(task.get(key, ""))]
                    elif "$gte" in value or "$lte" in value:
                        # Aplicar filtro de fecha
                        start_date = value.get("$gte")
                        end_date = value.get("$lte")
                        filtered_tasks = [task for task in filtered_tasks if task.get(key) >= start_date and task.get(key) <= end_date]
                else:
                    # Aplicar otros filtros
                    filtered_tasks = [task for task in filtered_tasks if task.get(key) == value]

        if len(filtered_tasks) == 0:
            print("No se encontraron tareas.")
            log_info(f"No se encontraron tareas para el usuario {username}.")
            return

        # Mostrar tareas
        for task in filtered_tasks:
            print(f"\n{'-'*40}")
            print(f"Título: {task['title']}")
            print(f"Descripción: {task['description']}")
            print(f"Fecha de vencimiento: {task['due_date']}")
            print(f"Etiqueta: {task['label']}")
            print(f"Estado: {task['status']}")
            print(f"Creado en: {task['created_at']}")
            print(f"{'-'*40}\n")
        
        log_info(f'Listado de tareas consultado para el usuario {username}')
    except Exception as e:
        log_error(f'Error al listar tareas para el usuario {username}: {e}')
        print("Ocurrió un error al listar las tareas.")

# Función que verifica la fecha de las tareas con la actual(local), para ver si una tarea esta atrasada
def check_and_update_overdue_tasks(username):
    try:
        current_date = datetime.now().date()
        tasks = _read_tasks()  # Leer todas las tareas desde el archivo JSON
        
        updated_tasks = []
        for task in tasks:
            # Ignorar tareas con due_date "-"
            if task['due_date'] == "-":
                updated_tasks.append(task)
                continue

            if task['username'] == username and task['status'] != "completada":
                due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
                if due_date < current_date and task['status'] != "atrasado":
                    task['status'] = "atrasado"
                    log_info(f"Estado de la tarea '{task['title']}' actualizado a 'atrasado' para el usuario {username}.")
            
            updated_tasks.append(task)
        
        # Guardar las tareas actualizadas en el archivo JSON
        _write_tasks(updated_tasks)
        
    except Exception as e:
        log_error(f"Error al verificar y actualizar tareas atrasadas para el usuario {username}: {e}")
        print("Ocurrió un error al verificar y actualizar las tareas atrasadas.")
