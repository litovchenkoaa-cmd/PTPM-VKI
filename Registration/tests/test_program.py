import unittest

from source.program import validate_and_register


class TestRegistrationValidation(unittest.TestCase):

    def setUp(self):#Начальная настройка
        pass

    # 1. Успешная регистрация с полностью корректными данными
    def test_successful_registration_with_valid_data(self):
        result, message = validate_and_register("valid_user_99", "Пароль123!", "Пароль123!")
        self.assertTrue(result)
        self.assertEqual(message, "")

    # 2. Ошибка: логин находится в чёрном списке
    def test_fails_when_login_in_blacklist(self):
        result, message = validate_and_register("admin", "Пароль123!", "Пароль123!")
        self.assertFalse(result)
        self.assertIn("чёрном списке", message)

    # 3. Ошибка: логин не соответствует формату (слишком короткий)
    def test_fails_when_login_format_is_invalid(self):
        result, message = validate_and_register("ab", "Пароль123!", "Пароль123!")
        self.assertFalse(result)
        self.assertIn("не соответствует формату", message)

    # 4. Ошибка: пароль слишком короткий (менее 7 символов)
    def test_fails_when_password_is_too_short(self):
        result, message = validate_and_register("user_test", "Пар1!", "Пар1!")
        self.assertFalse(result)
        self.assertIn("минимум 7 символов", message)

    # 5. Ошибка: в пароле нет заглавной буквы кириллицы
    def test_fails_when_no_uppercase_cyrillic_in_password(self):
        result, message = validate_and_register("user_test", "пароль123!", "пароль123!")
        self.assertFalse(result)
        self.assertIn("заглавную букву кириллицы", message)

    # 6. Ошибка: в пароле нет строчной буквы кириллицы
    def test_fails_when_no_lowercase_cyrillic_in_password(self):
        result, message = validate_and_register("user_test", "ПАРОЛЬ123!", "ПАРОЛЬ123!")
        self.assertFalse(result)
        self.assertIn("строчную букву кириллицы", message)

    # 7. Ошибка: в пароле нет цифры
    def test_fails_when_no_digit_in_password(self):
        result, message = validate_and_register("user_test", "Парольпароль!", "Парольпароль!")
        self.assertFalse(result)
        self.assertIn("минимум одну цифру", message)

    # 8. Ошибка: в пароле нет спецсимвола
    def test_fails_when_no_special_character_in_password(self):
        result, message = validate_and_register("user_test", "Пароль123", "Пароль123")
        self.assertFalse(result)
        self.assertIn("минимум один спецсимвол", message)

    # 9. Ошибка: пароль содержит запрещённые латинские буквы
    def test_fails_when_password_contains_latin_letters(self):
        result, message = validate_and_register("user_test", "Пароль123!a", "Пароль123!a")
        self.assertFalse(result)
        self.assertIn("латинские буквы", message)

    # 10. Ошибка: пароль и подтверждение пароля не совпадают
    def test_fails_when_passwords_do_not_match(self):
        result, message = validate_and_register("user_test", "Пароль123!", "Пароль123?")
        self.assertFalse(result)
        self.assertIn("не идентичны", message)

    def tearDown(self):
        # Метод вызывается после каждого теста. Можно оставить пустым или добавить print, как в примере.
        pass


if __name__ == '__main__':
    unittest.main()