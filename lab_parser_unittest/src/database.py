import sqlite3
from typing import Any, Dict, List, Optional

NAME_MAX_LENGTH = 256
MESSAGE_MAX_LENGTH = 8096


class DatabaseRepository:
    """
    Репозиторий для работы с таблицей comments в SQLite.

    Таблица:
        comments:
            id INTEGER PRIMARY KEY
            name TEXT NOT NULL
            message TEXT NOT NULL
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        """
        Создает подключение к базе данных и инициализирует схему.

        :param db_path: путь к файлу базы данных или ":memory:" для тестов.
        """
        self._connection = sqlite3.connect(str(db_path))
        self._connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        """
        Создает таблицу comments, если она еще не существует.

        Ограничения длины продублированы на уровне базы данных.
        """
        with self._connection:
            self._connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL CHECK(length(name) <= {NAME_MAX_LENGTH}),
                    message TEXT NOT NULL CHECK(length(message) <= {MESSAGE_MAX_LENGTH})
                );
                """
            )

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        self._connection.close()

    def __enter__(self) -> "DatabaseRepository":
        """Поддержка контекстного менеджера."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Закрывает соединение при выходе из контекста."""
        self.close()

    @staticmethod
    def _validate_comment_id(comment_id: int) -> None:
        """
        Проверяет корректность идентификатора комментария.

        :param comment_id: идентификатор комментария.
        :raises TypeError: если передан не целочисленный идентификатор.
        """
        if isinstance(comment_id, bool) or not isinstance(comment_id, int):
            raise TypeError("comment_id должен быть целым числом, а не булевым значением")

    @staticmethod
    def _validate_name(username: str) -> None:
        """
        Проверяет корректность имени пользователя.

        :param username: имя пользователя.
        :raises TypeError: если имя не является строкой.
        :raises ValueError: если имя пустое или превышает допустимую длину.
        """
        if not isinstance(username, str):
            raise TypeError("name должен быть строкой")

        if len(username) > NAME_MAX_LENGTH:
            raise ValueError(f"name должен быть не длиннее {NAME_MAX_LENGTH} символов")

        if not username.strip():
            raise ValueError("name не может быть пустым")

    @staticmethod
    def _validate_message(message: str) -> None:
        """
        Проверяет корректность текста сообщения.

        :param message: текст сообщения.
        :raises TypeError: если сообщение не является строкой.
        :raises ValueError: если сообщение превышает допустимую длину.
        """
        if not isinstance(message, str):
            raise TypeError("message должен быть строкой")

        if len(message) > MESSAGE_MAX_LENGTH:
            raise ValueError(f"message должен быть не длиннее {MESSAGE_MAX_LENGTH} символов")

    def add(self, comment_id: int, username: str, message: str) -> bool:
        """
        Добавляет новую запись в таблицу comments.

        :param comment_id: уникальный идентификатор комментария.
        :param username: имя пользователя.
        :param message: текст сообщения, может содержать HTML-разметку.
        :return: True при успешном добавлении.
        :raises TypeError: если переданы данные неверного типа.
        :raises ValueError: если нарушены ограничения длины.
        :raises sqlite3.IntegrityError: если запись с таким id уже существует.
        """
        self._validate_comment_id(comment_id)
        self._validate_name(username)
        self._validate_message(message)

        with self._connection:
            self._connection.execute(
                "INSERT INTO comments (id, name, message) VALUES (?, ?, ?);",
                (comment_id, username, message),
            )

        return True

    def get_by_id(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """
        Возвращает запись по идентификатору.

        :param comment_id: идентификатор комментария.
        :return: словарь с полями id, name, message или None, если запись не найдена.
        """
        self._validate_comment_id(comment_id)

        row = self._connection.execute(
            "SELECT id, name, message FROM comments WHERE id = ?;",
            (comment_id,),
        ).fetchone()

        return dict(row) if row is not None else None

    def get_by_name(self, username: str) -> List[Dict[str, Any]]:
        """
        Возвращает список всех записей пользователя с указанным именем.

        :param username: имя пользователя.
        :return: список словарей с полями id, name, message.
        """
        if not isinstance(username, str):
            raise TypeError("name должен быть строкой")

        rows = self._connection.execute(
            "SELECT id, name, message FROM comments WHERE name = ? ORDER BY id;",
            (username,),
        ).fetchall()

        return [dict(row) for row in rows]

    def update(self, comment_id: int, new_message: str) -> bool:
        """
        Обновляет текст сообщения по идентификатору.

        :param comment_id: идентификатор комментария.
        :param new_message: новый текст сообщения.
        :return: True, если запись существовала и была обновлена, иначе False.
        :raises TypeError: если переданы данные неверного типа.
        :raises ValueError: если нарушена допустимая длина сообщения.
        """
        self._validate_comment_id(comment_id)
        self._validate_message(new_message)

        if self.get_by_id(comment_id) is None:
            return False

        with self._connection:
            self._connection.execute(
                "UPDATE comments SET message = ? WHERE id = ?;",
                (new_message, comment_id),
            )

        return True

    def delete(self, comment_id: int) -> bool:
        """
        Удаляет запись по идентификатору.

        :param comment_id: идентификатор комментария.
        :return: True, если запись существовала и была удалена, иначе False.
        :raises TypeError: если идентификатор имеет неверный тип.
        """
        self._validate_comment_id(comment_id)

        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM comments WHERE id = ?;",
                (comment_id,),
            )

        return cursor.rowcount > 0