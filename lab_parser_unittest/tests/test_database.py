import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database import MESSAGE_MAX_LENGTH, NAME_MAX_LENGTH, DatabaseRepository


class BaseRepositoryTestCase(unittest.TestCase):
    """Базовый класс для тестов репозитория."""

    def setUp(self) -> None:
        """Создает репозиторий в памяти перед каждым тестом."""
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self) -> None:
        """Закрывает соединение с базой данных после каждого теста."""
        self.repo.close()


class TestAdd(BaseRepositoryTestCase):
    """Тесты для метода add."""

    def test_add_success(self) -> None:
        """Успешное добавление записи."""
        result = self.repo.add(1, "alice", "<p>Hello</p>")

        self.assertTrue(result)

        row = self.repo.get_by_id(1)

        self.assertIsNotNone(row)
        self.assertEqual(row["id"], 1)
        self.assertEqual(row["name"], "alice")
        self.assertEqual(row["message"], "<p>Hello</p>")

    def test_add_duplicate_id_raises(self) -> None:
        """Добавление записи с уже существующим ID должно вызывать исключение."""
        self.repo.add(1, "alice", "first")

        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.add(1, "bob", "second")

    def test_add_too_long_name_raises(self) -> None:
        """Добавление слишком длинного имени должно вызывать ValueError."""
        long_name = "x" * (NAME_MAX_LENGTH + 1)

        with self.assertRaises(ValueError):
            self.repo.add(2, long_name, "message")

    def test_add_invalid_message_type_raises(self) -> None:
        """Добавление сообщения неверного типа должно вызывать TypeError."""
        with self.assertRaises(TypeError):
            self.repo.add(3, "alice", 123)


class TestGetById(BaseRepositoryTestCase):
    """Тесты для метода get_by_id."""

    def test_get_by_id_exists(self) -> None:
        """Получение существующей записи по ID."""
        self.repo.add(10, "alice", "message")

        row = self.repo.get_by_id(10)

        self.assertIsNotNone(row)
        self.assertEqual(row["id"], 10)
        self.assertEqual(row["name"], "alice")
        self.assertEqual(row["message"], "message")

    def test_get_by_id_missing(self) -> None:
        """Получение несуществующей записи должно возвращать None."""
        row = self.repo.get_by_id(999)

        self.assertIsNone(row)


class TestGetByName(BaseRepositoryTestCase):
    """Тесты для метода get_by_name."""

    def test_get_by_name_returns_all_user_comments(self) -> None:
        """Возврат всех комментариев пользователя."""
        self.repo.add(1, "alice", "m1")
        self.repo.add(2, "bob", "m2")
        self.repo.add(3, "alice", "m3")

        rows = self.repo.get_by_name("alice")

        self.assertEqual(len(rows), 2)
        self.assertEqual([row["id"] for row in rows], [1, 3])

    def test_get_by_name_unknown_user_returns_empty_list(self) -> None:
        """Для неизвестного пользователя возвращается пустой список."""
        rows = self.repo.get_by_name("nonexistent")

        self.assertEqual(rows, [])


class TestUpdate(BaseRepositoryTestCase):
    """Тесты для метода update."""

    def test_update_existing(self) -> None:
        """Успешное обновление сообщения существующей записи."""
        self.repo.add(1, "alice", "old message")

        result = self.repo.update(1, "new message")

        self.assertTrue(result)

        row = self.repo.get_by_id(1)

        self.assertEqual(row["message"], "new message")

    def test_update_nonexistent(self) -> None:
        """Обновление несуществующей записи должно возвращать False."""
        result = self.repo.update(999, "new message")

        self.assertFalse(result)

    def test_update_too_long_message_raises(self) -> None:
        """Обновление слишком длинным сообщением должно вызывать ValueError."""
        self.repo.add(1, "alice", "old message")

        long_message = "x" * (MESSAGE_MAX_LENGTH + 1)

        with self.assertRaises(ValueError):
            self.repo.update(1, long_message)


class TestDelete(BaseRepositoryTestCase):
    """Тесты для метода delete."""

    def test_delete_existing(self) -> None:
        """Успешное удаление существующей записи."""
        self.repo.add(1, "alice", "message")

        result = self.repo.delete(1)

        self.assertTrue(result)
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_nonexistent(self) -> None:
        """Удаление несуществующей записи должно возвращать False."""
        result = self.repo.delete(999)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()