import sqlite3
from typing import Optional


class RegistrationDatabase:
    """Класс для работы с базой данных регистрации"""

    def __init__(self, db_path: str = "registration.db"):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Создание и сохранение соединения с БД"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            # Режим WAL (Write-Ahead Logging) снижает вероятность блокировки файлов в Windows
            self.conn.execute("PRAGMA journal_mode=WAL")

    def _create_table(self):
        """Создание таблицы если не существует"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL,
                password TEXT NOT NULL,
                confirm_password TEXT NOT NULL,
                result INTEGER NOT NULL,
                error_message TEXT,
                UNIQUE(login, password, confirm_password)
            )
        ''')
        self.conn.commit()

    def add_record(self, login: str, password: str, confirm_password: str,
                   result: bool, error_message: str = "") -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO registrations 
                (login, password, confirm_password, result, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (login, password, confirm_password, 1 if result else 0, error_message))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            return False

    def get_record(self, login: str, password: str, confirm_password: str) -> Optional[dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT login, password, confirm_password, result, error_message
                FROM registrations
                WHERE login = ? AND password = ? AND confirm_password = ?
            ''', (login, password, confirm_password))

            row = cursor.fetchone()
            if row:
                return {
                    "login": row[0],
                    "password": row[1],
                    "confirm_password": row[2],
                    "result": bool(row[3]),
                    "error_message": row[4] or ""
                }
            return None
        except Exception as e:
            print(f"Ошибка при получении записи: {e}")
            return None

    def delete_record(self, login: str, password: str, confirm_password: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM registrations
                WHERE login = ? AND password = ? AND confirm_password = ?
            ''', (login, password, confirm_password))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при удалении записи: {e}")
            return False

    def clear_all(self):
        """Очистка всех записей (для тестов)"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM registrations')
        self.conn.commit()

    def close(self):
        """Явное закрытие соединения с БД (ОБЯЗАТЕЛЬНО для тестов в Windows)"""
        if self.conn:
            self.conn.close()
            self.conn = None