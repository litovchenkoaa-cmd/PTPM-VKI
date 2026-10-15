import unittest
import os
from unittest.mock import patch, MagicMock

from source.validation_class import RegistrationValidator
from source.database_class import RegistrationDatabase
from source.user_interface import MockUserInterface, ConsoleUserInterface
from source.external_service import MockExternalService, EmailService
from source.controller import RegistrationController


class TestValidationClass(unittest.TestCase):
    """Тесты для класса валидации (модульные)"""

    def setUp(self):
        self.validator = RegistrationValidator()

    def test_valid_registration(self):
        """Тест успешной валидации"""
        result, message = self.validator.validate(
            "valid_user_99", "Пароль123!", "Пароль123!"
        )
        self.assertTrue(result)
        self.assertEqual(message, "")

    def test_blacklist_login(self):
        """Тест логина из черного списка"""
        result, message = self.validator.validate(
            "admin", "Пароль123!", "Пароль123!"
        )
        self.assertFalse(result)
        self.assertIn("чёрном списке", message)


class TestDatabaseClass(unittest.TestCase):
    """Тесты для класса работы с БД (модульные)"""

    def setUp(self):
        self.db = RegistrationDatabase("test_registration.db")
        self.db.clear_all()

    def tearDown(self):
        # 1. Сначала закрываем соединение (снимает блокировку файла в Windows)
        self.db.close()

        # 2. Затем удаляем файл
        if os.path.exists("test_registration.db"):
            try:
                os.remove("test_registration.db")
            except PermissionError:
                pass  # Игнорируем, если файл всё ещё занят (редкий кейс)

    def test_add_and_get_record(self):
        """Тест добавления и получения записи"""
        self.db.add_record("user1", "pass1", "pass1", True, "")
        record = self.db.get_record("user1", "pass1", "pass1")

        self.assertIsNotNone(record)
        self.assertEqual(record["login"], "user1")
        self.assertTrue(record["result"])

    def test_delete_record(self):
        """Тест удаления записи"""
        self.db.add_record("user2", "pass2", "pass2", False, "Error")
        result = self.db.delete_record("user2", "pass2", "pass2")

        self.assertTrue(result)
        record = self.db.get_record("user2", "pass2", "pass2")
        self.assertIsNone(record)

    def test_get_nonexistent_record(self):
        """Тест получения несуществующей записи"""
        record = self.db.get_record("nonexistent", "pass", "pass")
        self.assertIsNone(record)


class TestExternalService(unittest.TestCase):
    """Тесты для класса внешнего сервиса (модульные)"""

    def test_mock_service_send(self):
        """Тест отправки данных через mock сервис"""
        service = MockExternalService()
        result = service.send_data("test data")

        self.assertTrue(result)
        self.assertEqual(len(service.get_send_calls()), 1)
        self.assertEqual(service.get_send_calls()[0], "test data")


