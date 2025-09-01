import streamlit as st
import pandas as pd
import locale
from typing import Optional, Union

# --- Módulos do Projeto Zoro ---
import View.Graficos as Graficos
import View.Layout_Score as LayoutScore
import View.Layout_Montecarlo as LayoutMonteCarlo
import Control.Zoro as Zoro
import Control.Score_Manual.SM_analise as SMHelper

# --- Constantes de Configuração ---
THREE_COLS_SIZE = [1.5, 1.5, 1.5]

# --- Funções de Carregamento e Processamento com Cache ---
# Otimização Crítica: O cache impede que os dados sejam recarregados e os scores 
# reprocessados a cada interação do usuário (ex: ao mudar o número de simulações).

@st.cache_data
def carregar_dados(uploaded_file: Optional[object]) -> pd.DataFrame:
    """Carrega os dados a partir de um arquivo enviado ou de um caminho padrão."""
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return pd.read_csv('base_full.csv')

@st.cache_data
def processar_score_manual(_df: pd.DataFrame) -> pd.DataFrame:
    """Executa e cacheia os resultados do Score Manual."""
    return Zoro.score_manual(_df.copy())

@st.cache_data
def processar_score_xgboost(_df: pd.DataFrame, model_path: str) -> pd.DataFrame:
    """Executa e cacheia os resultados do Score XGBoost."""
    return Zoro.score_xgboost(_df.copy(), model_path)

@st.cache_data
def processar_analise_pca(_df: pd.DataFrame) -> pd.DataFrame:
    """Executa e cacheia os resultados da Análise de Componentes Principais."""
    return Zoro.analise_pca(_df.copy())

# --- Funções de Renderização de Componentes da UI ---
# Abstração: Estas funções evitam a duplicação de código no layout.

def renderizar_aba_score(df_scored: pd.DataFrame):
    print(df_scored.columns)
    # Cria as abas aninhadas
    tab_geral, tab_pf, tab_pj = st.tabs(["📊 Geral", "👤 Pessoa Física (PF)", "🏢 Pessoa Jurídica (PJ)"])

    # --- Aba Geral (Visão Consolidada) ---
    with tab_geral:
        st.subheader("Visão Consolidada da Carteira")
        if df_scored.empty:
            st.warning("Nenhum dado disponível para exibir.")
        else:
            LayoutScore.relatorio_score(df_scored)
            st.divider()
            st.dataframe(df_scored)

    # --- Aba Pessoa Física (Visão Filtrada) ---
    with tab_pf:
        st.subheader("Análise Detalhada: Pessoa Física")
        # Filtra o DataFrame para conter apenas registros PF
        df_pf = df_scored[df_scored['tipo_pessoa'] == 'pf'].copy()
        
        if df_pf.empty:
            st.info("Nenhum prospect do tipo Pessoa Física encontrado nesta carteira.")
        else:
            LayoutScore.relatorio_score(df_pf)
            st.divider()
            st.dataframe(df_pf)
    
    # --- Aba Pessoa Jurídica (Visão Filtrada) ---
    with tab_pj:
        st.subheader("Análise Detalhada: Pessoa Jurídica")
        # Filtra o DataFrame para conter apenas registros PJ
        df_pj = df_scored[df_scored['tipo_pessoa'] == 'pj'].copy()
        
        if df_pj.empty:
            st.info("Nenhum prospect do tipo Pessoa Jurídica encontrado nesta carteira.")
        else:
            LayoutScore.relatorio_score(df_pj)
            st.divider()
            st.dataframe(df_pj)

