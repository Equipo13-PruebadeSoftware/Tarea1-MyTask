# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de tu proyecto al contenedor
COPY . .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que correrá tu aplicación (si aplica)
EXPOSE 8081

# Comando para correr la aplicación
CMD ["python", "main.py"]
