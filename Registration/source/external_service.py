from abc import ABC, abstractmethod
import json
from datetime import datetime


class ExternalService(ABC):
    """Абстрактный базовый класс для внешней зависимости"""

    @abstractmethod
    def send_data(self, data: str) -> bool:
        """
        Отправка данных во внешний сервис.

        Args:
            data: Данные для отправки

        Returns:
            bool: Успешность отправки
        """
        pass


class EmailService(ExternalService):
    """Реализация сервиса отправки email (имитация)"""

    def __init__(self, server_address: str = "smtp.example.com"):
        self.server_address = server_address
        self._sent_messages = []

    def send_data(self, data: str) -> bool:
        """
        Имитация отправки email.

        Args:
            data: Данные для отправки

        Returns:
            bool: Всегда True (имитация успешной отправки)
        """
        message = {
            "timestamp": datetime.now().isoformat(),
            "server": self.server_address,
            "data": data
        }
        self._sent_messages.append(message)
        # В реальной реализации здесь был бы код отправки email
        return True

    def get_sent_messages(self):
        """Получение списка отправленных сообщений (для тестов)"""
        return self._sent_messages.copy()


class MockExternalService(ExternalService):
    """Mock-реализация для тестирования"""

    def __init__(self):
        self._send_calls = []
        self._should_fail = False

    def send_data(self, data: str) -> bool:
        self._send_calls.append(data)
        return not self._should_fail

    def get_send_calls(self):
        """Получение списка вызовов send_data"""
        return self._send_calls.copy()

    def set_should_fail(self, should_fail: bool):
        """Установка флага неудачи для тестирования"""
        self._should_fail = should_fail

    def reset(self):
        """Сброс состояния"""
        self._send_calls = []
        self._should_fail = False