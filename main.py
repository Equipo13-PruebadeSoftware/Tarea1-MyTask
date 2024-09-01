from auth import create_user, authenticate_user
from logger import log_info, log_warning
from task_manager import create_task, update_task, delete_task, list_tasks, change_task_status

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

                while True:
                    print(f"\nOpciones: [1] Crear tarea [2] Actualizar tarea [3] Eliminar tarea [4] Listar tareas [5] Cambiar estado de tarea [6] Cerrar sesión")
                    task_choice = input("Seleccione una opción: ")

                    if task_choice == '1':
                        title = input("Título: ")
                        description = input("Descripción: ")
                        due_date = input("Fecha de vencimiento (YYYY-MM-DD): ")
                        label = input("Etiqueta: ")
                        create_task(title, description, due_date, label, username)

                    elif task_choice == '2':
                        update_task(username)

                    elif task_choice == '3':
                        delete_task(username)

                    elif task_choice == '4':
                        filters = {}
                        status = input("Filtrar por estado (pendiente/en progreso/completada, dejar vacío para no filtrar): ")
                        if status:
                            filters['status'] = status
                        list_tasks(username, filters)

                    elif task_choice == '5':
                        change_task_status(username)

                    elif task_choice == '6':
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