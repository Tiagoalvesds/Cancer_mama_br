import pandas as pd
import os

def validar_score_critico():
    """Validação completa do cálculo do Score Crítico"""
    
    base_path = "/home/iauser/1.Tiago_Alves/portfolio/cancer_mama/bd"
    
    try:
        # Carregar as 3 tabelas principais do score
        mortalidade = pd.read_csv(os.path.join(base_path, "mortalidade_tabela2.csv"))
        nunca_mamografia = pd.read_csv(os.path.join(base_path, "nunca_mamografia_fig15.csv"))
        tempo_laudo = pd.read_csv(os.path.join(base_path, "tempo_laudo_rastreamento_tabela9.csv"))
        
        # Consolidar dados (igual ao app.py)
        dados = mortalidade.merge(nunca_mamografia, on=['UF', 'Regiao'], how='left')
        dados = dados.merge(tempo_laudo, on=['UF', 'Regiao'], how='left')
        
        print("=" * 120)
        print("📊 VALIDAÇÃO DO CÁLCULO DO SCORE CRÍTICO")
        print("=" * 120)
        
        # 1. MOSTRAR DADOS BRUTOS
        print("\n1. 📈 DADOS BRUTOS POR ESTADO:")
        print("-" * 120)
        
        colunas_brutas = ['UF', 'Taxa_mortalidade_ajustada', 'Percentual_nunca_fez_exame', 'Mais_60_dias_%', 'Obitos']
        dados_brutos = dados[colunas_brutas].copy()
        
        for index, row in dados_brutos.iterrows():
            print(f"{row['UF']:.<5} Mortalidade: {row['Taxa_mortalidade_ajustada']:>5.1f} | "
                  f"Não Rastreadas: {row['Percentual_nunca_fez_exame']:>5.1f}% | "
                  f"Laudos >60d: {row['Mais_60_dias_%']:>5.1f}% | "
                  f"Óbitos: {row['Obitos']:>4.0f}")
        
        # 2. CÁLCULO DO SCORE (igual ao app.py)
        print("\n2. 🧮 CÁLCULO DO SCORE CRÍTICO:")
        print("-" * 120)
        
        dados_score = dados.copy()
        
        # Normalização para escala 0-100
        dados_score['Score_Mortalidade'] = (dados_score['Taxa_mortalidade_ajustada'] / dados_score['Taxa_mortalidade_ajustada'].max() * 100).round(1)
        dados_score['Score_Nao_Rastreadas'] = (dados_score['Percentual_nunca_fez_exame'] / dados_score['Percentual_nunca_fez_exame'].max() * 100).round(1)
        dados_score['Score_Laudos_Lentos'] = (dados_score['Mais_60_dias_%'] / dados_score['Mais_60_dias_%'].max() * 100).round(1)
        
        # Score consolidado com pesos
        dados_score['Score_Consolidado'] = (
            dados_score['Score_Mortalidade'] * 0.35 +      # Peso 35%
            dados_score['Score_Nao_Rastreadas'] * 0.35 +   # Peso 35%
            dados_score['Score_Laudos_Lentos'] * 0.30      # Peso 30%
        ).round(1)
        
        # Ordenar por score
        dados_score = dados_score.sort_values('Score_Consolidado', ascending=False)
        
        # 3. MOSTRAR CÁLCULO DETALHADO
        print("\n3. 📋 SCORE DETALHADO (TOP 10 ESTADOS):")
        print("-" * 120)
        print("UF    | Score Final | Mortalidade | Não Rastreadas | Laudos Lentos | Contribuições")
        print("      |             |   (35%)     |     (35%)      |    (30%)      |  M + R + L")
        print("-" * 120)
        
        for index, row in dados_score.head(10).iterrows():
            contrib_mortalidade = row['Score_Mortalidade'] * 0.35
            contrib_rastreamento = row['Score_Nao_Rastreadas'] * 0.35
            contrib_laudos = row['Score_Laudos_Lentos'] * 0.30
            
            print(f"{row['UF']:<5} | {row['Score_Consolidado']:>11.1f} | {row['Score_Mortalidade']:>11.1f} | {row['Score_Nao_Rastreadas']:>14.1f} | {row['Score_Laudos_Lentos']:>13.1f} | {contrib_mortalidade:4.1f} + {contrib_rastreamento:4.1f} + {contrib_laudos:4.1f}")
        
        # 4. ESTATÍSTICAS GERAIS
        print("\n4. 📊 ESTATÍSTICAS DOS INDICADORES:")
        print("-" * 120)
        
        print(f"📈 MORTALIDADE (Taxa por 100k):")
        print(f"   Mínimo: {dados['Taxa_mortalidade_ajustada'].min():.1f}")
        print(f"   Máximo: {dados['Taxa_mortalidade_ajustada'].max():.1f} (usado para normalização)")
        print(f"   Média:  {dados['Taxa_mortalidade_ajustada'].mean():.1f}")
        
        print(f"\n🩺 NÃO RASTREADAS (%):")
        print(f"   Mínimo: {dados['Percentual_nunca_fez_exame'].min():.1f}%")
        print(f"   Máximo: {dados['Percentual_nunca_fez_exame'].max():.1f}% (usado para normalização)")
        print(f"   Média:  {dados['Percentual_nunca_fez_exame'].mean():.1f}%")
        
        print(f"\n⏱️  LAUDOS LENTOS (>60 dias):")
        print(f"   Mínimo: {dados['Mais_60_dias_%'].min():.1f}%")
        print(f"   Máximo: {dados['Mais_60_dias_%'].max():.1f}% (usado para normalização)")
        print(f"   Média:  {dados['Mais_60_dias_%'].mean():.1f}%")
        
        # 5. CLASSIFICAÇÃO FINAL
        print("\n5. 🎨 CLASSIFICAÇÃO FINAL POR CRITICIDADE:")
        print("-" * 120)
        
        classificacao = {
            '🔴 CRÍTICO (80-100)': len(dados_score[dados_score['Score_Consolidado'] >= 80]),
            '🟠 ALTO (60-79)': len(dados_score[dados_score['Score_Consolidado'].between(60, 79.9)]),
            '🟡 MÉDIO (40-59)': len(dados_score[dados_score['Score_Consolidado'].between(40, 59.9)]),
            '🟢 BAIXO (20-39)': len(dados_score[dados_score['Score_Consolidado'].between(20, 39.9)]),
            '🟢 MUITO BAIXO (0-19)': len(dados_score[dados_score['Score_Consolidado'] < 20])
        }
        
        for categoria, quantidade in classificacao.items():
            print(f"   {categoria}: {quantidade} estados")
        
        print("=" * 120)
        
        return dados_score
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return None

