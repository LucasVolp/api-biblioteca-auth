import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario

SECRET_KEY = os.getenv("SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao")
ALGORITHM = "HS256"
EXPIRA_EM_MINUTOS = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# usado quando o e-mail não existe, para o tempo de resposta não denunciar quais e-mails estão cadastrados
HASH_FALSO = password_hash.hash("senha-inexistente")


def gerar_hash(senha: str) -> str:
    return password_hash.hash(senha)


def autenticar(db: Session, email: str, senha: str) -> Usuario | None:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None:
        password_hash.verify(senha, HASH_FALSO)
        return None
    if not password_hash.verify(senha, usuario.senha_hash):
        return None
    return usuario


def criar_token(email: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=EXPIRA_EM_MINUTOS)
    return jwt.encode({"sub": email, "exp": expira}, SECRET_KEY, algorithm=ALGORITHM)


def usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    erro = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    except jwt.InvalidTokenError:
        raise erro
    usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None:
        raise erro
    return usuario
