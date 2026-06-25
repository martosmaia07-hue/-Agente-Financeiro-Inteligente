# 🚀 Passo a Passo de Execução - Pierre (Mentor de Python com IA)

## 🧠 Setup do Ollama

```bash
# 1. Instalar o Ollama
# Acesse: https://ollama.com e instale conforme seu sistema operacional

# 2. Baixar o modelo utilizado no projeto
ollama pull gpt-oss

# 3. Testar se o modelo está funcionando
ollama run gpt-oss "Olá!"
```

## ⚙️ Código Completo

O código principal está no arquivo ```src/app.py```

## 🚀 Como Rodar o Projeto

```
cd seu-repositorio

ollama serve

streamlit run src/app.py
```

## 📁 Estrutura do projeto
```
├── data/
│   ├── erros_comuns.csv
│   ├── historico_duvidas.csv
│   └── perfil_dev.json
│
├── docs/
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
│
├── src/
│   ├── app.py
│   └── README.md
│
└── README.md
```
---
## 📊 Evidência de Execução
<img width="544" height="875" alt="Captura de tela 2026-06-24 163344" src="https://github.com/user-attachments/assets/2d7414e1-faac-4b2d-93fb-0498ae3fc0c1" />
