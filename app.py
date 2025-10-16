import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard Câncer de Mama - Brasil",
    page_icon="🩷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados - CORRIGIDO PARA DADOS POR UF
@st.cache_data
def carregar_dados():
    try:
        # Carregar arquivos do mesmo diretório
        mortalidade = pd.read_csv("mortalidade_tabela2.csv")
        nunca_mamografia = pd.read_csv("nunca_mamografia_fig15.csv")
        mamografos_uf = pd.read_csv("mamografos_regiao_tabela10_total.csv")
        mamografos_sus = pd.read_csv("mamografos_regiao_tabela11_SUS.csv")
        tempo_laudo = pd.read_csv("tempo_laudo_rastreamento_tabela9.csv")
        
        # DEBUG: Verificar colunas de cada arquivo
        st.write("🔍 DEBUG - Colunas dos arquivos:")
        st.write(f"mortalidade: {list(mortalidade.columns)}")
        st.write(f"nunca_mamografia: {list(nunca_mamografia.columns)}")
        st.write(f"mamografos_uf: {list(mamografos_uf.columns)}")
        st.write(f"mamografos_sus: {list(mamografos_sus.columns)}")
        st.write(f"tempo_laudo: {list(tempo_laudo.columns)}")
        
        # Converter porcentagens para numérico
        mamografos_uf['Utilizacao_%'] = mamografos_uf['Utilização(%)'].str.replace('%', '').astype(float)
        
        # CORREÇÃO: Verificar se as colunas de junção existem
        # Primeiro, verificar quais colunas temos em comum
        colunas_mortalidade = set(mortalidade.columns)
        colunas_nunca_mamografia = set(nunca_mamografia.columns)
        colunas_tempo_laudo = set(tempo_laudo.columns)
        
        colunas_comuns = colunas_mortalidade & colunas_nunca_mamografia & colunas_tempo_laudo
        st.write(f"Colunas em comum: {colunas_comuns}")
        
        # Usar 'UF' como chave principal (mais confiável)
        if 'UF' in colunas_mortalidade and 'UF' in colunas_nunca_mamografia and 'UF' in colunas_tempo_laudo:
            # Consolidar dados principais usando UF
            dados = mortalidade.merge(nunca_mamografia, on='UF', how='left')
            dados = dados.merge(tempo_laudo, on='UF', how='left')
        elif 'Regiao' in colunas_mortalidade and 'Regiao' in colunas_nunca_mamografia and 'Regiao' in colunas_tempo_laudo:
            # Tentar com Regiao se UF não estiver disponível
            dados = mortalidade.merge(nunca_mamografia, on='Regiao', how='left')
            dados = dados.merge(tempo_laudo, on='Regiao', how='left')
        else:
            st.error("Não foi possível encontrar colunas comuns para unir os dados")
            return None
        
        # CORREÇÃO: Usar dados específicos por UF (não por região)
        dados = dados.merge(mamografos_uf[['UF', 'Utilizacao_%', 'Mamografos_existentes', 'Mamografos_em_uso']], 
                           on='UF', how='left')
        
        # Adicionar dados do SUS
        dados = dados.merge(mamografos_sus, on='UF', how='left')
        
        st.success("✅ Dados carregados com sucesso!")
        return dados
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        # Mostrar mais detalhes do erro
        import traceback
        st.error(f"Detalhes do erro: {traceback.format_exc()}")
        return None

def calcular_score_criticidade(dados):
    """Calcula score de criticidade para cada estado"""
    dados_score = dados.copy()
    
    # Normalizar cada métrica para escala 0-100
    dados_score['Score_Mortalidade'] = (dados_score['Taxa_mortalidade_ajustada'] / dados_score['Taxa_mortalidade_ajustada'].max() * 100).round(1)
    dados_score['Score_Nao_Rastreadas'] = (dados_score['Percentual_nunca_fez_exame'] / dados_score['Percentual_nunca_fez_exame'].max() * 100).round(1)
    dados_score['Score_Laudos_Lentos'] = (dados_score['Mais_60_dias_%'] / dados_score['Mais_60_dias_%'].max() * 100).round(1)
    
    # Score consolidado com pesos
    dados_score['Score_Consolidado'] = (
        dados_score['Score_Mortalidade'] * 0.35 +      # Peso 35%
        dados_score['Score_Nao_Rastreadas'] * 0.35 +   # Peso 35%
        dados_score['Score_Laudos_Lentos'] * 0.30      # Peso 30%
    ).round(1)
    
    # Classificar por criticidade
    dados_score = dados_score.sort_values('Score_Consolidado', ascending=False)
    
    return dados_score

