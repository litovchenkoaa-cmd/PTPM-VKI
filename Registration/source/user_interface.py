from abc import ABC, abstractmethod


class UserInterface(ABC):
    """Абстрактный базовый класс для взаимодействия с пользователем"""

    @abstractmethod
    def get_login(self) -> str:
        """Получение логина от пользователя"""
        pass

    @abstractmethod
    def get_password(self) -> str:
        """Получение пароля от пользователя"""
        pass

    @abstractmethod
    def get_confirm_password(self) -> str:
        """Получение подтверждения пароля"""
        pass

    @abstractmethod
    def display_result(self, result: bool, message: str):
        """Отображение результата"""
        pass


class ConsoleUserInterface(UserInterface):
    """Реализация консольного интерфейса"""

    def get_login(self) -> str:
        print("=== Регистрация ===")
        print("Логин: телефон (+x-xxx-xxx-xxxx), email или строка (мин. 5 символов: латиница, цифры, '_')")
        return input("Введите логин: ")

    def get_password(self) -> str:
        print("\nПароль: мин. 7 символов. ТОЛЬКО кириллица, цифры и спецсимволы.")
        print("Обязательно: 1 заглавная кириллическая буква, 1 строчная, 1 цифра, 1 спецсимвол.")
        return input("Введите пароль: ")

    def get_confirm_password(self) -> str:
        return input("Подтвердите пароль: ")

    def display_result(self, result: bool, message: str):
        print("\n--- Результат ---")
        print(f"Строка1 (Результат): {result}")
        print(f"Строка2 (Сообщение): {message if message else 'Пустая строка (успех)'}")


class MockUserInterface(UserInterface):
    """Mock-реализация для тестирования"""

    def __init__(self, login: str = "", password: str = "", confirm_password: str = ""):
        self._login = login
        self._password = password
        self._confirm_password = confirm_password
        self._displayed_result = None

    def get_login(self) -> str:
        return self._login

    def get_password(self) -> str:
        return self._password

    def get_confirm_password(self) -> str:
        return self._confirm_password

    def display_result(self, result: bool, message: str):
        self._displayed_result = (result, message)

    def get_displayed_result(self):
        return self._displayed_result

    def set_input(self, login: str, password: str, confirm_password: str):
        self._login = login
        self._password = password
        self._confirm_password = confirm_password