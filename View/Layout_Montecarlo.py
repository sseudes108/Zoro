import streamlit as st
import locale

# --- Funções de Formatação e Componentes Customizados ---

def _formatar_valor(valor: float) -> str:
    """Formata um valor numérico como moeda brasileira."""
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    return locale.currency(valor, grouping=True)

def _gerar_metrica_html(label: str, value: str, icon: str) -> str:
    """
    Gera o código HTML para um card de métrica com altura fixa para garantir alinhamento.
    """
    return f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# --- Funções de Renderização de Relatórios ---

def relatorio_sumario(df_final, analise_montecarlo):
    """Renderiza o sumário da carteira e os cenários da simulação com colunas de altura igual."""
    
    # CSS para definir a aparência e, mais importante, a altura mínima dos nossos cards de métrica.
    st.markdown("""
    <style>
    .metric-card {
        background-color: #0E1117;
        border: 1px solid #262730;
        border-radius: 0.5rem;
        padding: 1rem;
        min-height: 130px; /* ALTURA FIXA: O ponto chave da solução */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #808495;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 600;
        color: #FAFAFA;
    }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("📊 Sumário da Carteira")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(_gerar_metrica_html(
            label="Dívida Total Sob Análise",
            value=_formatar_valor(sum(df_final['valor_divida_mil']) * 1000),
            icon="💵"
        ), unsafe_allow_html=True)
        
        st.markdown(_gerar_metrica_html(
            label="Total de Prospects",
            value=f"{len(df_final)}",
            icon="👥"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(_gerar_metrica_html(
            label="Média de Recuperação",
            value=_formatar_valor(analise_montecarlo.get("media_recuperacao", 0)),
            icon="📈"
        ), unsafe_allow_html=True)
        
        st.markdown(_gerar_metrica_html(
            label="Risco (Desvio Padrão)",
            value=_formatar_valor(analise_montecarlo.get("desvio_padrao", 0)),
            icon="🎲"
        ), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔮 Cenários da Simulação")
    
    # Para esta seção, o st.metric original funciona bem pois os labels têm tamanho similar.
    col_pess, col_otim = st.columns(2)
    with col_pess:
        st.metric(
            label="📉 Cenário Pessimista (5%)",
            value=_formatar_valor(analise_montecarlo.get("percentil_5", 0))
        )
    with col_otim:
        st.metric(
            label="🚀 Cenário Otimista (95%)",
            value=_formatar_valor(analise_montecarlo.get("percentil_95", 0))
        )

def relatorio_preco(ve, analise_preco_montecarlo, retorno):
    """
    Renderiza a análise de precificação da carteira, destacando o lucro líquido em R$
    e usando o ROI percentual como indicador secundário.
    """
    st.subheader("💰 Precificação da Carteira")
    
    # --- Lógica de Cálculo ---
    # Extrai os valores necessários do dicionário para os cálculos.
    recuperacao_liquida = analise_preco_montecarlo.get("RLE", 0)
    preco_maximo = analise_preco_montecarlo.get("PMV", 0)
    roi_percentual = analise_preco_montecarlo.get("ROI", 0)
    
    # Calcula o lucro líquido, que é a métrica principal em valor monetário.
    lucro_liquido_esperado = recuperacao_liquida - preco_maximo
    
    # --- Renderização da Métrica ---
    # A métrica principal agora exibe o Lucro em R$.
    # O campo 'delta' é utilizado para mostrar o ROI percentual, fornecendo contexto.
    st.metric(
        label="🎯 Lucro Líquido Esperado (R$)",
        value=_formatar_valor(lucro_liquido_esperado),
        delta=f"ROI: {retorno/100:.2%}",
        delta_color="normal" if lucro_liquido_esperado >= 0 else "inverse"
    )
    
    # O markdown detalha os componentes do cálculo.
    st.markdown(
        f"""
        - **Valor Esperado (Cenário):** `{_formatar_valor(ve)}`
        - **Custo da Operação:** `{_formatar_valor(analise_preco_montecarlo.get("COP", 0))}` <span style="color: #FF4B4B;">(Saída)</span>
        - **Recuperação Líquida:** `{_formatar_valor(recuperacao_liquida)}` <span style="color: #3D9970;">(Entrada)</span>
        - **Preço Máximo Viável:** `{_formatar_valor(preco_maximo)}`
        """,
        unsafe_allow_html=True
    )