import logging

# Configuración básica del logging
logging.basicConfig(
    filename='logs/task_manager.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def log_info(message):
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)
