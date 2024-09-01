from auth import create_user, authenticate_user
from logger import log_info, log_warning, log_error
from task_manager import create_task, update_task, delete_task, list_tasks, change_task_status, list_filed_tasks, check_and_update_overdue_tasks, list_tasks_with_indices, load_labels,load_statuses
from datetime import datetime

def main():
    while True:

        print("\nOpciones: [1] Iniciar sesión [2] Crear usuario [3] Salir")
        choice = input("Seleccione una opción: ")

        if choice == '1':
            username = input("Ingrese su nombre de usuario: ")
            password = input("Ingrese su contraseña: ")

            if authenticate_user(username, password):
                log_info(f'Usuario {username} autenticado exitosamente')
                print("Autenticado exitosamente")

                # Verificar y actualizar tareas atrasadas al iniciar sesión
                check_and_update_overdue_tasks(username)
                                

                while True:
                    print(f"\nTAREAS de ", username)
                    print(f"\nPENDIENTES", "-"*20)
                    list_tasks_with_indices(username, {"status": "pendiente"}, "label")
                    print(f"\nEN PROGRESO", "-"*20)
                    list_tasks_with_indices(username, {"status": "en progreso"}, "label")
                    print(f"\nCOMPLETADAS", "-"*20)
                    list_tasks_with_indices(username, {"status": "completada"}, "label")
                
                    print(f"\nOpciones:\n[1] Crear tarea\n[2] Actualizar tarea\n[3] Eliminar tarea\n[4] Filtrar tareas\n[5] Cambiar estado de tarea\n[6] Ver archivadas\n[7] Cerrar sesión")
                    task_choice = input("Seleccione una opción: ")

                    if task_choice == '1': # Crear tarea
                        title = input("Título: ").strip()
                        if not title:
                            log_warning(f"No se ingersó titulo para tarea. No se creó la tarea.")
                            print("Aviso: El título de la tarea es obligatorio. No se creó la tarea.")
                            continue

                        description = input("Descripción: ").strip() or "-"
                        due_date = input("Fecha de vencimiento (YYYY-MM-DD): ").strip() or "-"

                        # Cargar etiquetas desde el archivo JSON
                        labels = load_labels()

                        # Seleccionar una etiqueta predefinida
                        label = 'sin etiqueta'
                        add_label = input("\n¿Desea agregar una etiqueta? (s/n): ").lower()

                        if add_label == 's':
                            print("\nSeleccione una etiqueta:")
                            for i, lbl in enumerate(labels, start=1):
                                print(f"[{i}] {lbl.capitalize()}")

                            label_choice = input("Seleccione una opción: ")

                            if label_choice.isdigit() and 1 <= int(label_choice) <= len(labels):
                                label = labels[int(label_choice) - 1]
                            else:
                                print("Opción no válida. No se aplicará ninguna etiqueta.")
                                label = 'sin etiqueta'  # Valor por defecto

                        create_task(title, description, due_date, label, username)

                    elif task_choice == '2': # Actualizar datos
                        update_task(username)

                    elif task_choice == '3': # Borrar tarea
                        delete_task(username)

                    elif task_choice == '4': # Filtrar tareas
                        filters = {}
                        
                        # Preguntar si desea aplicar algún filtro
                        apply_filters = input("\n¿Desea aplicar filtros? (s/n): ").lower()

                        if apply_filters == 's':
                            # Filtrado por título
                            filter_by_title = input("\n¿Desea filtrar por título? (s/n): ").lower()

                            if filter_by_title == 's':
                                title = input("Ingrese el título a buscar: ")
                                filters['title'] = {"$regex": title, "$options": "i"}  # Búsqueda por título (insensible a mayúsculas)
                            else:
                                # Filtrado por estado
                                filter_by_status = input("\n¿Desea filtrar por estado? (s/n): ").lower()

                                if filter_by_status == 's':
                                    statuses = load_statuses()
                                    print("\nSeleccione el estado:")
                                    for i, status in enumerate(statuses, start=1):
                                        print(f"[{i}] {status.capitalize()}")

                                    status_choice = input("Seleccione una opción: ")

                                    if status_choice.isdigit() and 1 <= int(status_choice) <= len(statuses):
                                        filters['status'] = statuses[int(status_choice) - 1]
                                    else:
                                        print("Opción no válida. No se aplicará ningún filtro de estado.")
                                
                                # Filtrado por etiqueta
                                filter_by_label = input("\n¿Desea filtrar por etiqueta? (s/n): ").lower()

                                if filter_by_label == 's':
                                    labels = load_labels()
                                    print("\nSeleccione la etiqueta:")
                                    for i, lbl in enumerate(labels, start=1):
                                        print(f"[{i}] {lbl.capitalize()}")

                                    label_choice = input("Seleccione una opción: ")

                                    if label_choice.isdigit() and 1 <= int(label_choice) <= len(labels):
                                        filters['label'] = labels[int(label_choice) - 1]
                                    else:
                                        print("Opción no válida. No se aplicará ningún filtro de etiqueta.")
                                
                                # Filtrado por rango de fechas desde la fecha actual
                                filter_by_date_range = input("\n¿Desea filtrar por un rango de fechas desde hoy? (s/n): ").lower()

                                if filter_by_date_range == 's':
                                    end_date = input("Ingrese la fecha de fin (YYYY-MM-DD): ")
                                    current_date = datetime.now().strftime('%Y-%m-%d')  # Obtener la fecha actual

                                    try:
                                        filters['due_date'] = {"$gte": current_date, "$lte": end_date}
                                    except Exception as e:
                                        print("Formato de fecha inválido.")
                                        log_warning(f"Formato de fecha inválido al filtrar por rango de fechas: {e}")

                        # Eliminar claves nulas
                        filters = {k: v for k, v in filters.items() if v is not None}

                        list_tasks(username, filters)

                    elif task_choice == '5': # Cambiar estado
                        change_task_status(username)

                    elif task_choice == '6':  # Tareas completadas/archivadas
                        list_filed_tasks(username)

                    elif task_choice == '7': # Cerrar sesion
                        print("Cerrando sesión...")
                        break

                    else:
                        print("Opción no válida.")
            else:
                log_warning(f'Intento fallido de autenticación para el usuario {username}')
                print("Usuario o contraseña incorrectos")

        elif choice == '2':
            username = input("Ingrese un nombre de usuario: ")
            password = input("Ingrese una contraseña: ")

            create_user(username, password)
            log_info(f'Usuario {username} creado exitosamente')
            print("Usuario creado exitosamente")

        elif choice == '3':
            print("Saliendo...")
            break

        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()