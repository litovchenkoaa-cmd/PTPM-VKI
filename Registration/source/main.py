from source.controller import RegistrationController
from source.database_class import RegistrationDatabase
from source.user_interface import ConsoleUserInterface
from source.external_service import EmailService


def main():
    """Основная функция приложения"""
    print("=== Система регистрации ===\n")

    # Создание экземпляров
    database = RegistrationDatabase("registration.db")
    user_interface = ConsoleUserInterface()
    external_service = EmailService()

    # Создание контроллера
    controller = RegistrationController(
        database=database,
        user_interface=user_interface,
        external_service=external_service
    )

    # Запуск регистрации
    try:
        result, message = controller.register()

        if result:
            print("\n✓ Регистрация успешна!")
        else:
            print(f"\n✗ Ошибка регистрации: {message}")

    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\n✗ Критическая ошибка: {e}")


if __name__ == '__main__':
    main()