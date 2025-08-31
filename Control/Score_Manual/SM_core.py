import json
from typing import Dict, List, Any

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# --- Bloco de Funções Modulares ---

def _carregar_configuracao_pesos(caminho_pesos: str) -> Dict[str, Any]:
    """
    Carrega os pesos e configurações a partir de um arquivo JSON.
    Isso centraliza a lógica de negócios, facilitando ajustes.
    """
    with open(caminho_pesos, 'r', encoding='utf-8') as f:
        return json.load(f)

def _preprocessar_features(df: pd.DataFrame, colunas_numericas: List[str], colunas_categoricas: List[str]) -> pd.DataFrame:
    """
    Aplica one-hot encoding e standard scaling nas colunas especificadas.
    Retorna um DataFrame processado e pronto para o cálculo de score.
    """
    df_categoricas_encoded = pd.get_dummies(df[colunas_categoricas])
    scaler = StandardScaler()
    df_numericas_scaled = pd.DataFrame(scaler.fit_transform(df[colunas_numericas]), columns=colunas_numericas, index=df.index)
    return pd.concat([df_numericas_scaled, df_categoricas_encoded], axis=1)

def _calcular_score_bruto(df_processado: pd.DataFrame, pesos_numericos: Dict[str, float], pesos_categoricos: Dict[str, float]) -> pd.Series:
    """
    Calcula o score bruto ponderando as features processadas.
    O score é uma métrica de ranking antes da normalização sigmoidal.
    """
    score = pd.Series(0, index=df_processado.index, dtype=float)
    todos_pesos = {**pesos_numericos, **pesos_categoricos}
    for feature, peso in todos_pesos.items():
        if feature in df_processado.columns:
            score += df_processado[feature] * peso
    return score

def _converter_score_para_probabilidade(score_bruto: pd.Series) -> np.ndarray:
    """
    Converte o score de ranking em uma probabilidade (0 a 1) usando a função sigmoide.
    Isso torna o resultado mais interpretável como uma 'chance de recuperação'.
    """
    scaler = StandardScaler()
    scores_padronizados = scaler.fit_transform(score_bruto.values.reshape(-1, 1))
    return 1 / (1 + np.exp(-scores_padronizados))


# --- Função Principal de Orquestração ---

def gerar_score_recuperacao(df_prospects: pd.DataFrame, caminho_pesos: str = "Control/Score_Manual/pesos.json") -> pd.DataFrame:
    """
    Orquestra o processo completo de scoring a partir de um DataFrame.

    1. Utiliza o DataFrame de prospects fornecido.
    2. Carrega a configuração de pesos.
    3. Pré-processa as features (numéricas e categóricas).
    4. Calcula o score bruto ponderado.
    5. Converte o score em uma probabilidade de recuperação.
    6. Retorna o DataFrame original com as colunas de score, ordenado pela probabilidade.
    """
    # A leitura do CSV foi removida. A função agora recebe o DataFrame diretamente.
    configuracao = _carregar_configuracao_pesos(caminho_pesos)
    
    pesos_numericos = configuracao.get('pesos_numericos', {})
    pesos_categoricos = configuracao.get('pesos_categoricos', {})
    
    # Identificação Dinâmica de Colunas
    # Garante que a coluna 'id_cliente' exista antes de tentar removê-la.
    colunas_a_remover = ['id_cliente']
    df_features = df_prospects.drop(columns=[col for col in colunas_a_remover if col in df_prospects.columns])
    
    colunas_numericas = df_features.select_dtypes(include=np.number).columns.tolist()
    colunas_categoricas = df_features.select_dtypes(include=['object', 'category']).columns.tolist()

    # Execução do Pipeline de Scoring
    df_processado = _preprocessar_features(df_features, colunas_numericas, colunas_categoricas)
    score_bruto = _calcular_score_bruto(df_processado, pesos_numericos, pesos_categoricos)
    probabilidade = _converter_score_para_probabilidade(score_bruto)

    # Consolidação do Resultado
    df_resultado = df_prospects.copy()
    df_resultado['score_ranking_bruto'] = score_bruto
    df_resultado['score_recuperacao'] = probabilidade
    
    return df_resultado.sort_values(by='score_recuperacao', ascending=False)

# # --- Exemplo de Uso ---
# if __name__ == '__main__':
#     # Simula a criação de um DataFrame, como seria feito no app.py
#     dados_exemplo = {
#         'id_cliente': [1, 2, 3, 4],
#         'valor_divida_mil': [10, 5, 20, 2],
#         'tempo_inadimplencia_dias': [365, 180, 730, 90],
#         'origem_divida': ['BANCO', 'TELECOM', 'VAREJO', 'BANCO'],
#         'possui_outras_dividas': ['SIM', 'NAO', 'SIM', 'NAO']
#     }
#     df_para_score = pd.DataFrame(dados_exemplo)

#     # O arquivo de pesos ainda é carregado do disco, o que é o comportamento esperado.
#     # (O código para criar o arquivo de pesos pode ser omitido se ele já existir)

#     # Executa a função principal passando o DataFrame
#     df_final_score = gerar_score_recuperacao(df_prospects=df_para_score)
    
#     print("--- DataFrame Final com Score de Recuperação ---")
#     print(df_final_score)