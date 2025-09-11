# FastAPI Frontend Theory

Учебный проект для изучения основ фронтенда с использованием FastAPI и шаблонов Jinja2.

## Структура проекта

```
LESSONS/
└─ FASTAPI_FRONTEND/
   ├─ REPETITION/
   ├─ THEORY/
   │  ├─ APP1/
   │  │  ├─ templates/
   │  │  │  ├─ base.html
   │  │  │  └─ index.html
   │  │  ├─ main.py
   │  │  └─ __init__.py
   │  ├─  APP2 
   │  ├─  APP3
   │  ├─  ... и так далее...   
   ├─ readme.md
   └─ UTILS
      └─ ... часто повторяющиеся блоки кода вынесенные в отдельный модуль
```

## Запуск первого приложения

1. Перейдите в папку с приложением:
   ```
   cd THEORY/APP1
   ```

2. Запустите сервер FastAPI:
   ```
   python main.py
   ```
   или через uvicorn:
   ```
   uvicorn main:app --reload
   ```

3. Откройте браузер и перейдите по адресу:
   ```
   http://127.0.0.1:8000/
   ```

## Основные возможности

- Отправка HTML-шаблонов с помощью Jinja2.
- Примеры маршрутов с шаблонами и простым HTML.
- Интерактивная документация по адресу `/docs` и `/redoc`.

## Полезные ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)

## Автор

Учебный проект для самостоятельного изучения FastAPI и основ фронтенда.