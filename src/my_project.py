# src/my_project.py
"""Валидация регистрации пользователя (из ЛР1, вариант 2)."""

import re
import hashlib

BLACKLIST = {
    "admin", "administrator", "root", "superuser",
    "moderator", "support", "system", "user", "test", "guest",
}

RE_PHONE = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
RE_EMAIL = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
RE_PLAIN_LOGIN = re.compile(r"^[A-Za-z0-9_]{5,}$")
RE_PASSWORD_ALLOWED = re.compile(
    r"^[А-Яа-яЁё0-9!@#$%^&*()_\-+=<>,.?/\\|{}\[\]:;\"'`~]+$"
)
RE_HAS_LOWER = re.compile(r"[а-яё]")
RE_HAS_UPPER = re.compile(r"[А-ЯЁ]")
RE_HAS_DIGIT = re.compile(r"[0-9]")
RE_HAS_SPECIAL = re.compile(r"[!@#$%^&*()_\-+=<>,.?/\\|{}\[\]:;\"'`~]")


def mask_secret(secret):
    """Одинаковые пароли → одинаковый хеш, разные → разный."""
    if secret is None:
        return "<none>"
    return f"<masked:{hashlib.sha256(secret.encode('utf-8')).hexdigest()[:16]}>"


def validate_login(login):
    """Возвращает (True, '') или (False, 'сообщение')."""
    if login is None:
        return False, "Логин не может быть None"
    login = login.strip()
    if login == "":
        return False, "Логин не может быть пустым"

    if RE_PHONE.match(login) or RE_EMAIL.match(login):
        pass  # валидный телефон или email
    else:
        if len(login) < 5:
            return False, "Логин-строка должен содержать минимум 5 символов"
        if not RE_PLAIN_LOGIN.match(login):
            return False, ("Логин-строка может содержать только латиницу, "
                           "цифры и знак подчёркивания")

    if login.lower() in BLACKLIST:
        return False, f"Логин '{login}' находится в чёрном списке"
    return True, ""


def validate_password(password, confirm):
    """Проверка пароля и его подтверждения."""
    if password is None:
        return False, "Пароль не может быть None"
    if confirm is None:
        return False, "Подтверждение пароля не может быть None"
    if len(password) < 7:
        return False, "Пароль должен содержать минимум 7 символов"
    if not RE_PASSWORD_ALLOWED.match(password):
        return False, ("Пароль может содержать только кириллицу, "
                       "цифры и спецсимволы")
    if not RE_HAS_LOWER.search(password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"
    if not RE_HAS_UPPER.search(password):
        return False, "Пароль должен содержать хотя бы одну прописную букву"
    if not RE_HAS_DIGIT.search(password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not RE_HAS_SPECIAL.search(password):
        return False, "Пароль должен содержать хотя бы один спецсимвол"
    if password != confirm:
        return False, "Пароль и подтверждение пароля не совпадают"
    return True, ""


def register_user(login, password, confirm):
    """Комплексная проверка: сначала логин, потом пароль."""
    ok, msg = validate_login(login)
    if not ok:
        return False, msg
    ok, msg = validate_password(password, confirm)
    if not ok:
        return False, msg
    return True, ""