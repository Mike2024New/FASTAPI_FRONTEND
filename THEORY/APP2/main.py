import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

"""
В этом уроке рассмотрены основные инструменты работы с jinja2 шаблонами.
ex1 - обработка переменных переданных в шаблоны
ex2 - условия в шаблонах, тернарные операторы
ex3 - тесты типов (проверка типов), обход вложенной коллекции
ex4 - передача функций в шаблоны
ex5 - определение пользовательских фильтров в шаблонах
ex6 - переменные созданные прямо в шаблонах
ex7 - макросы (пользовательские функции) определенные в шаблонах
ex8 - вставка блоков кода в макрос при помощи call и caller
ex9 - include - вставка фрагментов кода из других шаблонов, import - импортирование макросов и переменных из других модулей
ex10 - with - создание контекста с переменными
"""


"""
http://127.0.0.1:8000/ - главная страница приложения
http://127.0.0.1:8000/docs/ - интерактивная документация
http://127.0.0.1:8000/redoc/ - лаконичная и краткая документация
"""

# создать объект Jinja2 с указанием директории (путь относительный)
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

app = FastAPI(
    title="Jinja2 работа с шаблонами",
    summary="Основные методы работы с шаблонизатором jinja2 перменные, циклы условия, макросы и так далее.",
)


@app.get("/", response_class=HTMLResponse,summary="Содержание")
def home(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        context={"request": request}
    )



@app.get("/ex1/", response_class=HTMLResponse,summary="обработка переменных переданных в шаблоны")  # http://127.0.0.1:8000/ex1/
def ex1(request: Request):
    """Обработка переменных и обход итерируемых коллекций в шаблонах"""
    return templates.TemplateResponse(
        name="ex1.html",
        status_code=200,
        context={
            "request": request,
            "title": "Главная страница",
            "header": "Заголовок страницы",
            "text": "Текст переданный из бекенда отображается на странице...",
            # передача списков
            "languages_list": ["python", "html", "css", "java script"],
            # передача словарей
            "user": {"name": "Ivan", "age": 32, "city": "Moscow"},
        },
    )


@app.get("/ex2/", response_class=HTMLResponse,summary="условия в шаблонах, тернарные операторы")  # http://127.0.0.1:8000/ex2/
def ex2(request: Request):
    """Обработка условий в шаблонах, тернарные операторы"""
    return templates.TemplateResponse(
        name="ex2.html",
        context={
            "request": request,
            "parametr": [True, "parametr"],  # будет обработан в if/endif
            "mode": 2,  # будет обработан блоком с if/elif/else/endif
            # будет обработан тернарным оператором
            "user": {"is_active": False},
        }
    )


@app.get("/ex3/", response_class=HTMLResponse,summary="тесты типов (проверка типов), обход вложенной коллекции")  # http://127.0.0.1:8000/ex3/
async def ex3(request: Request):
    """тесты типов в шаблонах такие как: string, number, integer, boolean, mapping, sequence, iterable, defined, none, callable"""
    return templates.TemplateResponse(
        name="ex3.html",
        context={
            "request": request,
            "arr": {  # этот массив будет разобран на типы
                "bool": True,
                "string": "test",
                "num": 1234,
                "list": [1, 2, 3],
                "mapping": {"a": 123, "b": 456},
                "callable": lambda: print(123),
            },
            "arr2": {  # итерация по вложенным элементам массива
                "list": [],
                "string": "test",
                "list2": [1, 2, 3],
                "number": 10,
            }
        },
    )

# регистрация глобальной функции (которая будет доступна во всех шаблонах)
templates.env.globals["test"] = lambda: "test text"


@app.get("/ex4/", response_class=HTMLResponse,summary="передача функций в шаблоны")  # http://127.0.0.1:8000/ex4/
async def ex4(request: Request):
    """передача функции в шаблон / шаблоны jinja2 могут выполнять функции переданные в них из python"""
    return templates.TemplateResponse(
        name="ex4.html",
        context={
            "request": request,
            # эта функция может быть исполнена прямо в jinja2 шаблоне
            "func": lambda x: f"Привет, {x}",
        }
    )


def is_even_num(x):
    return x % 2 == 0


# определение пользователских фильтров которые будут доступны во всех шаблонах ниже
# можно передавать обычные функции
templates.env.filters['is_even_num'] = is_even_num
templates.env.filters['str_len'] = lambda string: len(string)  # lambda функции

# определение пользовательских фильтров в шаблонах
@app.get("/ex5/", response_class=HTMLResponse,summary="определение пользовательских фильтров в шаблонах")  # http://127.0.0.1:8000/ex5/
async def ex5(request: Request):
    """обработка пользовательских и встроенных фильтров в jinja2"""
    return templates.TemplateResponse(
        name="ex5.html",
        context={
            "request": request,
        }
    )

# определение переменных в шаблоне
@app.get("/ex6/", response_class=HTMLResponse,summary="переменные созданные прямо в шаблонах")  # http://127.0.0.1:8000/ex6/
async def ex6(request:Request):
    return templates.TemplateResponse(
        name="ex6.html",
        context={
            "request":request,
             }
    )

# макросы (пользовательские функции) в шаблонах
@app.get("/ex7/", response_class=HTMLResponse, summary="макросы (пользовательские функции) определенные в шаблонах")  # http://127.0.0.1:8000/ex7/
async def ex7(request:Request):
    return templates.TemplateResponse(
        name="ex7.html",
        context={
            "request":request,
             }
    )

# вставка фрагментов кода с помощью caller
@app.get("/ex8/", response_class=HTMLResponse,summary="вставка блоков кода в макрос при помощи call и caller")  # http://127.0.0.1:8000/ex8/
async def ex8(request:Request):
    return templates.TemplateResponse(
        name="ex8.html",
        context={
            "request":request,
             }
    )

# include и import
@app.get("/ex9/", response_class=HTMLResponse,summary="include - вставка фрагментов кода из других шаблонов, import - импортирование макросов и переменных из других модулей")  # http://127.0.0.1:8000/ex9/
async def ex9(request:Request):
    return templates.TemplateResponse(
        name="ex9.html",
        context={
            "request":request,
             }
    )

# работа с with
@app.get("/ex10/", response_class=HTMLResponse,summary="with - создание контекста с переменными")  # http://127.0.0.1:8000/ex10/
async def ex10(request:Request):
    return templates.TemplateResponse(
        name="ex10.html",
        context={
            "request":request,
             }
    )

if __name__ == "__main__":
    file = __file__
    file = os.path.basename(file)
    file = os.path.splitext(file)[0]
    uvicorn.run(app=f"{file}:app", host="127.0.0.1", port=8000, reload=True)
