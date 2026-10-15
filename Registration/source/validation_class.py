import re
import string
from source.password_mask import mask_password
from source.regular_expressions import login_re
from source.errors import ValidationError


class RegistrationValidator:
    """Класс для валидации данных регистрации"""

    BLACKLIST = {"admin", "user", "root", "test"}
    special = re.escape(string.punctuation)

    def validate(self, login: str, password: str, confirm_password: str) -> tuple[bool, str]:
        """
        Выполняет валидацию данных регистрации.

        Args:
            login: Логин пользователя
            password: Пароль
            confirm_password: Подтверждение пароля

        Returns:
            tuple: (Результат (bool), Сообщение (str))
        """
        pwd_mask = mask_password(password)

        try:
            # 1. Проверка черного списка
            if login.lower() in self.BLACKLIST:
                raise ValidationError("Логин находится в чёрном списке.")

            # 2. Проверка формата логина
            if not login_re.match(login):
                raise ValidationError(
                    "Логин не соответствует формату (телефон +x-xxx-xxx-xxxx, email или строка: мин. 5 символов, латиница, цифры, '_').")

            # 3. Проверка длины пароля
            if len(password) < 7:
                raise ValidationError("Пароль должен содержать минимум 7 символов.")

            # 4. Проверка заглавной буквы кириллицы
            if not re.search(r"[А-ЯЁ]", password):
                raise ValidationError("Пароль должен содержать минимум одну заглавную букву кириллицы.")

            # 5. Проверка строчной буквы кириллицы
            if not re.search(r"[а-яё]", password):
                raise ValidationError("Пароль должен содержать минимум одну строчную букву кириллицы.")

            # 6. Проверка цифры
            if not re.search(r"[0-9]", password):
                raise ValidationError("Пароль должен содержать минимум одну цифру.")

            # 7. Проверка спецсимвола
            if not re.search(rf"[{self.special}]", password):
                raise ValidationError("Пароль должен содержать минимум один спецсимвол.")

            # 8. Проверка отсутствия латинских букв
            if re.search(r"[A-Za-z]", password):
                raise ValidationError(
                    "Пароль не должен содержать латинские буквы (разрешены только кириллица, цифры и спецсимволы).")

            # 9. Проверка совпадения паролей
            if password != confirm_password:
                raise ValidationError("Пароль и подтверждение пароля не идентичны.")

            return True, ""

        except ValidationError as e:
            return False, str(e)

        except Exception as e:
            return False, "Внутренняя ошибка сервера. Попробуйте позже."