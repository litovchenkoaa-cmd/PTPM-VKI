import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database import DatabaseRepository
from src.parser import ForumParser

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "forum_page.html"


class BaseParserTestCase(unittest.TestCase):
    """Базовый класс для тестов парсера."""

    @classmethod
    def setUpClass(cls) -> None:
        """Загружает HTML-фикстуру один раз."""
        cls.parser = ForumParser()
        cls.html = FIXTURE_PATH.read_text(encoding="utf-8")

    def setUp(self) -> None:
        """Создает репозиторий в памяти перед каждым тестом."""
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self) -> None:
        """Закрывает репозиторий после каждого теста."""
        self.repo.close()


class TestForumParserParsing(BaseParserTestCase):
    """Тесты извлечения данных из HTML."""

    def test_parse_html_returns_expected_comments(self) -> None:
        """Парсер должен корректно извлекать комментарии из фикстуры."""
        comments = self.parser.parse_html(self.html)

        self.assertEqual(len(comments), 3)

        self.assertEqual(
            [comment["id"] for comment in comments],
            [101, 102, 103],
        )

        self.assertEqual(comments[0]["name"], "alice")
        self.assertEqual(comments[1]["name"], "bob")
        self.assertEqual(comments[2]["name"], "alice")

        self.assertIn("Первое сообщение", comments[0]["message"])
        self.assertIn("<strong>Важно!</strong>", comments[0]["message"])

        self.assertIn("Второе сообщение", comments[1]["message"])
        self.assertIn("<em>разметкой</em>", comments[1]["message"])

        self.assertIn("Текст без параграфа", comments[2]["message"])

    def test_parse_html_skips_incomplete_comments(self) -> None:
        """Парсер должен пропускать комментарии без автора или без сообщения."""
        html = """
        <article class="comment" data-comment-id="200">
            <span class="author">user_without_message</span>
        </article>

        <article class="comment" data-comment-id="201">
            <div class="message">Сообщение без автора</div>
        </article>
        """

        comments = self.parser.parse_html(html)

        self.assertEqual(comments, [])


class TestForumParserSaveToDatabase(BaseParserTestCase):
    """Тесты сохранения распарсенных данных в базу."""

    def test_save_to_db_inserts_parsed_comments(self) -> None:
        """Сохранение новых комментариев через репозиторий."""
        parsed = self.parser.parse_html(self.html)

        saved = self.parser.save_to_db(parsed, self.repo)

        self.assertEqual(saved, 3)

        first = self.repo.get_by_id(101)
        second = self.repo.get_by_id(102)
        third = self.repo.get_by_id(103)

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertIsNotNone(third)

        self.assertEqual(first["name"], "alice")
        self.assertEqual(second["name"], "bob")
        self.assertEqual(third["name"], "alice")

        self.assertEqual(len(self.repo.get_by_name("alice")), 2)

    def test_save_to_db_updates_existing_records(self) -> None:
        """Повторное сохранение не должно приводить к дублированию ID."""
        parsed = self.parser.parse_html(self.html)

        self.parser.save_to_db(parsed, self.repo)

        saved_again = self.parser.save_to_db(parsed, self.repo)

        self.assertEqual(saved_again, 3)
        self.assertEqual(len(self.repo.get_by_name("alice")), 2)


class TestForumParserPageFetching(BaseParserTestCase):
    """Тесты метода parse_page без реального доступа в интернет."""

    def test_parse_page_uses_fetch_html(self) -> None:
        """parse_page должен использовать fetch_html и корректно парсить результат."""
        with mock.patch.object(
            self.parser,
            "fetch_html",
            return_value=self.html,
        ) as fetch_mock:
            comments = self.parser.parse_page("https://example.com/forum/topic/1")

            fetch_mock.assert_called_once_with("https://example.com/forum/topic/1")
            self.assertEqual(len(comments), 3)

    def test_default_headers_contain_user_agent(self) -> None:
        """Парсер должен отправлять заголовок User-Agent."""
        self.assertIn("User-Agent", self.parser.headers)
        self.assertTrue(self.parser.headers["User-Agent"])


if __name__ == "__main__":
    unittest.main()