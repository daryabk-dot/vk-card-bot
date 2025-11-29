# bot_runner.py
import sys
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    # Добавляем путь к проекту
    sys.path.append(os.path.dirname(__file__))
    
    from bot import main
    logger = logging.getLogger(__name__)
    
    logger.info("Запускаем бота для открыток...")
    main()
    
except Exception as e:
    logging.error(f"Ошибка запуска бота: {e}")
    with open('error_log.txt', 'a') as f:
        f.write(f"Error: {e}\n")
