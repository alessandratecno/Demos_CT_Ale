# NotaSegura - utilitário de conexão e geração de SQL

Aplicação Flask com duas telas:

1. **Conexão**: informar host/porta/banco/usuário/senha, testar conexão e salvar configuração.
2. **Gerar SQL de deleção**: informar CNPJ, descobrir `users.id` e gerar SQL de deleção para tabelas relacionadas por `user_id`.

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:8000

## Observações

- A configuração salva fica em `db_config.json` (arquivo local).
- O SQL é apenas **gerado e exibido** para cópia; não há execução automática de `DELETE`.
