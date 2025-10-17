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

# Carregar dados - CORRIGIDO
@st.cache_data
def carregar_dados():
    try:
        # Carregar arquivos do mesmo diretório
        mortalidade = pd.read_csv("mortalidade_tabela2.csv")
        nunca_mamografia = pd.read_csv("nunca_mamografia_fig15.csv")
        mamografos_uf = pd.read_csv("mamografos_regiao_tabela10_total.csv")
        mamografos_sus = pd.read_csv("mamografos_regiao_tabela11_SUS.csv")
        tempo_laudo = pd.read_csv("tempo_laudo_rastreamento_tabela9.csv")
        
        # CORREÇÃO: Converter porcentagens para numérico (já estão numéricas nos arquivos)
        mamografos_uf['Utilizacao_%'] = mamografos_uf['Utilização(%)'].astype(float)
        
        # CORREÇÃO: Usar apenas UF como chave (mais confiável)
        # Consolidar dados principais usando UF
        dados = mortalidade.merge(nunca_mamografia, on='UF', how='left')
        dados = dados.merge(tempo_laudo, on='UF', how='left')
        
        # CORREÇÃO: Usar dados específicos por UF
        dados = dados.merge(mamografos_uf[['UF', 'Utilizacao_%']], on='UF', how='left')
        
        # Adicionar dados do SUS
        dados = dados.merge(mamografos_sus, on='UF', how='left')
        
        return dados
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
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
    tabela_display = dados_score[[
        'UF', 'Regiao', 'Score_Consolidado', 
        'Taxa_mortalidade_ajustada', 'Percentual_nunca_fez_exame', 'Mais_60_dias_%', 'Obitos'
    ]].copy()
    
    # Renomear colunas
    tabela_display.columns = [
        'UF', 'Região', 'Score Crítico', 
        'Mortalidade', '% Não Rastreadas', '% Laudos >60d', 'Óbitos'
    ]
    
    # Formatar valores
    tabela_display['Mortalidade'] = tabela_display['Mortalidade'].round(1)
    tabela_display['% Não Rastreadas'] = tabela_display['% Não Rastreadas'].round(1)
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
    
    # Aplicar estilos
    styled_table = tabela_display.style.apply(color_estado_selecionado, axis=1)\
                                      .applymap(color_score, subset=['Score Crítico'])\
                                      .format({
                                          'Score Crítico': '{:.1f}',
                                          'Mortalidade': '{:.1f}',
                                          '% Não Rastreadas': '{:.1f}%',
                                          '% Laudos >60d': '{:.1f}%',
                                          'Óbitos': '{:.0f}'
                                      })
    
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

