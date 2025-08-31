import streamlit as st
import locale

import View.Graficos as Graficos

def relatorio_score(dataframe_final):
    # 1. Calcular o "valor esperado" de recuperação (soma de cada dívida * sua probabilidade)
    valor_esperado_total = (dataframe_final['score_recuperacao'] * dataframe_final['valor_divida_mil']).sum()
    # 2. Calcular o valor total da carteira
    valor_total_carteira = dataframe_final['valor_divida_mil'].sum()
    # 3. A média ponderada é a divisão dos dois
    media_ponderada_score_sm = valor_esperado_total / valor_total_carteira
        
    # Seu código original para a soma do valor
    rankA_valor = dataframe_final[dataframe_final['score_recuperacao'] >= 0.75]['valor_divida_mil'].sum()
    rankB_valor = dataframe_final[(dataframe_final['score_recuperacao'] >= 0.50) & (dataframe_final['score_recuperacao'] < 0.75)]['valor_divida_mil'].sum()
    rankC_valor = dataframe_final[(dataframe_final['score_recuperacao'] >= 0.25) & (dataframe_final['score_recuperacao'] < 0.50)]['valor_divida_mil'].sum()
    rankD_valor = dataframe_final[dataframe_final['score_recuperacao'] < 0.25]['valor_divida_mil'].sum()

    # Novo código para a CONTAGEM de linhas em cada rank
    rankA_contagem = len(dataframe_final[dataframe_final['score_recuperacao'] >= 0.75])
    rankB_contagem = len(dataframe_final[(dataframe_final['score_recuperacao'] >= 0.50) & (dataframe_final['score_recuperacao'] < 0.75)])
    rankC_contagem = len(dataframe_final[(dataframe_final['score_recuperacao'] >= 0.25) & (dataframe_final['score_recuperacao'] < 0.50)])
    rankD_contagem = len(dataframe_final[dataframe_final['score_recuperacao'] < 0.25])

    # Agora você pode mostrar os resultados
    print("--- Resumo da Carteira por Rank ---")
    print(f"Rank A (Score >= 0.75): {rankA_contagem} devedores, somando R$ {rankA_valor * 1000:,.2f}")
    print(f"Rank B (Score 0.50-0.74): {rankB_contagem} devedores, somando R$ {rankB_valor * 1000:,.2f}")
    print(f"Rank C (Score 0.25-0.49): {rankC_contagem} devedores, somando R$ {rankC_valor * 1000:,.2f}")
    print(f"Rank D (Score < 0.25): {rankD_contagem} devedores, somando R$ {rankD_valor * 1000:,.2f}")
                    
    gauge_col, relatorio_col, bar_col = st.columns([1.5, 0.7, 1.7])
    
    with gauge_col:
        st.plotly_chart(Graficos.get_gauge(media_ponderada_score_sm * 100))
        
    with relatorio_col:
        # Multiplique por 1000 para obter o valor real e formate como moeda
        rankA_fmt = locale.currency(rankA_valor * 1000, grouping=True)
        rankB_fmt = locale.currency(rankB_valor * 1000, grouping=True)
        rankC_fmt = locale.currency(rankC_valor * 1000, grouping=True)
        rankD_fmt = locale.currency(rankD_valor * 1000, grouping=True)
        st.metric("Rank A", rankA_fmt)
        st.metric("Rank B", rankB_fmt)
        st.metric("Rank C", rankC_fmt)
        st.metric("Rank D", rankD_fmt)
        
    with bar_col:
        values = [rankA_valor, rankB_valor, rankC_valor, rankD_valor]
        st.plotly_chart(Graficos.get_bar(values))