class TestControllerIntegration(unittest.TestCase):
    """Интеграционные тесты для контроллера"""

    def setUp(self):
        self.db = RegistrationDatabase("test_integration.db")
        self.db.clear_all()
        self.validator = RegistrationValidator()
        self.external_service = MockExternalService()

    def tearDown(self):
        # 1. Сначала закрываем соединение
        self.db.close()

        # 2. Затем удаляем файл
        if os.path.exists("test_integration.db"):
            try:
                os.remove("test_integration.db")
            except PermissionError:
                pass

        # Удаляем файлы WAL/SHM
        for ext in ["-wal", "-shm"]:
            wal_file = f"test_integration.db{ext}"
            if os.path.exists(wal_file):
                try:
                    os.remove(wal_file)
                except PermissionError:
                    pass

    def test_integration_successful_registration(self):
        """
        ИНТЕГРАЦИОННЫЙ ТЕСТ 1:
        Полная регистрация с валидными данными
        """
        ui = MockUserInterface("valid_user", "Пароль123!", "Пароль123!")
        controller = RegistrationController(
            validator=self.validator,
            database=self.db,
            user_interface=ui,
            external_service=self.external_service
        )

        result, message = controller.register()

        # Проверка результата
        self.assertTrue(result)
        self.assertEqual(message, "")

        # Проверка что данные сохранены в БД
        record = self.db.get_record("valid_user", "Пароль123!", "Пароль123!")
        self.assertIsNotNone(record)
        self.assertTrue(record["result"])

        # Проверка что данные отправлены во внешний сервис
        self.assertEqual(len(self.external_service.get_send_calls()), 1)
        self.assertIn("valid_user", self.external_service.get_send_calls()[0])

    def test_integration_failed_registration(self):
        """
        ИНТЕГРАЦИОННЫЙ ТЕСТ 2:
        Регистрация с невалидными данными (короткий пароль)
        """
        ui = MockUserInterface("user_test", "Пар1!", "Пар1!")
        controller = RegistrationController(
            validator=self.validator,
            database=self.db,
            user_interface=ui,
            external_service=self.external_service
        )

        result, message = controller.register()

        # Проверка результата
        self.assertFalse(result)
        self.assertIn("минимум 7 символов", message)

        # Проверка что ошибка сохранена в БД
        record = self.db.get_record("user_test", "Пар1!", "Пар1!")
        self.assertIsNotNone(record)
        self.assertFalse(record["result"])
        self.assertIn("минимум 7 символов", record["error_message"])

        # Проверка что данные отправлены во внешний сервис
        self.assertEqual(len(self.external_service.get_send_calls()), 1)

    def test_integration_cached_result(self):
        """
        ИНТЕГРАЦИОННЫЙ ТЕСТ 3:
        Повторная регистрация с теми же данными (результат из кэша БД)
        """
        # Первая регистрация
        ui1 = MockUserInterface("cached_user", "Пароль123!", "Пароль123!")
        controller1 = RegistrationController(
            validator=self.validator,
            database=self.db,
            user_interface=ui1,
            external_service=self.external_service
        )

        result1, message1 = controller1.register()
        calls_after_first = len(self.external_service.get_send_calls())

        # Вторая регистрация с теми же данными
        ui2 = MockUserInterface("cached_user", "Пароль123!", "Пароль123!")
        controller2 = RegistrationController(
            validator=self.validator,
            database=self.db,
            user_interface=ui2,
            external_service=self.external_service
        )

        result2, message2 = controller2.register()
        calls_after_second = len(self.external_service.get_send_calls())

        # Результаты должны совпадать
        self.assertEqual(result1, result2)
        self.assertEqual(message1, message2)

        # Внешний сервис должен быть вызван дважды
        self.assertEqual(calls_after_second, calls_after_first + 1)

        # В БД должна быть только одна запись
        record = self.db.get_record("cached_user", "Пароль123!", "Пароль123!")
        self.assertIsNotNone(record)

    def test_integration_with_parameters(self):
        """
        ИНТЕГРАЦИОННЫЙ ТЕСТ 4:
        Регистрация с передачей параметров напрямую (без UI)
        """
        controller = RegistrationController(
            validator=self.validator,
            database=self.db,
            user_interface=MockUserInterface(),
            external_service=self.external_service
        )

        result, message = controller.register(
            login="direct_user",
            password="Пароль123!",
            confirm_password="Пароль123!"
        )

        self.assertTrue(result)
        self.assertEqual(message, "")

        # Проверка БД
        record = self.db.get_record("direct_user", "Пароль123!", "Пароль123!")
        self.assertIsNotNone(record)


class TestControllerWithMocks(unittest.TestCase):
    """Тесты с использованием mock для изоляции"""

    @patch('source.controller.RegistrationValidator')
    @patch('source.controller.RegistrationDatabase')
    def test_controller_with_mocked_dependencies(self, mock_db_class, mock_validator_class):
        """
        Тест с полной изоляцией зависимостей
        """
        # Настройка mock объектов
        mock_validator = MagicMock()
        mock_validator.validate.return_value = (True, "")
        mock_validator_class.return_value = mock_validator

        mock_db = MagicMock()
        mock_db.get_record.return_value = None
        mock_db_class.return_value = mock_db

        mock_service = MockExternalService()
        ui = MockUserInterface("mock_user", "Пароль123!", "Пароль123!")

        controller = RegistrationController(
            user_interface=ui,
            external_service=mock_service
        )

        result, message = controller.register()

        # Проверка что validator.validate был вызван
        mock_validator.validate.assert_called_once_with("mock_user", "Пароль123!", "Пароль123!")

        # Проверка что database.add_record был вызван
        mock_db.add_record.assert_called_once()

        self.assertTrue(result)


if __name__ == '__main__':
    # Запуск всех тестов
    unittest.main(verbosity=2)