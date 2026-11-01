# API Biblioteca — Autenticação com OAuth2 e JWT

API REST para controle de livros de uma biblioteca, com banco SQLite (SQLAlchemy + Alembic) e autenticação via OAuth2 Password Flow com tokens JWT.

As rotas de leitura (GET) são públicas. As rotas que alteram dados (POST, PUT e DELETE em `/livros`) exigem um token válido no header `Authorization: Bearer <token>`.

**Aluno:** Lucas Bezerra

## Estrutura

```
database.py      engine, sessão e dependência get_db
models.py        models Livro e Usuario
schemas.py       schemas Pydantic
auth.py          hash de senha, geração e validação do JWT
main.py          rotas de usuário, login e CRUD de livros
alembic/         configuração e migrações (versions/)
```

## Como rodar

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
fastapi dev main.py
```

Documentação (Swagger): http://127.0.0.1:8000/docs

A chave usada para assinar os tokens vem da variável de ambiente `SECRET_KEY`. Se ela não for definida, é usada uma chave de desenvolvimento. Para gerar uma chave:

```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

## Testando o login pelo Swagger

1. Abra http://127.0.0.1:8000/docs.
2. Em `POST /usuarios`, clique em **Try it out** e cadastre um usuário:
   ```json
   { "email": "admin@biblioteca.com", "senha": "admin123" }
   ```
3. Clique no botão **Authorize** (cadeado no topo da página). Preencha `username` com o e-mail e `password` com a senha, e confirme.
4. A partir daí, o Swagger envia o token automaticamente nas rotas protegidas. Teste um `POST /livros`.

Sem autorizar, as rotas POST, PUT e DELETE de `/livros` respondem `401 Unauthorized`.

## Testando pelo terminal

```bash
curl -X POST http://127.0.0.1:8000/token \
  -d "username=admin@biblioteca.com&password=admin123"

curl -X POST http://127.0.0.1:8000/livros \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Dom Casmurro", "autor": "Machado de Assis", "ano": 1899}'
```

## Exemplo de token gerado

Resposta de `POST /token` para o usuário `admin@biblioteca.com`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBiaWJsaW90ZWNhLmNvbSIsImV4cCI6MTc5MzQ5MzU2MH0.weoS6PZmfu5JC-hn3dv4gD7WG2tGEaJdV4losxLXqug",
  "token_type": "bearer"
}
```

Decodificado (em https://jwt.io), o payload tem o e-mail do usuário em `sub` e a data de expiração em `exp`. O token vale por 30 minutos.

```json
{ "sub": "admin@biblioteca.com", "exp": 1793493560 }
```

## Rotas

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/usuarios` | público | Cadastra um usuário |
| POST | `/token` | público | Login, retorna o JWT |
| GET | `/livros` | público | Lista livros (filtros: `autor`, `disponivel`) |
| GET | `/livros/{id}` | público | Busca um livro |
| POST | `/livros` | autenticado | Cadastra um livro |
| PUT | `/livros/{id}` | autenticado | Atualiza um livro |
| DELETE | `/livros/{id}` | autenticado | Remove um livro |
