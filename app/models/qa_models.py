from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr, IPvAnyAddress


class QA(BaseModel):
    name: str = None

    class Config:
        from_attributes = True
        from_attributes = True
        # orm_mode = True


class AddQA(QA):
    case: str = None
