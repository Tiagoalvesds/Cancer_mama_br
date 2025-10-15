# 📋 Sobre o Projeto
Este projeto consolida e analisa dados oficiais do INCA (Instituto Nacional de Câncer) sobre câncer de mama no Brasil, proporcionando uma visão integrada dos principais indicadores de mortalidade, rastreamento, infraestrutura e tempo de diagnóstico.

🎯 Objetivos
Identificar estados prioritários para intervenção

Monitorar indicadores críticos de saúde pública

Subsidiar políticas públicas baseadas em evidências

Visualizar desigualdades regionais no cuidado ao câncer de mama

📊 Fontes de Dados

## MINISTÉRIO DA SAÚDE
 INSTITUTO NACIONAL DE CÂNCER (INCA) 
 
 CONTROLE DO CÂNCER DE MAMA NO BRASIL: DADOS E NÚMEROS DE 2024

🩸 Mortalidade	Tabela 2 INCA	2022	mortalidade_tabela2.csv

🚺 Rastreamento	Figura 15 PNS	2019	nunca_mamografia_fig15.csv

🏥 Infraestrutura	Tabela 10 INCA	2023	mamografos_regiao_tabela10_total.csv

⏱️ Tempo de Laudo	Tabela 9 INCA	2023	tempo_laudo_rastreamento_tabela9.csv

🚀 Funcionalidades

🏆 Ranking de Criticidade

Score consolidado baseado em mortalidade, não rastreamento e laudos lentos

Classificação por cores para priorização

Filtros por região e nível de criticidade

Destaque automático do estado selecionado

🩸 Análise de Mortalidade
Taxas brutas e ajustadas por 100 mil mulheres

Ranking comparativo entre estados

Limites críticos de referência

Visualização em gráfico de barras

🚺 Cobertura de Rastreamento
Percentual de mulheres 50-69 anos não rastreadas

Análise de déficit de cobertura

Classificação por situação (Crítico, Alerta, Regular, Bom)

Metas ideais de cobertura

⏱️ Tempo de Laudo
Foco em laudos com mais de 60 dias (critério crítico)

Análise de impacto nos desfechos clínicos

Recomendações específicas por situação

Visualização em gráfico de pizza

📊 Visão Consolidada
Radar chart comparativo com média nacional

Índice de criticidade personalizado

Análise de infraestrutura por região

Priorização para intervenção

🛠️ Tecnologias Utilizadas
Python 3.8+

Streamlit - Interface web interativa

Pandas - Manipulação e análise de dados

Plotly - Visualizações interativas

NumPy - Cálculos numéricos

📦 Instalação e Execução
Pré-requisitos
Python 3.8 ou superior

pip (gerenciador de pacotes Python)

1. Clone o repositório
bash
git clone https://github.com/seu-usuario/dashboard-cancer-mama.git
cd dashboard-cancer-mama

2. Crie um ambiente virtual (recomendado)
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

3. Instale as dependências
bash
pip install -r requirements.txt

4. Execute a aplicação
bash
streamlit run app.py

5. Acesse no navegador
text
http://localhost:8501

🗂️ Estrutura do Projeto
text
dashboard-cancer-mama/
│
├── app.py                          # Aplicação principal Streamlit
├── requirements.txt                # Dependências do projeto
├── README.md                       # Documentação do projeto
│
├── bd/                             # Diretório de dados
│   ├── mortalidade_tabela2.csv
│   ├── nunca_mamografia_fig15.csv
│   ├── mamografos_regiao_tabela10_total.csv
│   └── tempo_laudo_rastreamento_tabela9.csv
│
└── assets/                         # Imagens e recursos
    └── screenshots/

    
📈 Metodologia do Score de Criticidade
O índice de criticidade é calculado com base em três indicadores principais:

Indicador	Peso	Normalização
🩸 Taxa de Mortalidade Ajustada	35%	Escala 0-100
🚺 % Mulheres Não Rastreadas	35%	Escala 0-100
⏱️ % Laudos > 60 Dias	30%	Escala 0-100
Classificação:

🔴 Crítico: ≥80 pontos

🟠 Alto: 60-79 pontos

🟡 Médio: 40-59 pontos

🟢 Baixo: 20-39 pontos

🟢 Muito Baixo: <20 pontos

🎨 Personalização
Modificando Pesos do Score
Edite a função calcular_score_criticidade no arquivo app.py:

python
# Pesos atuais
peso_mortalidade = 0.35      # 35%
peso_nao_rastreadas = 0.35   # 35%  
peso_laudos_lentos = 0.30    # 30%
Adicionando Novos Indicadores
Adicione o arquivo CSV na pasta bd/

Modifique a função carregar_dados()

Atualize as visualizações correspondentes

🤝 Contribuição
Contribuições são bem-vindas! Siga os passos:

Fork o projeto

Crie uma branch para sua feature (git checkout -b feature/AmazingFeature)

Commit suas mudanças (git commit -m 'Add some AmazingFeature')

Push para a branch (git push origin feature/AmazingFeature)

Abra um Pull Request

📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

🙋‍♂️ Autor
Tiago Alves
DATA SCIENCE

📞 Contato
Email: dstiagoalves@gmail.com

LinkedIn: https://www.linkedin.com/in/tiagoalvesds/

🏥 Aplicações em Saúde Pública
Este dashboard pode ser utilizado por:

Gestores públicos para alocação de recursos

Pesquisadores em saúde coletiva

Profissionais de saúde para planejamento local

Organizações não governamentais para advocacy

Estudantes de saúde pública e medicina

🔄 Atualizações Futuras
Integração com API do DATASUS

Análise temporal (séries históricas)

Comparação internacional

Alertas automáticos por email

Relatórios em PDF automatizados

Desenvolvido para salvar vidas através de dados 💝

Dados atualizados em: 2024
Última atualização do projeto: ${new Date().toLocaleDateString()}


