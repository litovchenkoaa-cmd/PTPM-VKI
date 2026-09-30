import os
import sys
import logging
import re
import string

from registration import get_registration_data
from password_mask import mask_password
from regular_expressions import login_re
from errors import ValidationError

# 1. Создание папки для логов, если её нет
os.makedirs("logs", exist_ok=True)

BLACKLIST = {"admin", "user", "root", "test"}
special = re.escape(string.punctuation)


# 2. Безопасная настройка логгера с фильтром по умолчанию
class ContextFilter(logging.Filter):
    """Добавляет значения по умолчанию, если extra не передан, чтобы избежать KeyError"""

    def filter(self, record):
        if not hasattr(record, 'login'):
            record.login = "N/A"
        if not hasattr(record, 'pwd_mask'):
            record.pwd_mask = "N/A"
        return True


logger = logging.getLogger("RegistrationLogger")
logger.setLevel(logging.DEBUG)
logger.addFilter(ContextFilter())

log_format = "%(asctime)s | [%(levelname)-7s] | Логин: %(login)s | Маска: %(pwd_mask)s | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(log_format, datefmt=date_format)

# Обработчики
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs/file_txt.log", encoding="utf-8")
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def validate_and_register(login: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Выполняет валидацию и возвращает кортеж: (Результат (bool), Сообщение (str))
    Реализует более 10 различных причин неуспеха.
    """
    pwd_mask = mask_password(password)

    try:
        logger.debug("Начало проверки данных пользователя", extra={"login": login, "pwd_mask": pwd_mask})

        # 1. Проверка черного списка
        if login.lower() in BLACKLIST:
            raise ValidationError("Логин находится в чёрном списке.")

        # 2. Проверка формата логина
        if not login_re.match(login):
            raise ValidationError(
                "Логин не соответствует формату (телефон +x-xxx-xxx-xxxx, email или строка: мин. 5 символов, латиница, цифры, '_').")

        # 3-8. Детальная проверка пароля (для обеспечения 10+ причин ошибок)
        if len(password) < 7:
            raise ValidationError("Пароль должен содержать минимум 7 символов.")
        if not re.search(r"[А-ЯЁ]", password):
            raise ValidationError("Пароль должен содержать минимум одну заглавную букву кириллицы.")
        if not re.search(r"[а-яё]", password):
            raise ValidationError("Пароль должен содержать минимум одну строчную букву кириллицы.")
        if not re.search(r"[0-9]", password):
            raise ValidationError("Пароль должен содержать минимум одну цифру.")
        if not re.search(rf"[{special}]", password):
            raise ValidationError("Пароль должен содержать минимум один спецсимвол.")
        if re.search(r"[A-Za-z]", password):
            raise ValidationError(
                "Пароль не должен содержать латинские буквы (разрешены только кириллица, цифры и спецсимволы).")

        # 9. Проверка совпадения паролей
        if password != confirm_password:
            raise ValidationError("Пароль и подтверждение пароля не идентичны.")

        # Успех
        logger.info("Регистрация успешно завершена", extra={"login": login, "pwd_mask": pwd_mask})
        return True, ""

    except ValidationError as e:
        # Логирование ошибки с трассировкой стека (traceback), как требуется в задании
        logger.error("Ошибка валидации данных", extra={"login": login, "pwd_mask": pwd_mask})
        logger.exception("Трассировка стека исключения валидации:")
        return False, str(e)

    except Exception as e:
        # Логирование непредвиденных сбоев
        logger.critical("Непредвиденный сбой приложения", extra={"login": login, "pwd_mask": pwd_mask})
        logger.exception("Трассировка стека критического сбоя:")
        return False, "Внутренняя ошибка сервера. Попробуйте позже."


if __name__ == '__main__':
    logger.info("Приложение запущено")

    # Получаем данные
    login, password, confirm_password = get_registration_data()

    # Выполняем валидацию
    is_success, message = validate_and_register(login, password, confirm_password)

    # Вывод выходных данных согласно требованиям
    print("\n--- Результат ---")
    print(f"Строка1 (Результат): {is_success}")
    print(f"Строка2 (Сообщение): {message if message else 'Пустая строка (успех)'}")