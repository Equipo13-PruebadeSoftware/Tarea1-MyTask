# Usar una imagen base de Python
FROM python:3.12-slim

# Copiar los archivos de tu proyecto al contenedor
COPY . /app

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar las dependencias de Python
RUN pip install -r requirements.txt

# Comando para correr la aplicación
CMD ["python3", "src/main.py"]
