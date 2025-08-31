import pandas as pd
import streamlit as st

# --- Importação dos Módulos de Lógica do Projeto ---
import Control.MonteCarlo.montecarlo    as MonteCarlo
import Control.XGboost.model_run        as XGRun
import Control.XGboost.model_training   as XGTraining
import Control.PCA.pca                  as PCA
import Control.Score_Manual.SM_core     as SM

# --- Funções Expostas para a Camada de Visualização (app.py) ---

# O decorador @st.cache_data agora operará sobre o conteúdo do DataFrame.
# Se o DataFrame de entrada não mudar, o resultado em cache será retornado.

def score_xgboost(df_prospects: pd.DataFrame, caminho_artefatos_modelo: str) -> pd.DataFrame:
    """
    Gera o score de recuperação usando um modelo XGBoost treinado.
    Recebe: um DataFrame de prospects.
    Retorna: um DataFrame com a coluna de score.
    """
    return XGRun.gerar_score_carteira(df_prospects, caminho_artefatos_modelo)

def score_manual(df_prospects: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o score de recuperação usando o modelo de pesos manuais.
    Recebe: um DataFrame de prospects.
    Retorna: um DataFrame com a coluna de score.
    """
    return SM.gerar_score_recuperacao(df_prospects)

def analise_pca(df_prospects: pd.DataFrame) -> pd.DataFrame:
    """
    Executa a Análise de Componentes Principais sobre os dados dos prospects.
    Recebe: um DataFrame de prospects.
    Retorna: um DataFrame com os componentes principais.
    """
    return PCA.analise_pca(df_prospects)

def rodar_simulacao_montecarlo(df_final: pd.DataFrame, n_simulacoes: int = 10000) -> list:
    """
    Executa a simulação de Monte Carlo sobre um DataFrame já com scores.
    Esta função já estava correta, recebendo um DataFrame.
    """
    return MonteCarlo.rodar_simulacao(df_final, n_simulacoes)

# --- Funções de Suporte (Ex: Treinamento, podem ser mantidas como estão se for um processo offline) ---

def treinar_modelo(caminho_base_treinamento: str, numero_de_amostras: int = 54000) -> str:
    """
    Orquestra o treinamento de um novo modelo XGBoost.
    Por ser uma operação distinta e offline, pode continuar recebendo um caminho de arquivo.
    """
    return XGTraining.treinar_modelo(caminho_base_treinamento, numero_de_amostras)