# Código-fonte do IR Smart

Este diretório contém o código-fonte principal do projeto IR Smart.

## Estrutura dos Módulos

| Arquivo | Descrição |
|---------|-----------|
| `app.py` | Interface Streamlit principal |
| `motor_calculo.py` | Engine de cálculo de IR (core do sistema) |
| `chatgpt_client.py` | Cliente para comunicação com GPT-4 |
| `database.py` | Gerenciamento do banco SQLite |
| `validacao.py` | Sistema de validação anti-alucinação |
| `utils.py` | Funções utilitárias |

## Como executar

```bash
# Da raiz do projeto
streamlit run src/app.py
```

## Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   app.py    │────▶│ chatgpt_    │────▶│  motor_     │
│ (Interface) │     │  client.py  │     │ calculo.py  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ database.py │     │ validacao.py│     │  utils.py   │
│   (SQLite)  │     │(Anti-alucin)│     │ (Helpers)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Dependências

- Python 3.10+
- Streamlit
- OpenAI API
- SQLite
- Ver `requirements.txt` na raiz do projeto
