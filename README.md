# 🩷 Dashboard de Monitoramento – Câncer de Mama no Brasil

Este projeto consolida e analisa dados oficiais do **INCA (Instituto Nacional de Câncer)** para oferecer uma visão integrada sobre os principais indicadores do câncer de mama no Brasil, com foco em **mortalidade**, **rastreamento**, **infraestrutura de diagnóstico** e **tempo de emissão de laudos**.

---

## 🎯 Objetivos do Projeto

- Identificar **estados prioritários para intervenção**
- Monitorar **indicadores críticos de saúde pública**
- **Subsidiar políticas públicas baseadas em dados**
- Evidenciar **desigualdades regionais** no diagnóstico e tratamento

---

## 📊 Fontes de Dados

Dados oficiais do **Ministério da Saúde / INCA (2024)**:

| Indicador | Referência | Ano | Fonte |
|------------|------------|-----|-------|
| 🩸 Mortalidade | Tabela 2 – INCA | 2022 | `mortalidade_tabela2.csv` |
| 🚺 Rastreamento (Mamografia) | Figura 15 – PNS | 2019 | `nunca_mamografia_fig15.csv` |
| 🏥 Infraestrutura (Mamógrafos) | Tabela 10 – INCA | 2023 | `mamografos_regiao_tabela10_total.csv` |
| ⏱️ Tempo de Laudo | Tabela 9 – INCA | 2023 | `tempo_laudo_rastreamento_tabela9.csv` |

---

## 🚀 Funcionalidades do Dashboard

### 🔴 Ranking de Criticidade
- Score consolidado baseado nos indicadores principais
- Classificação automática por criticidade
- Filtros por estado e região
- Destaque visual de prioridades

### 🩸 Análise de Mortalidade
- Taxas brutas e ajustadas (por 100 mil mulheres)
- Comparação entre estados
- Gráfico interativo

### 🚺 Cobertura de Rastreamento
- Percentual de mulheres 50–69 anos sem mamografia
- Identificação de déficit de cobertura
- Classificação automática:
  - 🔴 Crítico – 🟠 Alerta – 🟡 Regular – 🟢 Bom

### ⏱️ Tempo de Diagnóstico
- Foco em laudos emitidos **após 60 dias**
- Impacto sobre desfechos clínicos
- Visualização em gráfico de pizza

### 📊 Visão Consolidada
- Radar Chart comparativo por estado
- Índice de criticidade nacional
- Gap de infraestrutura

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Função |
|-------------|--------|
| Python 3.8+ | Backend e base do código |
| Streamlit | Interface web |
| Pandas | Análise de dados |
| Plotly | Visualizações interativas |
| NumPy | Tratamento numérico |

---

## 📦 Instalação e Execução

### ✅ Pré-requisitos
- Python 3.8 ou superior
- `pip` instalado

### 🔧 Passo a passo

```bash
# 1. Clonar o repositório
git clone https://github.com/Tiagoalvesds/Cancer_mama_br.git
cd Cancer_mama_br

# 2. Criar ambiente virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar aplicação
streamlit run app.py

dashboard-cancer-mama/
│
├── app.py                      # Aplicação principal
├── requirements.txt            # Dependências
├── README.md                   # Documentação
│
├── bd/                         # Base de dados
│   ├── mortalidade_tabela2.csv
│   ├── nunca_mamografia_fig15.csv
│   ├── mamografos_regiao_tabela10_total.csv
│   └── tempo_laudo_rastreamento_tabela9.csv
│
└── assets/                     # Imagens e materiais
    └── screenshots/

📈 Score de Criticidade

O índice de criticidade classifica os estados com base em três pilares:

Indicador	Peso	Escala
🩸 Mortalidade ajustada	35%	0–100
🚺 Não rastreio	35%	0–100
⏱️ Laudos > 60 dias	30%	0–100
🔎 Classificação Final
Score	Nível
≥ 80	🔴 Crítico
60–79	🟠 Alto
40–59	🟡 Médio
20–39	🟢 Baixo
< 20	🟢 Muito Baixo
🎨 Personalização
Alterar pesos do score

Edite no arquivo app.py:

peso_mortalidade = 0.35
peso_nao_rastreadas = 0.35
peso_laudos_lentos = 0.30

🤝 Contribuindo

Contribuições são bem-vindas! Para colaborar:

git checkout -b feature/nova-feature
git commit -m "Descrição da feature"
git push origin feature/nova-feature


Abra um Pull Request 🚀

📝 Licença

Distribuído sob a licença MIT. Consulte o arquivo LICENSE.

👨‍💻 Autor

Tiago Alves
📊 Data Science
📩 Email: dstiagoalves@gmail.com

🔗 LinkedIn: https://www.linkedin.com/in/tiagoalvesds/

🏥 Aplicações

Este projeto pode ser usado por:

✅ Gestores públicos
✅ Pesquisadores de saúde coletiva
✅ Profissionais da oncologia
✅ ONGs e instituições de prevenção
✅ Projetos acadêmicos

📅 Dados atualizados: 2024
💡 Construído para salvar vidas através de dados 🩷

