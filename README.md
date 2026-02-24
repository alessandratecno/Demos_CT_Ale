# NotaSegura - utilitário de conexão e geração de SQL

Aplicação Flask com duas telas:

1. **Conexão**: informar host/porta/banco/usuário/senha, testar conexão e salvar configuração.
2. **Gerar SQL de deleção**: informar CNPJ, descobrir `users.id` e gerar SQL de deleção para tabelas relacionadas por `user_id`.

## Como executar (modo desenvolvimento)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:8000

## Gerar `.exe` (Windows)

> O `.exe` precisa ser gerado em **Windows** usando o Python para Windows.

1. Abra o terminal na pasta do projeto.
2. Execute:

```bat
build_windows.bat
```

3. O executável será criado em:

```text
dist\NotaSeguraApp.exe
```

### Build manual (opcional)

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-build.txt
pyinstaller --noconfirm --clean --onefile --name NotaSeguraApp --add-data "templates;templates" --add-data "static;static" app.py
```

## Observações

- A configuração salva fica em `db_config.json` (arquivo local).
- Quando rodar como `.exe`, o `db_config.json` será salvo ao lado do executável.
- O SQL é apenas **gerado e exibido** para cópia; não há execução automática de `DELETE`.

## Solução de problemas

### `ModuleNotFoundError: No module named 'MySQLdb'`

Esse erro acontece em alguns ambientes quando alguma lib espera o módulo `MySQLdb`.

Este projeto já inclui compatibilidade via `PyMySQL` (instalado em `requirements.txt` e registrado com `install_as_MySQLdb()` no startup), então normalmente basta reinstalar as dependências no venv:

```bash
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
