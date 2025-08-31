import numpy as np
import streamlit as st

def rodar_simulacao(df_carteira, n_simulacoes):
    """
    Roda uma simulação de Monte Carlo sobre uma carteira de prospects.

    Args:
        df_carteira (pd.DataFrame): DataFrame com as colunas 'score_recuperacao' e 'valor_divida_mil'.
        n_simulacoes (int): O número de cenários a serem simulados.

    Returns:
        list: Uma lista contendo o valor total recuperado para cada simulação.
    """
    print(f"Iniciando Simulação de Monte Carlo com {n_simulacoes} cenários...")
    
    # Extrair as probabilidades e valores para arrays NumPy (muito mais rápido)
    probabilidades = df_carteira['score_recuperacao'].values
    valores = df_carteira['valor_divida_mil'].values * 1000 # Convertendo para valor real
    
    resultados_simulacao = []
    
    for i in range(n_simulacoes):
        if i == 0:
            print(f"🎲 Simulando {i+1}/{n_simulacoes}")
        elif i%1000 == 0:
            print(f"🎲 Simulando {i}/{n_simulacoes}")
            
        # Gera um número aleatório (0 a 1) para cada prospect
        random_rolls = np.random.rand(len(df_carteira))
        
        # Compara o número aleatório com a probabilidade de pagamento
        # O resultado é um array de True/False (pagou / não pagou)
        pagou = random_rolls < probabilidades
        
        # Soma o valor da dívida apenas dos que pagaram (onde 'pagou' é True)
        valor_recuperado_nesta_simulacao = np.sum(valores[pagou])
        
        resultados_simulacao.append(valor_recuperado_nesta_simulacao)
        
    print(f"✅ Simulação concluída {n_simulacoes}/{n_simulacoes}")    
    return resultados_simulacao