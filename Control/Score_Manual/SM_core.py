# Control/Score_Manual/SM_core.py

import json
from typing import Dict, Any

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# --- Funções Auxiliares (Lógica Interna) ---

def _carregar_configuracao_pesos(caminho_pesos: str) -> Dict[str, Any]:
    """Carrega o arquivo JSON completo com as configurações de PF e PJ."""
    with open(caminho_pesos, 'r', encoding='utf-8') as f:
        return json.load(f)

def _calcular_score_segmento(df_segmento: pd.DataFrame, config_pesos_segmento: Dict[str, Any]) -> pd.DataFrame:
    """
    Função core que calcula o score para um segmento específico (PF ou PJ),
    agora com logging detalhado para monitoramento do processo.
    """
    if df_segmento.empty:
        print("   [LOG] Segmento vazio, pulando processamento.")
        return pd.DataFrame()

    pesos_numericos = config_pesos_segmento.get('pesos_numericos', {})
    pesos_categoricos = config_pesos_segmento.get('pesos_categoricos', {})
    
    # --- LOG: Identificação de Features ---
    colunas_numericas_relevantes = list(pesos_numericos.keys())
    colunas_categoricas_relevantes = list(set([k.rsplit('_', 1)[0] for k in pesos_categoricos.keys()]))
    colunas_numericas_presentes = [col for col in colunas_numericas_relevantes if col in df_segmento.columns]
    colunas_categoricas_presentes = [col for col in colunas_categoricas_relevantes if col in df_segmento.columns]
    
    print(f"   [LOG] Features Numéricas Identificadas: {colunas_numericas_presentes}")
    print(f"   [LOG] Features Categóricas Identificadas: {colunas_categoricas_presentes}")
    
    df_features = df_segmento[colunas_numericas_presentes + colunas_categoricas_presentes].copy()

    # --- Pré-processamento Robusto ---
    if colunas_numericas_presentes:
        imputer = SimpleImputer(strategy='mean')
        df_features.loc[:, colunas_numericas_presentes] = imputer.fit_transform(df_features[colunas_numericas_presentes])
        print("   [LOG] Imputação de dados numéricos ausentes concluída.")

    df_categoricas_encoded = pd.get_dummies(df_features[colunas_categoricas_presentes])
    
    df_numericas_scaled = pd.DataFrame(index=df_features.index)
    if colunas_numericas_presentes:
        numeric_data = df_features[colunas_numericas_presentes]
        colunas_com_variancia = numeric_data.columns[numeric_data.var() > 0]
        
        if not colunas_com_variancia.empty:
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data[colunas_com_variancia])
            df_numericas_scaled = pd.DataFrame(scaled_data, columns=colunas_com_variancia, index=df_features.index)
            print("   [LOG] Padronização (scaling) das features numéricas concluída.")
        else:
            print("   [LOG] Nenhuma feature numérica com variância para padronizar.")

    df_processado = pd.concat([df_numericas_scaled, df_categoricas_encoded], axis=1)
    print(f"   [LOG] DataFrame final para scoring criado com {df_processado.shape[0]} linhas e {df_processado.shape[1]} colunas.")

    # --- Cálculo do Score ---
    score_bruto = pd.Series(0, index=df_processado.index, dtype=float)
    todos_pesos = {**pesos_numericos, **pesos_categoricos}
    for feature, peso in todos_pesos.items():
        if feature in df_processado.columns:
            score_bruto += df_processado[feature] * peso
    
    print(f"   [LOG] Score bruto calculado. Resumo: Mín={score_bruto.min():.2f}, Média={score_bruto.mean():.2f}, Máx={score_bruto.max():.2f}")
            
    if score_bruto.var() == 0:
        probabilidade = np.full(shape=len(score_bruto), fill_value=0.5)
        print("   [LOG] Variância do score é zero. Probabilidade definida como 0.5 para todos.")
    else:
        scaler_score = StandardScaler()
        scores_padronizados = scaler_score.fit_transform(score_bruto.values.reshape(-1, 1))
        probabilidade = 1 / (1 + np.exp(-scores_padronizados))
        print("   [LOG] Score convertido para probabilidade via função sigmoide.")

    df_resultado_segmento = df_segmento.copy()
    df_resultado_segmento['score_ranking_bruto'] = score_bruto
    df_resultado_segmento['score_recuperacao'] = probabilidade
    
    return df_resultado_segmento

# --- Função Principal de Orquestração (Inalterada) ---
def gerar_score_recuperacao(df_prospects: pd.DataFrame, caminho_pesos: str = "Control/Score_Manual/pesos.json") -> pd.DataFrame:
    """
    Orquestra o processo de scoring, segmentando os prospects em PF e PJ.
    """
    configuracao_completa = _carregar_configuracao_pesos(caminho_pesos)
    df_trabalho = df_prospects.copy()

    df_trabalho['tipo_pessoa'] = df_trabalho['documento'].str.replace(r'\D', '', regex=True).str.len().map({11: 'pf', 14: 'pj'})

    df_pf = df_trabalho[df_trabalho['tipo_pessoa'] == 'pf'].copy()
    df_pj = df_trabalho[df_trabalho['tipo_pessoa'] == 'pj'].copy()

    print(f"Processando {len(df_pf)} CPFs com o modelo PF...")
    resultado_pf = _calcular_score_segmento(df_pf, configuracao_completa.get('pf', {}))
    
    print(f"Processando {len(df_pj)} CNPJs com o modelo PJ...")
    resultado_pj = _calcular_score_segmento(df_pj, configuracao_completa.get('pj', {}))

    df_final = pd.concat([resultado_pf, resultado_pj], ignore_index=True)
    
    df_final.to_csv("DF_FINAL.csv")
    
    return df_final.sort_values(by='score_recuperacao', ascending=False)