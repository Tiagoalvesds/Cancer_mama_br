import pandas as pd
import os

def validar_dados_mamografos_local():
    """Validação local dos dados de mamógrafos"""
    
    # Caminho do diretório
    base_path = "/home/iauser/1.Tiago_Alves/portfolio/cancer_mama/bd"
    
    try:
        # Carregar dados
        mamografos_uf = pd.read_csv(os.path.join(base_path, "mamografos_regiao_tabela10_total.csv"))
        mamografos_sus = pd.read_csv(os.path.join(base_path, "mamografos_regiao_tabela11_SUS.csv"))
        
        # Converter porcentagens para numérico
        mamografos_uf['Utilizacao_%'] = mamografos_uf['Utilização(%)'].str.replace('%', '').astype(float)
        
        # Juntar dados
        dados_completos = mamografos_uf.merge(mamografos_sus, on='UF', how='left')
        
        # Calcular percentual do SUS
        dados_completos['%_SUS'] = (dados_completos['Mamografos_SUS'] / dados_completos['Mamografos_existentes'] * 100).round(1)
        
        # Criar tabela de validação
        print("=" * 100)
        print("📊 VALIDAÇÃO DOS DADOS DE MAMÓGRAFOS POR UF")
        print("=" * 100)
        
        # Tabela principal
        colunas = ['UF', 'Mamografos_existentes', 'Mamografos_em_uso', 'Utilizacao_%', 'Mamografos_SUS', '%_SUS']
        dados_validacao = dados_completos[colunas].copy()
        
        # Formatar para display
        for index, row in dados_validacao.iterrows():
            status = "✅ OK"
            if row['Mamografos_em_uso'] > row['Mamografos_existentes']:
                status = "❌ INCONSISTENTE"
            elif row['Utilizacao_%'] > 100:
                status = "⚠️  SUPERIOR A 100%"
            
            print(f"{row['UF']:.<25} {row['Mamografos_existentes']:>3} existentes | {row['Mamografos_em_uso']:>3} em uso | {row['Utilizacao_%']:>6.2f}% | {row['Mamografos_SUS']:>3} SUS ({row['%_SUS']:>4.1f}%) {status}")
        
        print("\n" + "=" * 100)
        
        # Estatísticas
        total_existentes = dados_validacao['Mamografos_existentes'].sum()
        total_em_uso = dados_validacao['Mamografos_em_uso'].sum()
        total_sus = dados_validacao['Mamografos_SUS'].sum()
        
        print(f"📈 ESTATÍSTICAS GERAIS:")
        print(f"   Total de mamógrafos existentes: {total_existentes}")
        print(f"   Total de mamógrafos em uso: {total_em_uso}")
        print(f"   Total de mamógrafos SUS: {total_sus}")
        print(f"   Utilização média: {(total_em_uso/total_existentes*100):.1f}%")
        print(f"   Percentual SUS: {(total_sus/total_existentes*100):.1f}%")
        
        # Problemas identificados
        problemas = dados_validacao[dados_validacao['Mamografos_em_uso'] > dados_validacao['Mamografos_existentes']]
        if not problemas.empty:
            print(f"\n🚨 PROBLEMAS IDENTIFICADOS:")
            for _, problema in problemas.iterrows():
                print(f"   - {problema['UF']}: {problema['Mamografos_em_uso']} em uso > {problema['Mamografos_existentes']} existentes")
        
        return dados_validacao
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return None

def validar_estados_especificos():
    """Validação de estados específicos com problemas conhecidos"""
    
    base_path = "/home/iauser/1.Tiago_Alves/portfolio/cancer_mama/bd"
    
    try:
        mamografos_uf = pd.read_csv(os.path.join(base_path, "mamografos_regiao_tabela10_total.csv"))
        mamografos_uf['Utilizacao_%'] = mamografos_uf['Utilização(%)'].str.replace('%', '').astype(float)
        
        print("\n" + "=" * 80)
        print("🎯 VALIDAÇÃO DE ESTADOS ESPECÍFICOS")
        print("=" * 80)
        
        estados_validar = ['GO', 'PR', 'SP', 'RJ', 'MG']
        
        for uf in estados_validar:
            estado_data = mamografos_uf[mamografos_uf['UF'] == uf].iloc[0]
            print(f"{uf}: {estado_data['Utilizacao_%']:.2f}% (CSV)")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"Erro na validação específica: {e}")

# Executar validação
if __name__ == "__main__":
    print("Iniciando validação dos dados de mamógrafos...")
    dados_validados = validar_dados_mamografos_local()
    validar_estados_especificos()