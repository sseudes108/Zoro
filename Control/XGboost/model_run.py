import pandas as pd
import joblib
from typing import Dict, Any

def _carregar_artefatos_modelo(caminho_artefatos: str) -> Dict[str, Any]:
    """
    Carrega os artefatos do modelo (objeto do modelo e lista de colunas) de um arquivo .pkl.
    """
    return joblib.load(caminho_artefatos)

def _preparar_dados_para_predicao(df: pd.DataFrame, colunas_do_treino: list) -> pd.DataFrame:
    """
    Realiza o one-hot encoding e alinha as colunas do DataFrame de prospects
    com as colunas esperadas pelo modelo.
    """
    # Define as colunas categóricas esperadas. É mais robusto definir explicitamente
    # do que inferir, para garantir consistência com o treino.
    colunas_categoricas = ['porte_cliente', 'ramo_atuacao_cliente', 'score_risco_interno', 'regiao']
    
    # Garante que apenas as colunas categóricas existentes no DataFrame sejam processadas.
    colunas_para_encode = [col for col in colunas_categoricas if col in df.columns]
    
    df_encoded = pd.get_dummies(df, columns=colunas_para_encode)
    
    # Remove o identificador, se existir.
    X_prospects = df_encoded.drop('id_cliente', axis=1, errors='ignore')
    
    # Alinha as colunas com o modelo, preenchendo com 0 as que não existem nos dados de entrada.
    # Isso garante que o modelo sempre receba o formato de dados que ele espera.
    X_prospects_aligned = X_prospects.reindex(columns=colunas_do_treino, fill_value=0)
    
    return X_prospects_aligned

def gerar_score_carteira(df_prospects: pd.DataFrame, caminho_artefatos_modelo: str) -> pd.DataFrame:
    """
    Aplica um modelo XGBoost treinado a um DataFrame de prospects para gerar scores de recuperação.

    Args:
        df_prospects (pd.DataFrame): O DataFrame contendo os dados dos prospects.
        caminho_artefatos_modelo (str): O caminho para o arquivo .pkl que contém o modelo e as colunas.

    Returns:
        pd.DataFrame: O DataFrame original com a coluna 'score_recuperacao' adicionada e ordenado.
    """
    # A leitura do CSV foi removida. A função agora recebe o DataFrame diretamente.
    artefatos = _carregar_artefatos_modelo(caminho_artefatos_modelo)
    modelo_carregado = artefatos['model']
    colunas_do_treino = artefatos['columns']

    # Prepara os dados de entrada para terem a mesma estrutura dos dados de treino.
    X_prospects_aligned = _preparar_dados_para_predicao(df_prospects, colunas_do_treino)

    # Gera as probabilidades de recuperação (classe 1).
    scores_recuperacao = modelo_carregado.predict_proba(X_prospects_aligned)[:, 1]

    # Consolida o resultado no DataFrame original.
    df_resultado = df_prospects.copy()
    df_resultado['score_recuperacao'] = scores_recuperacao

    return df_resultado.sort_values(by='score_recuperacao', ascending=False)

# # --- Exemplo de Uso (para teste do módulo) ---
# if __name__ == '__main__':
#     # Simula um DataFrame de entrada, como no app.py
#     dados_exemplo = {
#         'id_cliente': [101, 102, 103],
#         'valor_divida': [5000, 15000, 2000],
#         'dias_atraso': [90, 365, 30],
#         'porte_cliente': ['PEQUENA', 'GRANDE', 'MEDIA'],
#         'ramo_atuacao_cliente': ['VAREJO', 'INDUSTRIA', 'SERVICOS'],
#         'score_risco_interno': ['B', 'C', 'A'],
#         'regiao': ['SUDESTE', 'SUL', 'NORDESTE']
#     }
#     df_teste = pd.DataFrame(dados_exemplo)
    
#     # Caminho para o modelo treinado (deve existir para o teste funcionar)
#     caminho_modelo_teste = 'modelo_score_recuperacao_with_columns_v1.pkl'
    
#     try:
#         df_com_score = gerar_score_carteira(df_teste, caminho_modelo_teste)
#         print("--- Scoring XGBoost Concluído com Sucesso ---")
#         print(df_com_score)
#     except FileNotFoundError:
#         print(f"Erro: Arquivo de modelo não encontrado em '{caminho_modelo_teste}'.")
#         print("Este teste requer que o artefato do modelo treinado esteja no local correto.")