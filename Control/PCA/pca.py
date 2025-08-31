import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# --- Funções Auxiliares (Lógica Interna) ---

def _preprocessar_para_pca(df_features: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara o DataFrame para a análise de PCA, aplicando one-hot encoding
    nas colunas categóricas e padronização (scaling) nas numéricas.

    Args:
        df_features (pd.DataFrame): DataFrame contendo apenas as features (sem 'id_cliente').

    Returns:
        pd.DataFrame: DataFrame processado e pronto para a aplicação do PCA.
    """
    # Identifica colunas de forma dinâmica para maior robustez.
    colunas_numericas = df_features.select_dtypes(include=np.number).columns.tolist()
    colunas_categoricas = df_features.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # One-Hot Encoding para as colunas categóricas.
    df_categoricas_encoded = pd.get_dummies(df_features[colunas_categoricas])

    # Padronização (Standardization) para as colunas numéricas.
    scaler = StandardScaler()
    df_numericas_scaled = pd.DataFrame(
        scaler.fit_transform(df_features[colunas_numericas]), 
        columns=colunas_numericas, 
        index=df_features.index
    )

    # Concatena as features processadas.
    return pd.concat([df_numericas_scaled, df_categoricas_encoded], axis=1)

# --- Função Principal de Orquestração ---

def analise_pca(df_prospects: pd.DataFrame) -> pd.DataFrame:
    """
    Executa a Análise de Componentes Principais (PCA) em um DataFrame de prospects.
    O objetivo é reduzir a dimensionalidade dos dados para visualização.

    Args:
        df_prospects (pd.DataFrame): O DataFrame contendo os dados dos prospects.

    Returns:
        pd.DataFrame: Uma cópia do DataFrame original com as duas primeiras 
                      componentes principais (PC_1, PC_2) adicionadas.
    """
    # 1. Prepara os dados, removendo o identificador.
    df_features = df_prospects.drop('id_cliente', axis=1, errors='ignore')
    df_processado = _preprocessar_para_pca(df_features)

    # 2. Aplica o PCA para extrair os componentes.
    # Instanciamos e aplicamos o PCA em uma única etapa.
    pca = PCA(n_components=2) # Calculamos apenas os 2 componentes necessários para o gráfico.
    componentes_principais = pca.fit_transform(df_processado)

    # 3. Consolida o resultado.
    # Adiciona os dois componentes principais ao DataFrame original para a visualização.
    df_resultado = df_prospects.copy()
    df_resultado['PC_1'] = componentes_principais[:, 0]
    df_resultado['PC_2'] = componentes_principais[:, 1]
    
    return df_resultado

# # --- Exemplo de Uso (para teste do módulo) ---
# if __name__ == '__main__':
#     # Simula um DataFrame de entrada, como seria recebido do app.py
#     dados_exemplo = {
#         'id_cliente': [1, 2, 3, 4],
#         'valor_divida_mil': [10.5, 5.2, 20.0, 2.1],
#         'tempo_inadimplencia_dias': [365, 180, 730, 90],
#         'porte_cliente': ['Pequeno', 'Médio', 'Grande', 'Pequeno'],
#         'ramo_atuacao_cliente': ['VAREJO', 'INDUSTRIA', 'SERVICOS', 'VAREJO'],
#         'score_risco_interno': ['B', 'C', 'A', 'B'],
#         'regiao': ['SUDESTE', 'SUL', 'NORDESTE', 'SUDESTE']
#     }
#     df_teste = pd.DataFrame(dados_exemplo)

#     # Executa a função principal com o DataFrame
#     df_com_pca = analise_pca(df_teste)

#     print("--- Análise de PCA Concluída com Sucesso ---")
#     print(df_com_pca)