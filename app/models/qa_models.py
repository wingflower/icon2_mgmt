from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress


class QA(BaseModel):
    name: str = None

    class Config:
        orm_mode = True


class AddQA(QA):
    case: str = None