def criar_tabela_criticidade(dados_score, estado_selecionado=None):
    """Cria tabela com ranking de criticidade"""
    
    st.header("🔎 Ranking de Criticidade por Estado")
    st.markdown("**Classificação baseada na combinação de mortalidade, mulheres não rastreadas e laudos lentos**")
    
    # Criar tabela formatada
    colunas_disponiveis = []
    for coluna in ['UF', 'Regiao', 'Score_Consolidado', 'Taxa_mortalidade_ajustada', 'Percentual_nunca_fez_exame', 'Mais_60_dias_%', 'Obitos']:
        if coluna in dados_score.columns:
            colunas_disponiveis.append(coluna)
    
    tabela_display = dados_score[colunas_disponiveis].copy()
    
    # Renomear colunas
    mapeamento_colunas = {
        'UF': 'UF',
        'Regiao': 'Região', 
        'Score_Consolidado': 'Score Crítico',
        'Taxa_mortalidade_ajustada': 'Mortalidade',
        'Percentual_nunca_fez_exame': '% Não Rastreadas',
        'Mais_60_dias_%': '% Laudos >60d',
        'Obitos': 'Óbitos'
    }
    
    tabela_display.columns = [mapeamento_colunas.get(col, col) for col in tabela_display.columns]
    
    # Formatar valores
    if 'Mortalidade' in tabela_display.columns:
        tabela_display['Mortalidade'] = tabela_display['Mortalidade'].round(1)
    if '% Não Rastreadas' in tabela_display.columns:
        tabela_display['% Não Rastreadas'] = tabela_display['% Não Rastreadas'].round(1)
    if '% Laudos >60d' in tabela_display.columns:
        tabela_display['% Laudos >60d'] = tabela_display['% Laudos >60d'].round(1)
    
    # Adicionar ranking
    tabela_display.insert(0, 'Posição', range(1, len(tabela_display) + 1))
    
    # Estilizar a tabela
    def color_score(val):
        if val >= 80:
            return 'background-color: #ff4d4d; color: white; font-weight: bold'
        elif val >= 60:
            return 'background-color: #ff9999; color: black; font-weight: bold'
        elif val >= 40:
            return 'background-color: #ffcc99; color: black;'
        elif val >= 20:
            return 'background-color: #ffff99; color: black;'
        else:
            return 'background-color: #ccffcc; color: black;'
    
    def color_estado_selecionado(row):
        if estado_selecionado and row['UF'] == estado_selecionado:
            return ['background-color: #EE82EE; font-weight: bold;'] * len(row)
        else:
            return [''] * len(row)
    
    # Aplicar estilos apenas se a coluna existir
    styled_table = tabela_display.style.apply(color_estado_selecionado, axis=1)
    
    if 'Score Crítico' in tabela_display.columns:
        styled_table = styled_table.applymap(color_score, subset=['Score Crítico'])
    
    # Exibir tabela
    st.dataframe(
        styled_table,
        use_container_width=True,
        height=800
    )
    
    # Legenda
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("**🔴 ≥80: Crítico**")
    with col2:
        st.markdown("**🟠 60-79: Alto**")
    with col3:
        st.markdown("**🟡 40-59: Médio**")
    with col4:
        st.markdown("**🟢 20-39: Baixo**")
    with col5:
        st.markdown("**🟢 <20: Muito Baixo**")
    
    return tabela_display

# ... (as outras funções permanecem as mesmas, mas vou manter apenas as essenciais para o exemplo)

