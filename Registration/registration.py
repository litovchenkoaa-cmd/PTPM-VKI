def get_registration_data():
    print("=== Регистрация ===")
    print("Логин: телефон (+x-xxx-xxx-xxxx), email или строка (мин. 5 символов: латиница, цифры, '_')")
    login = input("Введите логин: ")

    print("\nПароль: мин. 7 символов. ТОЛЬКО кириллица, цифры и спецсимволы.")
    print("Обязательно: 1 заглавная кириллическая буква, 1 строчная, 1 цифра, 1 спецсимвол.")
    password = input("Введите пароль: ")

    confirm_password = input("Подтвердите пароль: ")


    return login, password, confirm_password


if __name__ == '__main__':
    login, password, confirm_password = registration()
    print(login)