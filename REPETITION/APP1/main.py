from datetime import timedelta
import os
from fastapi import FastAPI, Request, Form, Depends, Cookie,HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from starlette.middleware.sessions import SessionMiddleware
# Для работы с БД
from .models import engine, UserBase, UserRegister, User
from sqlmodel import SQLModel, Session, select
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager
import uvicorn
# Подключаемые утилиты python -m REPETITION.APP1.helper
from UTIL.HASH_MANAGER import HashManager
from UTIL.JWT_MANAGER import JWTManager

"""
http://127.0.0.1:8000/ - главная страница приложения
http://127.0.0.1:8000/docs/ - интерактивная документация
http://127.0.0.1:8000/redoc/ - лаконичная и краткая документация
"""

# Для упрощения, тут указан один ключ и для паролей и для токенов и сессий, но нужно делать разные и не хранить ключ в коде
SECRET_KEY = "a7d090ad57d614b12ae399d59c038cf2fbba7d727b1bae2eae068940e701c014"

# инициализировать шаблоны
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)


@asynccontextmanager
async def on_startup(application: FastAPI):
    ...  # действия при запуске приложения fastapi...
    SQLModel.metadata.create_all(engine)
    yield
    ...  # действия после завершения работы приложения fastapi...


def get_session():  # получение сессии для работы с БД
    with Session(engine) as session:
        yield session


# через этот тип можно будет получать сессию
SessionDepends = Annotated[Session, Depends(get_session)]
hash_manager = HashManager(secret_key=SECRET_KEY)
jwt_manager = JWTManager(secret_key=SECRET_KEY,
                         token_action=timedelta(minutes=30), algoritm="HS256")
# схема авторизации, привязать маршрут login
# oauth2_scheme = OAuth2PasswordBearer("login/")

# инициализация приложения с подключенным промежуточным слоем для работы с сессией
app = FastAPI(lifespan=on_startup)
# для упрощения ключ якобы здесь
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


class FlashMessages:
    """Класс для работы с flash сообщениями выводимыми пользователю"""
    @staticmethod
    async def set_flashed_messages(request: Request, message: str, critical: bool = False):
        """Установка Flash сообщения в request (для вывода информации пользователю)"""
        flash_messages = request.session.get("_flash_messages", [])
        flash_messages.append({
            "msg": message,
            "status": "critical" if critical else "success",
        })
        request.session["_flash_messages"] = flash_messages

    @staticmethod
    async def get_flashed_messages(request: Request):
        """Получить все Flash сообщения из сессии"""
        flash_messages = request.session.pop("_flash_messages", [])
        return flash_messages


async def get_user(login, session: SessionDepends):
    statement = select(User).where(User.user_name == login)  # условие WHERE
    user = session.exec(statement)  # выполнение запроса в БД
    user = user.first()
    return user


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # http://127.0.0.1:8000/
    flashed_messages = await FlashMessages.get_flashed_messages(request)
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "flashed_messages": flashed_messages,
        }
    )


async def get_user_from_token(request: Request, session: SessionDepends, access_token: Annotated[str | None, Cookie()] = None):
    # ! Установка заголовка Location и статус кода 300 серии автоматически в браузере переводи клиента на страницу указанную в заголовке
    exception_verify = HTTPException(status_code=303, headers={"Location":"/login/"})
    if access_token is None:
        await FlashMessages.set_flashed_messages(request=request, message=f"Неверные данные для входа", critical=True)
        raise exception_verify

    payload = jwt_manager.get_payload_from_token_verify(token_in=access_token)
    try:
        payload = jwt_manager.get_payload_from_token_verify(
            token_in=access_token)
        username = payload.get("sub")
        if username is None:
            await FlashMessages.set_flashed_messages(request=request, message=f"Отказано в доступе", critical=True)
            raise exception_verify

    except Exception as err:

        print(f"Ошибка чтения jwt токена: {err}")
        await FlashMessages.set_flashed_messages(request=request, message=f"Отказано в доступе", critical=True)
        raise exception_verify
    user = await get_user(login=username, session=session)
    if user is None:

        await FlashMessages.set_flashed_messages(request=request, message=f"Отказано в доступе", critical=True)
        raise exception_verify


