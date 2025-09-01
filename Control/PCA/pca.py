import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer # <-- IMPORTAÇÃO ESTRATÉGICA

# --- Funções Auxiliares (Lógica Interna) ---

def _preprocessar_para_pca(df_features: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara o DataFrame para a análise de PCA, aplicando imputação de dados,
    one-hot encoding e padronização (scaling).
    """
    colunas_numericas = df_features.select_dtypes(include=np.number).columns.tolist()
    colunas_categoricas = df_features.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # --- ETAPA DE CORREÇÃO: IMPUTAÇÃO DE DADOS NUMÉRICOS ---
    # 1. Cria um imputer que substituirá os valores NaN pela média da coluna.
    imputer = SimpleImputer(strategy='mean')
    
    # 2. Aplica a imputação SOMENTE nas colunas numéricas.
    # O resultado é um array NumPy, então o recriamos como um DataFrame
    # preservando os nomes das colunas e o índice.
    df_numericas_imputadas = pd.DataFrame(
        imputer.fit_transform(df_features[colunas_numericas]),
        columns=colunas_numericas,
        index=df_features.index
    )

    # One-Hot Encoding para as colunas categóricas.
    df_categoricas_encoded = pd.get_dummies(df_features[colunas_categoricas])

    # Padronização (Standardization) para as colunas numéricas já imputadas.
    scaler = StandardScaler()
    df_numericas_scaled = pd.DataFrame(
        scaler.fit_transform(df_numericas_imputadas), 
        columns=colunas_numericas, 
        index=df_features.index
    )

    # Concatena as features processadas.
    return pd.concat([df_numericas_scaled, df_categoricas_encoded], axis=1)

# --- Função Principal de Orquestração (Inalterada) ---

def analise_pca(df_prospects: pd.DataFrame) -> pd.DataFrame:
    """
    Executa a Análise de Componentes Principais (PCA) em um DataFrame de prospects.
    """
    # 1. Prepara os dados, removendo o identificador.
    df_features = df_prospects.drop('id_cliente', axis=1, errors='ignore')
    df_processado = _preprocessar_para_pca(df_features)
    
    df_processado.to_csv("DF_PROCESSADO_PCA.csv")

    # 2. Aplica o PCA para extrair os componentes.
    pca = PCA(n_components=2)
    componentes_principais = pca.fit_transform(df_processado)

    # 3. Consolida o resultado.
    df_resultado = df_prospects.copy()
    df_resultado['PC_1'] = componentes_principais[:, 0]
    df_resultado['PC_2'] = componentes_principais[:, 1]
    
    return df_resultado