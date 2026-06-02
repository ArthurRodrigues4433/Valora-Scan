from pydantic import BaseModel, ConfigDict
from typing import Optional


class LoginSchema(BaseModel):
    email: str
    senha: str

    model_config = ConfigDict(from_attributes=True)
