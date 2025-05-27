from pydantic import BaseModel

class User(BaseModel):
    email: str | None = None
    password: str | None = None
    active: bool | None = None