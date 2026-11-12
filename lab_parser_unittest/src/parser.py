import re
from typing import Any, Dict, List, Optional, Sequence, Union

import requests
from bs4 import BeautifulSoup

try:
    import lxml  # noqa: F401

    DEFAULT_PARSER_NAME = "lxml"
except ImportError:
    DEFAULT_PARSER_NAME = "html.parser"


class ForumParser:
    """
    Парсер форумных страниц.

    Класс предназначен для извлечения комментариев/сообщений со страниц форумов.
    По умолчанию используются эвристические CSS-селекторы и атрибуты,
    которые подходят для многих типовых форумных разметок.

    При необходимости селекторы можно переопределить через конструктор.
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )

    DEFAULT_COMMENT_SELECTORS = (
        "article.comment",
        "div.comment",
        "li.comment",
        "article.post",
        "div.post",
        "[data-comment-id]",
        "[data-post-id]",
    )

    DEFAULT_AUTHOR_SELECTORS = (
        ".author",
        ".username",
        ".user",
        ".login",
        "[data-role='author']",
        "a.username",
    )

    DEFAULT_MESSAGE_SELECTORS = (
        ".message",
        ".comment-body",
        ".post-body",
        ".text",
        "[data-role='message']",
    )

    DEFAULT_ID_ATTRIBUTES = (
        "data-comment-id",
        "data-post-id",
        "data-message-id",
        "data-id",
    )

    TOKEN_ID_PATTERNS = (
        r"^#?(\d+)$",
        r"comment[-_]?id[-_=](\d+)",
        r"comment[-_](\d+)",
        r"post[-_](\d+)",
        r"message[-_](\d+)",
        r"(\d+)",
    )

    LINK_ID_PATTERNS = (
        r"#comment[-_](\d+)",
        r"/comment[s]?/(\d+)",
        r"#post[-_](\d+)",
        r"/post[s]?/(\d+)",
        r"/message[s]?/(\d+)",
        r"comment[-_]?id=(\d+)",
    )

    def __init__(
        self,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 10.0,
        parser_name: Optional[str] = None,
        session: Optional[requests.Session] = None,
        comment_selectors: Optional[Sequence[str]] = None,
        author_selectors: Optional[Sequence[str]] = None,
        message_selectors: Optional[Sequence[str]] = None,
        id_attributes: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Инициализирует парсер.

        :param headers: пользовательские HTTP-заголовки.
        :param timeout: таймаут запросов в секундах.
        :param parser_name: парсер BeautifulSoup, например "lxml" или "html.parser".
        :param session: заранее созданная requests.Session.
        :param comment_selectors: CSS-селекторы для контейнеров комментариев.
        :param author_selectors: CSS-селекторы для имени автора.
        :param message_selectors: CSS-селекторы для текста сообщения.
        :param id_attributes: атрибуты, в которых может находиться ID комментария.
        """
        self.headers = {
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru,en;q=0.8",
        }

        if headers:
            self.headers.update(headers)

        self.timeout = timeout
        self.parser_name = parser_name or DEFAULT_PARSER_NAME
        self.session = session or requests.Session()

        self.comment_selectors = tuple(comment_selectors or self.DEFAULT_COMMENT_SELECTORS)
        self.author_selectors = tuple(author_selectors or self.DEFAULT_AUTHOR_SELECTORS)
        self.message_selectors = tuple(message_selectors or self.DEFAULT_MESSAGE_SELECTORS)
        self.id_attributes = tuple(id_attributes or self.DEFAULT_ID_ATTRIBUTES)

    def parse_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Скачивает страницу и извлекает комментарии.

        :param url: адрес страницы.
        :return: список словарей вида {"id": int, "name": str, "message": str}.
        """
        if not isinstance(url, str) or not url.strip():
            raise ValueError("URL должен быть непустой строкой")

        html = self.fetch_html(url)
        return self.parse_html(html)

    def fetch_html(self, url: str) -> str:
        """
        Скачивает HTML-код страницы.

        :param url: адрес страницы.
        :return: HTML-код страницы.
        """
        response = self.session.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()

        if not response.encoding:
            return response.content.decode("utf-8", errors="replace")

        return response.text

    def parse_html(self, html: Union[str, bytes]) -> List[Dict[str, Any]]:
        """
        Разбирает HTML-код и возвращает найденные комментарии.

        :param html: HTML-код страницы.
        :return: список словарей вида {"id": int, "name": str, "message": str}.
        """
        if not html:
            return []

        soup = BeautifulSoup(html, self.parser_name)
        containers = self._find_comment_containers(soup)

        comments: List[Dict[str, Any]] = []
        seen_ids = set()

        for container in containers:
            comment_id = self._extract_comment_id(container)

            if comment_id is None or comment_id in seen_ids:
                continue

            name = self._extract_author(container)
            message = self._extract_message(container)

            if not name or not message:
                continue

            comments.append(
                {
                    "id": comment_id,
                    "name": name,
                    "message": message,
                }
            )

            seen_ids.add(comment_id)

        return comments

    def save_to_db(self, parsed_data: Sequence[Dict[str, Any]], repository) -> int:
        """
        Сохраняет распарсенные комментарии в базу данных через репозиторий.

        Если комментарий с таким ID уже существует, обновляется его message.

        :param parsed_data: список распарсенных комментариев.
        :param repository: объект DatabaseRepository.
        :return: количество обработанных записей.
        """
        saved = 0

        for item in parsed_data:
            if not isinstance(item, dict):
                continue

            comment_id = item.get("id")
            name = item.get("name")
            message = item.get("message")

            if comment_id is None or not name or message is None:
                continue

            existing = repository.get_by_id(comment_id)

            if existing is None:
                repository.add(comment_id, name, message)
            else:
                repository.update(comment_id, message)

            saved += 1

        return saved

    def _find_comment_containers(self, soup: BeautifulSoup) -> List[Any]:
        """
        Ищет контейнеры комментариев по списку CSS-селекторов.

        :param soup: объект BeautifulSoup.
        :return: список найденных HTML-элементов.
        """
        containers: List[Any] = []
        seen_tags = set()

        for selector in self.comment_selectors:
            try:
                nodes = soup.select(selector)
            except Exception:
                continue

            for node in nodes:
                tag_id = id(node)

                if tag_id in seen_tags:
                    continue

                seen_tags.add(tag_id)
                containers.append(node)

        return containers

    def _extract_comment_id(self, element: Any) -> Optional[int]:
        """
        Извлекает ID комментария из атрибутов элемента или ссылок внутри него.

        :param element: HTML-элемент комментария.
        :return: ID комментария или None.
        """
        for attr in self.id_attributes:
            value = element.get(attr)

            if value is not None:
                parsed = self._parse_id_token(value)

                if parsed is not None:
                    return parsed

        element_id = element.get("id")

        if element_id is not None:
            parsed = self._parse_id_token(element_id)

            if parsed is not None:
                return parsed

        for link in element.find_all("a", href=True):
            parsed = self._parse_link_id(link["href"])

            if parsed is not None:
                return parsed

        return None

    def _extract_author(self, element: Any) -> Optional[str]:
        """
        Извлекает имя автора комментария.

        :param element: HTML-элемент комментария.
        :return: имя автора или None.
        """
        for selector in self.author_selectors:
            node = element.select_one(selector)

            if node:
                text = node.get_text(strip=True)

                if text:
                    return text

        return None

    def _extract_message(self, element: Any) -> Optional[str]:
        """
        Извлекает текст сообщения с сохранением внутренней HTML-разметки.

        :param element: HTML-элемент комментария.
        :return: HTML-содержимое сообщения или None.
        """
        for selector in self.message_selectors:
            node = element.select_one(selector)

            if node:
                message = node.decode_contents().strip()

                if message:
                    return message

        return None

    @classmethod
    def _parse_id_token(cls, value: Any) -> Optional[int]:
        """
        Извлекает числовой ID из атрибута или текстового токена.

        :param value: значение атрибута или текста.
        :return: числовой ID или None.
        """
        if isinstance(value, bool):
            return None

        if isinstance(value, int):
            return value

        if not isinstance(value, str):
            return None

        text = value.strip()

        if not text:
            return None

        for pattern in cls.TOKEN_ID_PATTERNS:
            match = re.search(pattern, text, flags=re.IGNORECASE)

            if match:
                return int(match.group(1))

        return None

    @classmethod
    def _parse_link_id(cls, value: Any) -> Optional[int]:
        """
        Извлекает числовой ID из ссылки, если ссылка похожа на ссылку комментария.

        :param value: значение href.
        :return: числовой ID или None.
        """
        if not isinstance(value, str):
            return None

        text = value.strip()

        if not text:
            return None

        for pattern in cls.LINK_ID_PATTERNS:
            match = re.search(pattern, text, flags=re.IGNORECASE)

            if match:
                return int(match.group(1))

        return None