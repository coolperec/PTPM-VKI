# -*- coding: utf-8 -*-
"""
Лабораторная работа №1. Вариант 2.
Проверка данных пользователя при регистрации.

Входные данные:
    Строка1 — Логин (телефон, email или обычная строка)
    Строка2 — Пароль
    Строка3 — Подтверждение пароля

Выходные данные:
    Строка1 (Результат) — True / False
    Строка2 (Сообщение) — пустая строка при успехе, иначе причина отказа
"""

import os
import re
import sys
import hashlib
import logging
from datetime import datetime

# ---------------------------------------------------------------------------
# 1. НАСТРОЙКА ЛОГИРОВАНИЯ
# ---------------------------------------------------------------------------

# Создаём папку Logs (по заданию — рядом с main.py), если её нет
LOG_DIR = "Logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "registration.log")

log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),                 # вывод в консоль
        logging.FileHandler(LOG_FILE, encoding="utf-8"),   # вывод в файл
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 2. МАСКИРОВАНИЕ ПАРОЛЕЙ
# ---------------------------------------------------------------------------

def mask_secret(secret: str) -> str:
    """
    Необратимое маскирование (хеш) секретных данных для логирования.

    Требование ТЗ: одинаковые пароли -> одинаковый результат,
    разные пароли -> разный результат.
    Используем SHA-256 и обрезаем до 16 символов для читаемости логов.
    """
    if secret is None:
        return "<none>"
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    return f"<masked:{digest[:16]}>"


# ---------------------------------------------------------------------------
# 3. ЧЁРНЫЙ СПИСОК ЛОГИНОВ
# ---------------------------------------------------------------------------

BLACKLIST = {
    "admin",
    "administrator",
    "root",
    "superuser",
    "moderator",
    "support",
    "system",
    "user",
    "test",
    "guest",
}


# ---------------------------------------------------------------------------
# 4. РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ
# ---------------------------------------------------------------------------

# Телефон: +x-xxx-xxx-xxxx (по ТЗ формат строго такой)
RE_PHONE = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")

# Email: стандартная маска (упрощённая, но покрывающая типовые случаи)
RE_EMAIL = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
)

# Обычный логин: только латиница, цифры и '_', минимум 5 символов
RE_PLAIN_LOGIN = re.compile(r"^[A-Za-z0-9_]{5,}$")

# Пароль: кириллица, цифры, спецсимволы (разрешённые).
# Разрешаем кириллические буквы, цифры и набор спецсимволов.
RE_PASSWORD_ALLOWED = re.compile(r"^[А-Яа-яЁё0-9!@#$%^&*()_\-+=<>,.?/\\|{}\[\]:;\"'`~]+$")

# В пароле обязательны: хотя бы одна строчная буква кириллицы,
# одна прописная, одна цифра, один спецсимвол.
RE_HAS_LOWER = re.compile(r"[а-яё]")
RE_HAS_UPPER = re.compile(r"[А-ЯЁ]")
RE_HAS_DIGIT = re.compile(r"[0-9]")
RE_HAS_SPECIAL = re.compile(r"[!@#$%^&*()_\-+=<>,.?/\\|{}\[\]:;\"'`~]")

# Для проверки «латиница/цифры/подчёркивание» в строковом логине
RE_HAS_LATIN_ONLY = re.compile(r"^[A-Za-z0-9_]+$")


# ---------------------------------------------------------------------------
# 5. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ВАЛИДАЦИИ
# ---------------------------------------------------------------------------

def validate_login(login: str):
    """
    Возвращает (True, "") при успехе,
    либо (False, "<сообщение об ошибке>") при провале.
    """
    if login is None:
        return False, "Логин не может быть None"

    login = login.strip()
    if login == "":
        return False, "Логин не может быть пустым"

    # Определяем тип логина
    if RE_PHONE.match(login):
        logger.debug("Логин распознан как телефон: %s", login)
        # Дополнительных проверок по ТЗ нет
    elif RE_EMAIL.match(login):
        logger.debug("Логин распознан как email: %s", login)
        # Дополнительных проверок по ТЗ нет
    else:
        logger.debug("Логин распознан как обычная строка: %s", login)
        if len(login) < 5:
            return False, "Логин-строка должен содержать минимум 5 символов"
        if not RE_HAS_LATIN_ONLY.match(login):
            return False, ("Логин-строка может содержать только латиницу, "
                           "цифры и знак подчёркивания")

    # Проверка чёрного списка (без учёта регистра)
    if login.lower() in BLACKLIST:
        return False, f"Логин '{login}' находится в чёрном списке"

    return True, ""