def validar_estado_especifico(dados_score, uf):
    """Validação detalhada de um estado específico"""
    
    if dados_score is not None:
        estado = dados_score[dados_score['UF'] == uf].iloc[0]
        
        print(f"\n🎯 VALIDAÇÃO DETALHADA - {uf}:")
        print("-" * 80)
        print(f"Score Final: {estado['Score_Consolidado']:.1f}")
        print(f"\nDados Brutos:")
        print(f"  • Mortalidade: {estado['Taxa_mortalidade_ajustada']:.1f}")
        print(f"  • Não Rastreadas: {estado['Percentual_nunca_fez_exame']:.1f}%")
        print(f"  • Laudos >60d: {estado['Mais_60_dias_%']:.1f}%")
        
        print(f"\nScores Normalizados:")
        print(f"  • Mortalidade: {estado['Score_Mortalidade']:.1f} (de 100)")
        print(f"  • Não Rastreadas: {estado['Score_Nao_Rastreadas']:.1f} (de 100)")
        print(f"  • Laudos Lentos: {estado['Score_Laudos_Lentos']:.1f} (de 100)")
        
        print(f"\nContribuições:")
        contrib_mortalidade = estado['Score_Mortalidade'] * 0.35
        contrib_rastreamento = estado['Score_Nao_Rastreadas'] * 0.35
        contrib_laudos = estado['Score_Laudos_Lentos'] * 0.30
        
        print(f"  • Mortalidade (35%): {contrib_mortalidade:.1f}")
        print(f"  • Não Rastreadas (35%): {contrib_rastreamento:.1f}")
        print(f"  • Laudos Lentos (30%): {contrib_laudos:.1f}")
        print(f"  • TOTAL: {contrib_mortalidade + contrib_rastreamento + contrib_laudos:.1f}")

# Executar validação
if __name__ == "__main__":
    print("Iniciando validação do Score Crítico...")
    dados_validados = validar_score_critico()
    
    # Validar estado específico (exemplo: SP)
    if dados_validados is not None:
        validar_estado_especifico(dados_validados, 'SP')