@app.get("/test/", response_class=HTMLResponse, dependencies=[Depends(get_user_from_token)])
async def test(request: Request):
    flashed_messages = await FlashMessages.get_flashed_messages(request)
    return templates.TemplateResponse(
        name="test.html",
        context={
            "request": request,
            "flashed_messages": flashed_messages,
        }
    )


@app.get("/login/", response_class=HTMLResponse, summary="Получение формы с авторизацией", tags=["login"])
async def login_send_form(request: Request):
    flashed_messages = await FlashMessages.get_flashed_messages(request)
    return templates.TemplateResponse(
        name="login.html",
        context={
            "request": request,
            "flashed_messages": flashed_messages,
        }
    )


@app.post("/login/", summary="Авторизация пользователя", tags=["login"])
async def login_check_user(session: SessionDepends, request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # get запрос с получением пользователя из БД
    login = form_data.username
    password = form_data.password
    # получение пользователя из БД
    user = await get_user(login=login, session=session)
    if not user:
        print(f"Пользователя {login} не существует в БД.")
        await FlashMessages.set_flashed_messages(request=request, message="Не верные логин и/или пароль", critical=True)
        return RedirectResponse(url="/login/", status_code=303)
    if not hash_manager.verify_password(password_checker=password, password_original=user.password):
        print(f"Пользователь {login} ввел не правильный пароль.")
        await FlashMessages.set_flashed_messages(request=request, message="Не верные логин и/или пароль", critical=True)
        return RedirectResponse(url="/login/", status_code=303)

    # когда все проверки пройдены:
    await FlashMessages.set_flashed_messages(request=request, message="Успешная авторизация, все ок!")
    token = jwt_manager.create_token(data={"sub": login})
    response = RedirectResponse(url="/test", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=1800,
        secure=True,
        samesite='lax'
    )
    return response


@app.get("/create_account/", response_class=HTMLResponse, summary="Получение формы с регистрацией", tags=["create_account"])
async def create_account_send_form(request: Request):
    flashed_messages = await FlashMessages.get_flashed_messages(request)
    return templates.TemplateResponse(
        name="create_account.html",
        context={
            "request": request,
            "flashed_messages": flashed_messages,
        }
    )


@app.post("/create_account/", summary="регистрация нового пользователя", tags=["create_account"])
async def create_account_add_user(
    # приём данных из формы отправленной post запросом
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    password_repeat: Annotated[str, Form()],
    session: SessionDepends,
    request: Request,
):
    # БЛОК ПРОВЕРОК:
    UserRegister(user_name=username, password=password,
                 password_repeat=password_repeat)  # проверка что валидация пройдена
    # проверка паролей (пока так, потом здесь будет устанавливаться flash сообщение и редиректить на get create_account)
    if password != password_repeat:
        await FlashMessages.set_flashed_messages(request=request, message="Пароли должны совпадать", critical=True)
        # переход обратно на страницу регистрации
        return RedirectResponse(url="/create_account/", status_code=303)

    # ПРЕОБРАЗОВАНИЕ ПАРОЛЯ В ХЕШ:
    password = hash_manager.hash_password(password_in=password)
    # СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ В БД:
    try:
        user = User(user_name=username, password=password)
        session.add(user)
        session.commit()
    except IntegrityError as err:
        print(err)
        await FlashMessages.set_flashed_messages(request=request, message=f"Пользователь с логином {username} уже существует...", critical=True)
        # переход обратно на страницу регистрации
        return RedirectResponse(url="/create_account/", status_code=303)
    except Exception as err:
        print(err)
        await FlashMessages.set_flashed_messages(request=request, message="Произошла не предвиденная ошибк, попробуйте ещё", critical=True)
        # переход обратно на страницу регистрации
        return RedirectResponse(url="/create_account/", status_code=303)
    await FlashMessages.set_flashed_messages(request=request, message="Отлично, аккаунт успешно создан", critical=False)
    # перенаправить пользователя после регистрации
    print(f"Создан пользователь с логином: {username} и паролем: {password}")
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    file = __file__
    file = os.path.basename(file)
    file = os.path.splitext(file)[0]
    uvicorn.run(app=f"{file}:app", host="127.0.0.1", port=8000, reload=True)