def validate_password(password: str, confirm: str):
    """
    Возвращает (True, "") при успехе,
    либо (False, "<сообщение об ошибке>") при провале.
    """
    if password is None:
        return False, "Пароль не может быть None"
    if confirm is None:
        return False, "Подтверждение пароля не может быть None"

    # Длина
    if len(password) < 7:
        return False, "Пароль должен содержать минимум 7 символов"

    # Только разрешённые символы (кириллица, цифры, спецсимволы)
    if not RE_PASSWORD_ALLOWED.match(password):
        return False, ("Пароль может содержать только кириллицу, "
                       "цифры и спецсимволы")

    # Обязательные классы символов
    if not RE_HAS_LOWER.search(password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"
    if not RE_HAS_UPPER.search(password):
        return False, "Пароль должен содержать хотя бы одну прописную букву"
    if not RE_HAS_DIGIT.search(password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not RE_HAS_SPECIAL.search(password):
        return False, "Пароль должен содержать хотя бы один спецсимвол"

    # Совпадение пароля и подтверждения
    if password != confirm:
        return False, "Пароль и подтверждение пароля не совпадают"

    return True, ""


# ---------------------------------------------------------------------------
# 6. ОСНОВНАЯ ФУНКЦИЯ РЕГИСТРАЦИИ
# ---------------------------------------------------------------------------

def register_user(login: str, password: str, confirm: str):
    """
    Комплексная проверка учётных данных.

    :return: (result: bool, message: str)
    """
    # Маскируем пароли для логирования
    masked_pwd = mask_secret(password)
    masked_cfm = mask_secret(confirm)

    logger.info(
        "Запрос регистрации | login=%r | password=%s | confirm=%s",
        login, masked_pwd, masked_cfm,
    )

    try:
        ok_login, msg_login = validate_login(login)
        if not ok_login:
            logger.warning("Отказ регистрации (логин): %s", msg_login)
            return False, msg_login

        ok_pwd, msg_pwd = validate_password(password, confirm)
        if not ok_pwd:
            logger.warning("Отказ регистрации (пароль): %s", msg_pwd)
            return False, msg_pwd

        logger.info("Регистрация успешна | login=%r", login)
        return True, ""

    except Exception as ex:
        # Логируем ошибку со стеком
        logger.exception("Непредвиденная ошибка при регистрации: %s", ex)
        return False, f"Внутренняя ошибка: {ex}"


# ---------------------------------------------------------------------------
# 7. ТОЧКА ВХОДА
# ---------------------------------------------------------------------------

def main():
    logger.info("=" * 70)
    logger.info("Приложение запущено: %s", datetime.now().strftime(date_format))

    # Демонстрационные кейсы (покрывают все правила валидации).
    # Если запускаете интерактивно — раскомментируйте блок input() ниже.

    test_cases = [
        # (login, password, confirm)
        ("+7-999-123-4567", "Пароль1!", "Пароль1!"),          # OK, телефон
        ("user@example.com", "Пароль1!", "Пароль1!"),         # OK, email
        ("john_doe",         "Пароль1!", "Пароль1!"),         # OK, строка
        ("abc",              "Пароль1!", "Пароль1!"),         # логин < 5
        ("jo hn",            "Пароль1!", "Пароль1!"),         # недоп. символы
        ("admin",            "Пароль1!", "Пароль1!"),         # чёрный список
        ("john_doe",         "Парол1",   "Парол1"),           # пароль < 7
        ("john_doe",         "Пароль1",  "Пароль1"),          # нет спецсимвола
        ("john_doe",         "пароль1!", "пароль1!"),         # нет прописной
        ("john_doe",         "ПАРОЛЬ1!", "ПАРОЛЬ1!"),         # нет строчной
        ("john_doe",         "Пароль!",  "Пароль!"),          # нет цифры
        ("john_doe",         "Пароль1!", "Пароль1?"),         # не совпадают
        ("john_doe",         "Password1!", "Password1!"),     # латиница в пароле
        ("",                 "Пароль1!", "Пароль1!"),         # пустой логин
    ]

    print("\n----- РЕЗУЛЬТАТЫ ТЕСТОВЫХ ПРОВЕРОК -----")
    for i, (l, p, c) in enumerate(test_cases, 1):
        print(f"\n[Кейс {i}] login={l!r}  password={mask_secret(p)}")
        result, message = register_user(l, p, c)
        print(f"  Результат: {result}")
        print(f"  Сообщение: {message!r}")

    # --- Интерактивный режим (раскомментируйте при необходимости) ---
    # print("\nВведите логин: ");    login_in    = input().strip()
    # print("Введите пароль: ");     password_in = input()
    # print("Повторите пароль: ");   confirm_in  = input()
    # res, msg = register_user(login_in, password_in, confirm_in)
    # print(res); print(msg)

    logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()