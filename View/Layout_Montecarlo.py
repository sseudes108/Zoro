import streamlit as st
import locale

def relatorio_sumario(df_final, analise_montecarlo):
    # Defina o locale para Português do Brasil para formatação correta
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        # Fallback para ambientes (como alguns contêineres ou Windows)
        # onde 'pt_BR.UTF-8' pode não estar disponível.
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    
    metrica("Valor Total Carteira:", sum(df_final['valor_divida_mil'])*1000)
    metrica("Média de Recuperação:", analise_montecarlo.get("media_recuperacao"))
    metrica("Desvio Padrão (risco/volatilidade):", analise_montecarlo.get("desvio_padrao"))
    metrica("Cenário Pessimista (Percentil 5):", analise_montecarlo.get("percentil_5"))
    metrica("Cenário Otimista (Percentil 95):", analise_montecarlo.get("percentil_95"))
        
def metrica(nome, valor):
    valor_fmt = locale.currency(valor, grouping=True)
    st.metric(f"{nome} ", f"{valor_fmt}", width='content')
    
def relatorio_preco(ve, analise_preco_montecarlo):    
    metrica("Valor Esperado: ", ve)
    metrica("Custo da Operação: ", analise_preco_montecarlo.get("COP"))
    metrica("Recuperação Liquida Esperada:", analise_preco_montecarlo.get("RLE"))
    metrica("Preço Maximo Viável:", analise_preco_montecarlo.get("PMV"))