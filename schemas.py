from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LivroIn(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    autor: str = Field(min_length=1, max_length=120)
    ano: int = Field(ge=0, le=2100)
    disponivel: bool = True


class LivroOut(LivroIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UsuarioIn(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=6, max_length=128)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
