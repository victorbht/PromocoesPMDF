# 🛡️ Sistema de Projeção de Carreira Militar - PMDF

Sistema para cálculo e projeção de promoções na carreira de praças da Polícia Militar do Distrito Federal, baseado na Lei 12.086/2009.

## 🚀 Funcionalidades

- **Próxima Promoção**: Calcula a data da próxima promoção com base no interstício
- **Plano de Carreira**: Projeta toda a carreira até Subtenente
- **Cenários**: Simula com e sem redução de interstício
- **Cálculo de Idade**: Mostra a idade prevista em cada promoção
- **Export CSV**: Baixa o planejamento completo

## 📋 Pré-requisitos

- Python 3.8+
- pip

## ⚙️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/victorbht/PromocoesPMDF.git
cd PromocoesPMDF
```

2. Crie um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🖥️ Execução

### Versão Web (Streamlit)
```bash
streamlit run app_final.py
```

### Versão Console
```bash
python main.py
```

## 📊 Interstícios (Lei 12.086/2009)

| Graduação | Completo | Reduzido |
|-----------|----------|----------|
| Soldado → Cabo | 120 meses | 60 meses |
| Cabo → 3º Sargento | 60 meses | 30 meses |
| 3º → 2º Sargento | 60 meses | 30 meses |
| 2º → 1º Sargento | 60 meses | 30 meses |
| 1º Sargento → Subtenente | 36 meses | 18 meses |

## 📅 Datas de Promoção

- 22 de Abril
- 21 de Agosto  
- 26 de Dezembro

## ⚠️ Aviso Legal

Esta ferramenta é uma iniciativa independente e **NÃO** possui vínculo oficial com a Polícia Militar do Distrito Federal. Os cálculos são estimativas baseadas na legislação vigente.

## 🛠️ Tecnologias

- Python
- Streamlit
- Pandas
- python-dateutil

## 📄 Licença

MIT License