from source.validation_class import RegistrationValidator
from source.database_class import RegistrationDatabase
from source.user_interface import UserInterface, MockUserInterface
from source.external_service import ExternalService, MockExternalService


class RegistrationController:
    """
    Контроллер для управления процессом регистрации.
    Реализует бизнес-логику сквозного сценария.
    """

    def __init__(self,
                 validator: RegistrationValidator = None,
                 database: RegistrationDatabase = None,
                 user_interface: UserInterface = None,
                 external_service: ExternalService = None):
        """
        Инициализация контроллера.

        Args:
            validator: Экземпляр валидатора
            database: Экземпляр базы данных
            user_interface: Экземпляр пользовательского интерфейса
            external_service: Экземпляр внешнего сервиса
        """
        self.validator = validator or RegistrationValidator()
        self.database = database or RegistrationDatabase()
        self.user_interface = user_interface or MockUserInterface()
        self.external_service = external_service or MockExternalService()

    def register(self, login: str = None, password: str = None,
                 confirm_password: str = None) -> tuple[bool, str]:
        """
        Основной метод регистрации.

        Бизнес-логика:
        1. Запрашивает входные данные (через user_interface или параметры)
        2. Проверяет наличие записи в БД
        3. Если нет записи - вычисляет результат и добавляет в БД
        4. Если есть запись - берет результат из БД
        5. Отправляет результат во внешний сервис
        6. Возвращает результат

        Args:
            login: Логин (если None, берется из user_interface)
            password: Пароль (если None, берется из user_interface)
            confirm_password: Подтверждение пароля (если None, берется из user_interface)

        Returns:
            tuple: (Результат (bool), Сообщение (str))
        """
        # 1. Получение данных от пользователя
        if login is None or password is None or confirm_password is None:
            login = self.user_interface.get_login()
            password = self.user_interface.get_password()
            confirm_password = self.user_interface.get_confirm_password()

        # 2. Проверка наличия записи в БД
        existing_record = self.database.get_record(login, password, confirm_password)

        if existing_record:
            # Запись существует - берем результат из БД
            result = existing_record["result"]
            error_message = existing_record["error_message"]
        else:
            # Записи нет - вычисляем результат
            result, error_message = self.validator.validate(login, password, confirm_password)

            # Добавляем запись в БД
            self.database.add_record(login, password, confirm_password, result, error_message)

        # 3. Отправка результата во внешний сервис
        result_string = f"Registration: login={login}, success={result}"
        if error_message:
            result_string += f", error={error_message}"

        self.external_service.send_data(result_string)

        # 4. Отображение результата (если есть интерфейс)
        if hasattr(self.user_interface, 'display_result'):
            self.user_interface.display_result(result, error_message)

        return result, error_message

    def get_registration_history(self, login: str) -> list:
        """
        Получение истории регистраций для конкретного логина.

        Args:
            login: Логин для поиска

        Returns:
            list: Список записей
        """
        # В реальной реализации нужен метод в БД для поиска по логину
        # Для простоты возвращаем пустой список
        return []