# Utilizamos la imagen oficial de Python 3
FROM python:3.9-slim

# Establecemos el directorio de trabajo en /app
WORKDIR /app

# Copiamos los archivos del proyecto en el contenedor
COPY app/ /app/
COPY data/ /app/data/
COPY logs/ /app/logs/

# Instalamos las dependencias del proyecto
RUN pip install -r requirements.txt

# Exponemos el puerto 8000 para que se pueda acceder al contenedor
EXPOSE 8000

# Establecemos el comando para ejecutar el contenedor
CMD ["python", "main.py"]
