# tests/test_my_project.py
import sys
import os
import unittest

# Чтобы тесты видели модуль из src/
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src")))

from my_project import (
    validate_login, validate_password, register_user, mask_secret
)


# ============================================================
# ТЕСТЫ ЛОГИНА
# ============================================================
class TestValidateLogin(unittest.TestCase):

    def test_login_none_returns_error(self):
        ok, msg = validate_login(None)
        self.assertFalse(ok)
        self.assertIn("None", msg)

    def test_login_empty_returns_error(self):
        ok, msg = validate_login("")
        self.assertFalse(ok)
        self.assertEqual(msg, "Логин не может быть пустым")

    def test_login_only_spaces_returns_error(self):
        ok, msg = validate_login("     ")
        self.assertFalse(ok)
        self.assertEqual(msg, "Логин не может быть пустым")

    def test_login_valid_phone(self):
        ok, msg = validate_login("+7-999-123-4567")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_login_invalid_phone_wrong_format(self):
        ok, _ = validate_login("+79991234567")
        self.assertFalse(ok)

    def test_login_valid_email(self):
        ok, msg = validate_login("user@example.com")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_login_invalid_email_no_domain(self):
        ok, _ = validate_login("user@")
        self.assertFalse(ok)

    def test_login_plain_too_short(self):
        ok, msg = validate_login("abcd")
        self.assertFalse(ok)
        self.assertIn("минимум 5", msg)

    def test_login_plain_min_length_ok(self):
        ok, _ = validate_login("abcde")
        self.assertTrue(ok)

    def test_login_plain_with_digits_and_underscore_ok(self):
        ok, _ = validate_login("user_123")
        self.assertTrue(ok)

    def test_login_plain_with_space_invalid(self):
        ok, msg = validate_login("user name")
        self.assertFalse(ok)
        self.assertIn("латиницу", msg)

    def test_login_plain_with_cyrillic_invalid(self):
        ok, _ = validate_login("пользователь")
        self.assertFalse(ok)

    def test_login_in_blacklist_lowercase(self):
        ok, msg = validate_login("admin")
        self.assertFalse(ok)
        self.assertIn("чёрном списке", msg)

    def test_login_in_blacklist_uppercase(self):
        ok, _ = validate_login("ADMIN")
        self.assertFalse(ok)

    def test_login_in_blacklist_mixed_case(self):
        ok, _ = validate_login("RoOt")
        self.assertFalse(ok)

    def test_login_not_in_blacklist_ok(self):
        ok, _ = validate_login("john_doe")
        self.assertTrue(ok)


# ============================================================
# ТЕСТЫ ПАРОЛЯ
# ============================================================
class TestValidatePassword(unittest.TestCase):

    def test_password_none_returns_error(self):
        ok, msg = validate_password(None, "anything")
        self.assertFalse(ok)
        self.assertIn("None", msg)

    def test_confirm_none_returns_error(self):
        ok, msg = validate_password("Пароль1!", None)
        self.assertFalse(ok)
        self.assertIn("None", msg)

    def test_password_too_short(self):
        ok, msg = validate_password("Пар1!", "Пар1!")
        self.assertFalse(ok)
        self.assertIn("минимум 7", msg)

    def test_password_min_length_ok(self):
        ok, _ = validate_password("Пароль1!", "Пароль1!")
        self.assertTrue(ok)

    def test_password_with_latin_invalid(self):
        ok, msg = validate_password("Password1!", "Password1!")
        self.assertFalse(ok)
        self.assertIn("кириллицу", msg)

    def test_password_without_uppercase_invalid(self):
        ok, msg = validate_password("пароль1!", "пароль1!")
        self.assertFalse(ok)
        self.assertIn("прописную", msg)

    def test_password_without_lowercase_invalid(self):
        ok, msg = validate_password("ПАРОЛЬ1!", "ПАРОЛЬ1!")
        self.assertFalse(ok)
        self.assertIn("строчную", msg)

    def test_password_without_digit_invalid(self):
        ok, msg = validate_password("Пароль!", "Пароль!")
        self.assertFalse(ok)
        self.assertIn("цифру", msg)

    def test_password_without_special_invalid(self):
        ok, msg = validate_password("Пароль1", "Пароль1")
        self.assertFalse(ok)
        self.assertIn("спецсимвол", msg)

    def test_passwords_do_not_match(self):
        ok, msg = validate_password("Пароль1!", "Пароль1?")
        self.assertFalse(ok)
        self.assertIn("не совпадают", msg)


# ============================================================
# ТЕСТЫ РЕГИСТРАЦИИ (ИНТЕГРАЦИОННЫЕ)
# ============================================================
class TestRegisterUser(unittest.TestCase):

    def test_register_success_phone(self):
        result, msg = register_user("+7-999-123-4567", "Пароль1!", "Пароль1!")
        self.assertTrue(result)
        self.assertEqual(msg, "")

    def test_register_success_email(self):
        result, msg = register_user("user@example.com", "Пароль1!", "Пароль1!")
        self.assertTrue(result)
        self.assertEqual(msg, "")

    def test_register_fail_when_login_invalid(self):
        result, msg = register_user("admin", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertIn("чёрном списке", msg)

    def test_register_fail_when_password_invalid(self):
        result, msg = register_user("john_doe", "пароль", "пароль")
        self.assertFalse(result)
        self.assertIn("минимум 7", msg)


# ============================================================
# ТЕСТЫ МАСКИРОВАНИЯ
# ============================================================
class TestMaskSecret(unittest.TestCase):

    def test_mask_same_input_same_output(self):
        self.assertEqual(mask_secret("Пароль1!"), mask_secret("Пароль1!"))

    def test_mask_different_input_different_output(self):
        self.assertNotEqual(mask_secret("Пароль1!"), mask_secret("Пароль2!"))

    def test_mask_none_returns_placeholder(self):
        self.assertEqual(mask_secret(None), "<none>")

    def test_mask_does_not_contain_original(self):
        masked = mask_secret("SuperSecret123!")
        self.assertNotIn("SuperSecret123!", masked)


if __name__ == "__main__":
    unittest.main(verbosity=2)