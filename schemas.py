from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    age: int


class User(UserCreate):
    id: int

    class Config:
        orm_mode = True
