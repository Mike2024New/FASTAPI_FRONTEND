from sqlmodel import create_engine, SQLModel, Field
from pydantic import BaseModel, ConfigDict

class User(SQLModel, table=True):
    """структура модели пользователя в БД"""
    id: int | None = Field(default=None, primary_key=True)
    user_name: str =  Field(nullable=False, unique=True, max_length=50)
    password: str = Field(nullable=False, min_length=4, max_length=50)

class UserBase(BaseModel):
    """общая модель она будет выводиться пользователю"""
    user_name: str = Field(max_length=50)
    model_config = ConfigDict(from_attributes=True, extra="forbid")

class UserLogin(UserBase):
    """Модель для авторизации пользователя"""
    password : str = Field(nullable=False, min_length=4, max_length=50)

class UserRegister(UserLogin):
    """модель для регистрации и создания нового аккаунта пользователя"""
    password_repeat: str = Field(nullable=False, min_length=4, max_length=50)

# создание драйвера для базы данных (вынесен отдельно из модуля main)
connect_args = {"check_same_thread" : False} # разрешить Fastapi работать с БД из разных потоков
engine = create_engine(url="sqlite:///database.db", connect_args=connect_args)