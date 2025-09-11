import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

"""
Отправка html шаблонов и кода пользователю.
"""


# Запуск через терминал: python THEORY\APP1\main.py
# Альтернативный запуск через терминал: uvicorn THEORY.APP1.main:app --reload
"""
http://127.0.0.1:8000/ - главная страница приложения
http://127.0.0.1:8000/docs/ - интерактивная документация
http://127.0.0.1:8000/redoc/ - лаконичная и краткая документация
"""

templates_path = os.path.join(os.path.dirname(__file__),"templates") # чтобы можно было запускать из разных проектов, нужно указать относительный путь
# Для того, чтобы использовать шаблоны нужно создать экземпляр класса Jinja2Templates с путём к папке с шаблонами
templates = Jinja2Templates(
    directory=templates_path,
)
app = FastAPI()

# в декораторе пути явно указан тип HTMLResponse, что отобразится в документации


@app.get("/", response_class=HTMLResponse)  # http://127.0.0.1:8000/
def home_page(request: Request):
    """В качестве ответа явно передаётся шаблон с указанием пути напрямую."""
    return templates.TemplateResponse(name="index.html", context={
        "request": request,
    })

# также можно отправить простейший html в виде текста прямо из маршрута без подгрузки шаблонов
@app.get("/ex1/",response_class=HTMLResponse)  # http://127.0.0.1:8000/ex1/
def ex1():
    return HTMLResponse(content="""
    <h1>Заголовок</h1>
    <p>Просто текст на странице...</p>
    """)

if __name__ == "__main__":
    file = __file__
    file = os.path.basename(file)
    file = os.path.splitext(file)[0]
    uvicorn.run(app=f"{file}:app", host="127.0.0.1", port=8000, reload=True)
