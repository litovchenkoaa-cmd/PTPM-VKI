"""
Пакет лабораторной работы.

Содержит модули для работы с базой данных и веб-парсером.
"""

from .database import DatabaseRepository
from .parser import ForumParser

__all__ = [
    "DatabaseRepository",
    "ForumParser",
]