def criar_visao_mortalidade(dados, estado_selecionado):
    """Cria visualização focada em mortalidade"""
    st.header("🪦 Análise de Mortalidade por Câncer de Mama")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        taxa_estado = dados[dados['UF'] == estado_selecionado]['Taxa_mortalidade_ajustada'].iloc[0]
        media_br = dados['Taxa_mortalidade_ajustada'].mean()
        diff = taxa_estado - media_br
        st.metric(
            "Taxa de Mortalidade Ajustada",
            f"{taxa_estado:.1f}",
            f"{diff:+.1f} vs BR",
            delta_color="inverse" if diff > 0 else "normal"
        )
    
    with col2:
        obitos_estado = dados[dados['UF'] == estado_selecionado]['Obitos'].iloc[0]
        total_br = dados['Obitos'].sum()
        participacao = (obitos_estado / total_br * 100)
        st.metric(
            "Óbitos Registrados (2022)",
            f"{obitos_estado:.0f}",
            f"{participacao:.1f}% do total BR"
        )
    
    with col3:
        taxa_bruta = dados[dados['UF'] == estado_selecionado]['Taxa_bruta'].iloc[0]
        st.metric(
            "Taxa Bruta de Mortalidade",
            f"{taxa_bruta:.1f}",
            "por 100 mil mulheres"
        )
    
    with col4:
        ranking = dados['Taxa_mortalidade_ajustada'].rank(ascending=False)
        posicao = int(ranking[dados['UF'] == estado_selecionado].iloc[0])
        st.metric(
            "Posição no Ranking",
            f"{posicao}º lugar",
            f"de {len(dados)} estados"
        )
    
    # Gráfico de comparação
    fig = go.Figure()
    
    dados_ordenados = dados.sort_values('Taxa_mortalidade_ajustada', ascending=True)
    
    # Barras para todos os estados
    fig.add_trace(go.Bar(
        y=dados_ordenados['UF'],
        x=dados_ordenados['Taxa_mortalidade_ajustada'],
        orientation='h',
        marker_color=['red' if uf == estado_selecionado else 'lightgray' for uf in dados_ordenados['UF']],
        name='Taxa de Mortalidade'
    ))
    
    fig.add_vline(x=media_br, line_dash="dash", line_color="blue", annotation_text="Média BR")
    fig.add_vline(x=13.0, line_dash="dash", line_color="red", annotation_text="Limite Crítico")
    
    fig.update_layout(
        height=400,
        title="Comparação da Taxa de Mortalidade entre Estados",
        xaxis_title="Taxa de Mortalidade Ajustada (por 100 mil mulheres)",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def criar_visao_rastreamento(dados, estado_selecionado):
    """Cria visualização focada em rastreamento"""
    st.header("☂️ Cobertura de Rastreamento por Mamografia")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nao_rastreadas = dados[dados['UF'] == estado_selecionado]['Percentual_nunca_fez_exame'].iloc[0]
        media_br = dados['Percentual_nunca_fez_exame'].mean()
        diff = nao_rastreadas - media_br
        st.metric(
            "Mulheres Não Rastreadas",
            f"{nao_rastreadas:.1f}%",
            f"{diff:+.1f}% vs BR",
            delta_color="inverse" if diff > 0 else "normal",
            help="% mulheres 50-69 anos que nunca fizeram mamografia"
        )
    
    with col2:
        rastreadas = 100 - nao_rastreadas
        st.metric(
            "Cobertura de Rastreamento",
            f"{rastreadas:.1f}%",
            "mulheres 50-69 anos"
        )
    
    with col3:
        deficit = max(0, nao_rastreadas - 25)  # Meta ideal seria <25%
        st.metric(
            "Déficit de Cobertura",
            f"{deficit:.1f}%",
            "acima da meta ideal",
            delta_color="off"
        )
    
    # Análise de situação
    st.subheader("📊 Situação do Rastreamento")
    
    if nao_rastreadas > 40:
        st.error("**CRÍTICO**: Mais de 40% das mulheres nunca fizeram mamografia - necessidade urgente de ampliação do acesso")
    elif nao_rastreadas > 30:
        st.warning("**ALERTA**: Entre 30-40% de não rastreadas - necessidade de fortalecimento das ações")
    elif nao_rastreadas > 20:
        st.info("**REGULAR**: Entre 20-30% de não rastreadas - pode melhorar")
    else:
        st.success("**BOM**: Menos de 20% de não rastreadas - situação satisfatória")

def criar_visao_infraestrutura(dados, estado_selecionado):
    """Cria visualização focada em infraestrutura - CORRIGIDA"""
    st.header("🖥️ Infraestrutura de Mamógrafos")
    
    estado_data = dados[dados['UF'] == estado_selecionado].iloc[0]
    utilizacao_estado = estado_data['Utilizacao_%']
    mamografos_sus = estado_data['Mamografos_SUS']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Utilização de Mamógrafos",
            f"{utilizacao_estado:.1f}%",
            "no estado",
            help="% de mamógrafos existentes que estão em uso"
        )
    
    with col2:
        st.metric(
            "Mamógrafos do SUS",
            f"{mamografos_sus:.0f}",
            "disponíveis",
            help="Quantidade de mamógrafos do SUS no estado"
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
    observacoes = {
        'ACRE': f"Utilização de {utilizacao_estado:.1f}%, com 19 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'AMAPÁ': f"Utilização de {utilizacao_estado:.1f}%, com 25 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'AMAZONAS': f"Utilização de {utilizacao_estado:.1f}%, com 103 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'PARÁ': f"Utilização de {utilizacao_estado:.1f}%, com 176 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'RONDÔNIA': f"Utilização de {utilizacao_estado:.1f}%, com 60 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'RORAIMA': f"Utilização de {utilizacao_estado:.1f}%, com 9 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'TOCANTINS': f"Utilização de {utilizacao_estado:.1f}%, com 41 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'ALAGOAS': f"Utilização de {utilizacao_estado:.1f}%, com 98 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'BAHIA': f"Utilização de {utilizacao_estado:.1f}%, com 406 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'CEARÁ': f"Utilização de {utilizacao_estado:.1f}%, com 205 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'MARANHÃO': f"Utilização de {utilizacao_estado:.1f}%, com 160 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'PARAÍBA': f"Utilização de {utilizacao_estado:.1f}%, com 163 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'PERNAMBUCO': f"Utilização de {utilizacao_estado:.1f}%, com 224 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'PIAUÍ': f"Utilização de {utilizacao_estado:.1f}%, com 93 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'RIO GRANDE DO NORTE': f"Utilização de {utilizacao_estado:.1f}%, com 86 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'SERGIPE': f"Utilização de {utilizacao_estado:.1f}%, com 65 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'ESPÍRITO SANTO': f"Utilização de {utilizacao_estado:.1f}%, com 136 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'MINAS GERAIS': f"Utilização de {utilizacao_estado:.1f}%, com 694 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'RIO DE JANEIRO': f"Utilização de {utilizacao_estado:.1f}%, com 616 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'SÃO PAULO': f"Utilização de {utilizacao_estado:.1f}%, com 1450 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'PARANÁ': f"⚠️ DADO INCONSISTENTE: Utilização de {utilizacao_estado:.1f}% (impossível), com 318 mamógrafos em uso para apenas 117 existentes, sendo {mamografos_sus} pelo SUS",
        'RIO GRANDE DO SUL': f"Utilização de {utilizacao_estado:.1f}%, com 407 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'SANTA CATARINA': f"Utilização de {utilizacao_estado:.1f}%, com 268 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'DISTRITO FEDERAL': f"Utilização de {utilizacao_estado:.1f}%, com 120 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'GOIÁS': f"Utilização de {utilizacao_estado:.1f}%, com 266 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'MATO GROSSO': f"Utilização de {utilizacao_estado:.1f}%, com 128 mamógrafos em uso, sendo {mamografos_sus} pelo SUS",
        'MATO GROSSO DO SUL': f"Utilização de {utilizacao_estado:.1f}%, com 84 mamógrafos em uso, sendo {mamografos_sus} pelo SUS"
    }
    
    observacao = observacoes.get(estado_selecionado, f"Utilização de {utilizacao_estado:.1f}%, com {mamografos_sus} mamógrafos pelo SUS")
    
    if estado_selecionado == 'PARANÁ':
        st.error(f"**Observação - {estado_selecionado}:** {observacao}")
    else:
        st.info(f"**Observação - {estado_selecionado}:** {observacao}")

def criar_visao_tempo_laudo(dados, estado_selecionado):
    """Cria visualização focada no tempo de laudo"""
    st.header("⏱️ Tempo para Emissão de Laudos")
    
    estado_data = dados[dados['UF'] == estado_selecionado].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        mais_60 = estado_data['Mais_60_dias_%']
        media_br = dados['Mais_60_dias_%'].mean()
        diff = mais_60 - media_br
        st.metric(
            "Laudos > 60 Dias",
            f"{mais_60:.1f}%",
            f"{diff:+.1f}% vs BR",
            delta_color="inverse" if diff > 0 else "normal",
            help="Percentual de laudos que demoram mais de 60 dias"
        )
    
    with col2:
        ate_30 = estado_data['Ate_30_dias_%']
        st.metric(
            "Laudos ≤ 30 Dias",
            f"{ate_30:.1f}%",
            "dentro do prazo ideal"
        )
    
    with col3:
        entre_31_60 = estado_data['31_60_dias_%']
        st.metric(
            "Laudos 31-60 Dias",
            f"{entre_31_60:.1f}%",
            "prazo intermediário"
        )
    
    with col4:
        if mais_60 > 30:
            situacao = "❌ Crítica"
        elif mais_60 > 20:
            situacao = "⚠️  Preocupante"
        else:
            situacao = "✅ Aceitável"
        st.metric(
            "Situação",
            situacao,
            "tempo de laudo"
        )
    
    # Gráfico de pizza
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=['Até 30 dias', '31-60 dias', 'Mais de 60 dias'],
        values=[ate_30, entre_31_60, mais_60],
        marker_colors=['green', 'orange', 'red'],
        hole=0.4,
        textinfo='percent+label'
    ))
    
    fig.update_layout(
        height=400,
        title="Distribuição do Tempo para Emissão de Laudos",
        annotations=[dict(text='Tempo<br>Laudo', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise crítica
    st.subheader("🌎 Impacto dos Laudos com Mais de 60 Dias")
    
    if mais_60 > 30:
        st.error(f"""
        **SITUAÇÃO CRÍTICA**: {mais_60:.1f}% dos laudos demoram mais de 60 dias
        
        **Impactos:**
        - 🚨 **Atraso no diagnóstico** e início do tratamento
        - 📈 **Progressão da doença** para estágios mais avançados
        - 💔 **Aumento da mortalidade** e piora na qualidade de vida
        - 🔥 **Sobrecarga** no sistema de saúde terciário
        
        **Recomendações:**
        - Fortalecer a rede de diagnóstico por imagem
        - Implementar sistema de regulação eficiente
        - Capacitar profissionais para laudo
        - Adotar telemedicina para apoio diagnóstico
        """)
    elif mais_60 > 20:
        st.warning(f"""
        **SITUAÇÃO PREOCUPANTE**: {mais_60:.1f}% dos laudos demoram mais de 60 dias
        
        Necessidade de monitoramento constante e ações preventivas para evitar
        deterioração do serviço.
        """)

def criar_visao_consolidada(dados, estado_selecionado):
    """Cria visão consolidada com todos os indicadores"""
    st.header("📊 Visão Consolidada do Estado")
    
    estado_data = dados[dados['UF'] == estado_selecionado].iloc[0]
    
    # Calcular score de criticidade
    score = (
        (estado_data['Taxa_mortalidade_ajustada'] / 20 * 30) +  # Peso 30%
        (estado_data['Percentual_nunca_fez_exame'] / 100 * 35) +  # Peso 35%
        (estado_data['Mais_60_dias_%'] / 100 * 35)  # Peso 35%
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Índice de Criticidade")
        st.metric(
            "Score Consolidado",
            f"{score:.1f}/100",
            "quanto maior, mais crítico"
        )
        
        if score > 70:
            st.error("**PRIORIDADE MÁXIMA** - Necessidade de intervenção urgente")
        elif score > 50:
            st.warning("**PRIORIDADE ALTA** - Necessidade de atenção especial")
        elif score > 30:
            st.info("**PRIORIDADE MÉDIA** - Situação requer monitoramento")
        else:
            st.success("**PRIORIDADE BAIXA** - Situação relativamente estável")
    
    with col2:
        # Radar chart com os principais indicadores
        categorias = ['Mortalidade', 'Não Rastreadas', 'Laudos Lentos']
        valores = [
            min(estado_data['Taxa_mortalidade_ajustada'] / 20 * 100, 100),
            estado_data['Percentual_nunca_fez_exame'],
            estado_data['Mais_60_dias_%']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=valores + [valores[0]],  # Fechar o radar
            theta=categorias + [categorias[0]],
            fill='toself',
            name=estado_selecionado,
            line=dict(color='red')
        ))
        
        # Adicionar média BR como referência
        valores_media = [
            min(dados['Taxa_mortalidade_ajustada'].mean() / 20 * 100, 100),
            dados['Percentual_nunca_fez_exame'].mean(),
            dados['Mais_60_dias_%'].mean()
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=valores_media + [valores_media[0]],
            theta=categorias + [categorias[0]],
            fill='toself',
            name='Média Brasil',
            line=dict(color='blue')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("🎀 Câncer de Mama no Brasil 🎀 ")
    st.markdown("### Análise Integrada: Mortalidade, Rastreamento e Infraestrutura")
    
    # Carregar dados
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
    
    # Calcular scores de criticidade
    dados_score = calcular_score_criticidade(dados)
    
    # Sidebar para controles
    with st.sidebar:
        st.header("🎯 Controles")
        
        # Seletor de estado
        estado_selecionado = st.selectbox(
            "Selecione o Estado:",
            options=dados['UF'].unique(),
            index=24  # SP como padrão
        )
        
        st.markdown("---")
        st.header("📊 Filtros da Tabela")
        
        # Filtro por região
        regioes = ['Todas'] + list(dados['Regiao'].unique())
        regiao_filtro = st.selectbox("Filtrar por região:", regioes)
        
        # Filtro por nível de criticidade
        nivel_criticidade = st.selectbox(
            "Filtrar por criticidade:",
            ['Todos', 'Crítico (≥80)', 'Alto (60-79)', 'Médio (40-59)', 'Baixo (20-39)', 'Muito Baixo (<20)']
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
    
    # Layout principal
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚑 Ranking Crítico", 
        "🪦 Mortalidade", 
        "🩺 Rastreamento", 
        "⏱️ Tempo Laudo", 
        "📊 Visão Consolidada"
    ])
    
    with tab1:
        # Aplicar filtros
        dados_filtrados = dados_score.copy()
        
        if regiao_filtro != 'Todas':
            dados_filtrados = dados_filtrados[dados_filtrados['Regiao'] == regiao_filtro]
        
        if nivel_criticidade != 'Todos':
            if nivel_criticidade == 'Crítico (≥80)':
                dados_filtrados = dados_filtrados[dados_filtrados['Score_Consolidado'] >= 80]
            elif nivel_criticidade == 'Alto (60-79)':
                dados_filtrados = dados_filtrados[dados_filtrados['Score_Consolidado'].between(60, 79.9)]
            elif nivel_criticidade == 'Médio (40-59)':
                dados_filtrados = dados_filtrados[dados_filtrados['Score_Consolidado'].between(40, 59.9)]
            elif nivel_criticidade == 'Baixo (20-39)':
                dados_filtrados = dados_filtrados[dados_filtrados['Score_Consolidado'].between(20, 39.9)]
            elif nivel_criticidade == 'Muito Baixo (<20)':
                dados_filtrados = dados_filtrados[dados_filtrados['Score_Consolidado'] < 20]
        
        criar_tabela_criticidade(dados_filtrados, estado_selecionado)
    
    with tab2:
        criar_visao_mortalidade(dados, estado_selecionado)
    
    with tab3:
        criar_visao_rastreamento(dados, estado_selecionado)
    
    with tab4:
        criar_visao_tempo_laudo(dados, estado_selecionado)
    
    with tab5:
        criar_visao_consolidada(dados, estado_selecionado)
        criar_visao_infraestrutura(dados, estado_selecionado)
    
    # Footer
    st.markdown("---")
    st.markdown("**Fonte**: INCA - Instituto Nacional de Câncer (Dados 2022-2024)")
    st.markdown("**Criado para apoio à tomada de decisão em saúde pública**")
    st.markdown("*Desenvolvido por Tiago Alves - Cientista de Dados - https://www.linkedin.com/in/tiagoalvesds/*")

if __name__ == "__main__":
    main()