def criar_visao_infraestrutura(dados, estado_selecionado):
    """Cria visualização focada em infraestrutura - CORRIGIDA"""
    st.header("🖥️ Infraestrutura de Mamógrafos")
    
    estado_data = dados[dados['UF'] == estado_selecionado].iloc[0]
    utilizacao_estado = estado_data['Utilizacao_%']
    mamografos_sus = estado_data['Mamografos_SUS']
    mamografos_existentes = estado_data['Mamografos_existentes']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Utilização de Mamógrafos",
            f"{utilizacao_estado:.1f}%",
            help="% de mamógrafos existentes que estão em uso"
        )
    
    with col2:
        st.metric(
            "Mamógrafos do SUS",
            f"{mamografos_sus:.0f}",
            f"de {mamografos_existentes:.0f} existentes"
        )
    
    with col3:
        if utilizacao_estado > 100:
            status = "❌ Dados Inconsistentes"
        elif utilizacao_estado > 80:
            status = "✅ Boa Utilização"
        elif utilizacao_estado > 60:
            status = "⚠️ Capacidade Ociosa"
        else:
            status = "🔴 Baixa Utilização"
        st.metric(
            "Situação",
            status,
            "infraestrutura"
        )
    
    # OBSERVAÇÃO ESPECÍFICA DO ESTADO
    if estado_selecionado == 'PR':
        st.error(f"**Observação - {estado_selecionado}:** ⚠️ DADO INCONSISTENTE: Utilização de {utilizacao_estado}% (impossível), com {estado_data['Mamografos_em_uso']} mamógrafos em uso para apenas {mamografos_existentes} existentes, sendo {mamografos_sus} pelo SUS")
    else:
        st.info(f"**Observação - {estado_selecionado}:** Utilização de {utilizacao_estado}%, com {estado_data['Mamografos_em_uso']} mamógrafos em uso, sendo {mamografos_sus} pelo SUS")

def main():
    st.title("🎀 Câncer de Mama no Brasil 🎀 ")
    st.markdown("### Análise Integrada: Mortalidade, Rastreamento e Infraestrutura")
    
    # Carregar dados CORRIGIDOS
    dados = carregar_dados()
    
    if dados is None:
        st.error("Não foi possível carregar os dados. Verifique se todos os arquivos CSV estão no mesmo diretório:")
        st.markdown("""
        - `mortalidade_tabela2.csv`
        - `nunca_mamografia_fig15.csv` 
        - `mamografos_regiao_tabela10_total.csv`
        - `mamografos_regiao_tabela11_SUS.csv`
        - `tempo_laudo_rastreamento_tabela9.csv`
        """)
        return
    
    # Mostrar preview dos dados carregados
    st.write("📊 Preview dos dados carregados:")
    st.write(dados.head())
    
    # Calcular scores de criticidade
    dados_score = calcular_score_criticidade(dados)
    
    # Sidebar para controles
    with st.sidebar:
        st.header("🎯 Controles")
        
        # Seletor de estado
        estado_selecionado = st.selectbox(
            "Selecione o Estado:",
            options=dados['UF'].unique(),
            index=0
        )
        
        st.markdown("---")
        st.info("""
        **Fontes dos Dados:**
        - 🪦 Tabela 2: Mortalidade (2022)
        - 🩺 Figura 15: Rastreamento (PNS 2019)  
        - 🖥️ Tabela 10: Mamógrafos (por UF)
        - 🏥 Tabela 11: Mamógrafos SUS
        - ⏱️ Tabela 9: Tempo de laudo
        """)
    
    # Layout principal simplificado para teste
    tab1, tab2 = st.tabs(["🚑 Ranking Crítico", "🖥️ Infraestrutura"])
    
    with tab1:
        criar_tabela_criticidade(dados_score, estado_selecionado)
    
    with tab2:
        criar_visao_infraestrutura(dados, estado_selecionado)
    
    # Footer
    st.markdown("---")
    st.markdown("**Fonte**: INCA - Instituto Nacional de Câncer (Dados 2022-2024)")
    st.markdown("**Criado para apoio à tomada de decisão em saúde pública**")
    st.markdown("*Desenvolvido por Tiago Alves - Cientista de Dados - https://www.linkedin.com/in/tiagoalvesds/*")

if __name__ == "__main__":
    main()