def renderizar_aba_simulacao(df_scored: pd.DataFrame, simul_count: int, model_name: str, key_prefix: str):
    """Renderiza um bloco completo de simulação Monte Carlo para um dado score."""
    st.subheader(f"Análise de Cenários com {model_name}")
    
    # --- Inputs do Usuário ---
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        cenario = st.selectbox("Cenário", ["Pessimista", "Média", "Otimista"], key=f"{key_prefix}_cenario", index=0)
    with col2:
        custo_op = st.number_input("Custo de Operação %", 1.0, 100.0, 25.0, step=0.01, key=f"{key_prefix}_cop")
    with col3:
        retorno = st.number_input("Retorno Desejado %", 1.0, 1000.0, 50.0, step=0.01, key=f"{key_prefix}_roi")

    # --- Lógica de Simulação ---
    resultados_mc = Zoro.rodar_simulacao_montecarlo(df_scored, simul_count)
    analise_mc = SMHelper.calcular_estatisticas_simulacao(resultados_mc, simul_count)
    
    mapa_cenarios = {
        "Pessimista": analise_mc.get("percentil_5", 0),
        "Otimista": analise_mc.get("percentil_95", 0),
        "Média": analise_mc.get("media_recuperacao", 0)
    }
    valor_esperado = mapa_cenarios[cenario]
    analise_preco = SMHelper.estimar_valor_carteira(valor_esperado, custo_op, retorno)

    # --- Exibição dos Resultados ---
    g_col, m_col, p_col = st.columns(THREE_COLS_SIZE)
    with g_col:
        st.plotly_chart(Graficos.get_hist(analise_mc, simul_count), use_container_width=True)
    with m_col:
        LayoutMonteCarlo.relatorio_sumario(df_scored, analise_mc)
    with p_col:
        LayoutMonteCarlo.relatorio_preco(valor_esperado, analise_preco, retorno)

# --- Função Principal da Aplicação ---

def draw_page():
    """Renderiza a página principal da aplicação Zoro."""
    st.set_page_config(page_title='Zoro', layout='wide')
    
    # Configuração de localidade para formatação de moeda
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        
    st.title("🏴‍☠️ Zoro")
    st.caption("Caçador de Recompensas - 2025")
    
    # --- Inputs Globais ---
    with st.container():
        _, model_xb_col, simulations_col, upload_file_col = st.columns([0.5, 0.3, 0.3, 1])
        with model_xb_col:
            model_xb_input = st.selectbox("Modelo XGBoost", ["V1"])
        with simulations_col:
            simulations_count_input = st.number_input("Nº de Simulações", 108, 108000, 10800, 1)
        with upload_file_col:
            uploaded_file = st.file_uploader("Upload Base Prospects", type="csv")

    # --- Lógica Principal e Renderização das Abas (ARQUITETURA AJUSTADA) ---
    df_prospects = carregar_dados(uploaded_file)

    if df_prospects is None or df_prospects.empty:
        st.header("⚔️ Aguardando Base de Prospects")
        return

    # --- PONTO CENTRAL DA CORREÇÃO ---
    # 1. Enriquecer o DataFrame principal com a coluna 'tipo_pessoa' AQUI.
    # Esta lógica é executada uma única vez e serve de base para todos os modelos.
    if 'documento' in df_prospects.columns:
        df_prospects['tipo_pessoa'] = df_prospects['documento'].str.replace(r'\D', '', regex=True).str.len().map({11: 'pf', 14: 'pj'})
    else:
        # Fallback caso a coluna 'documento' não exista
        df_prospects['tipo_pessoa'] = 'indefinido'

    # 2. Processar todos os dataframes. Agora, ambos os fluxos herdarão a coluna 'tipo_pessoa'.
    df_final_sm = processar_score_manual(df_prospects)
    
    model_path = "modelo_score_recuperacao_with_columns_v1.pkl"
    df_final_xb = processar_score_xgboost(df_prospects, model_path)
    
    df_pca = processar_analise_pca(df_prospects)

    # 3. Criar e renderizar as abas da interface (código inalterado)
    score_manual_tab, score_xb_tab, pca_tab, simulation_tab = st.tabs(["🧠 Score Manual", "🐉 XGBoost", "🧪 PCA", "🎲 Monte Carlo"])

    with score_manual_tab:
        renderizar_aba_score(df_final_sm)

    with score_xb_tab:
        renderizar_aba_score(df_final_xb) # Agora esta chamada funcionará.
        
    with pca_tab:
        scatter_graf_col, _ = st.columns([1.7, 0.5])
        with scatter_graf_col:
            st.plotly_chart(Graficos.get_scatter_pca(df_pca))
        st.dataframe(df_pca)

    with simulation_tab:
        renderizar_aba_simulacao(df_final_sm, simulations_count_input, "Score Manual", "sm")
        st.divider()
        renderizar_aba_simulacao(df_final_xb, simulations_count_input, "XGBoost", "xgb")

def main():
    draw_page()

if __name__ == '__main__':
    main()