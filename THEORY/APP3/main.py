import os
from fastapi import FastAPI, Request,Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
# для работы с этим слоем нужно установить pip list itsdangerous
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

"""
http://127.0.0.1:8000/ - главная страница приложения
http://127.0.0.1:8000/docs/ - интерактивная документация
http://127.0.0.1:8000/redoc/ - лаконичная и краткая документация
"""

# инициализация шаблона
path_templates = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=path_templates)

# инициализация приложения
app = FastAPI()
# естественно нужно использовать более сложные ключи и не хранить их в коде
app.add_middleware(SessionMiddleware, secret_key="test secret")


def set_flashed_messages(request: Request, message: str, critical:bool=False):
    """Установка flash сообщения в словарь сессию с пользователем"""
    flash_messages = request.session.get("_flash_messages", {"status":"success", "messages":[]})
    flash_messages["messages"].append(message)
    flash_messages["status"] = "critical" if critical else "success"
    request.session["_flash_messages"] = flash_messages


def get_flashed_messages(request: Request):
    "Получить и очистить flash сообщения из сессии."
    messages = request.session.pop("_flash_messages", {"status":"success", "messages":[]})
    return messages


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """на каждый запрос необходимо сперва заглянуть в flash сообщения, и отправить их пользователю"""
    messages = get_flashed_messages(request)
    return templates.TemplateResponse(
        name="index.html", 
        context={"request":request, "messages" : messages}
        )

@app.post("/submit_form", response_class=HTMLResponse)
async def submit_form(request:Request, name: str=Form(...)):
    if not name:
        set_flashed_messages(request, "Имя не может быть пустым", critical=True)
    else:
        set_flashed_messages(request, f"Привет, {name}! Ваши данные были успешно отправлены.")
    return RedirectResponse(url="/", status_code=303) # перенаправить пользователя на главную страницу / статус 303 означает что данные успешно были приняты

if __name__ == "__main__":
    file = __file__
    file = os.path.basename(file)
    file = os.path.splitext(file)[0]
    uvicorn.run(app=f"{file}:app", host="127.0.0.1", port=8000, reload=True)
