import plotly.graph_objects as go
import plotly.express as px

def get_gauge(value):
    # --- 1. Definição dos Parâmetros ---
    # O valor que o medidor irá mostrar.
    valor_atual = value

    # O valor máximo do medidor.
    valor_maximo = 100

    # Título do gráfico.
    titulo_grafico = "Score Geral"

    # --- 2. Criação da Figura ---
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", # Define o tipo de indicador: medidor com um número.
        value = valor_atual,   # O valor a ser exibido pelo ponteiro.
        title = {'text': titulo_grafico, 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, valor_maximo], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "black"},
            'bgcolor': "white",
            # --- 3. Definição dos Quatro Níveis (Steps) ---
            # Cada dicionário na lista 'steps' é um nível colorido.
            'steps': [
                {'range': [0, 25], 'color': "#ea4335"},    # Nível 1: Vermelho
                {'range': [25, 50], 'color': "#fbbc05"},   # Nível 2: Laranja/Amarelo
                {'range': [50, 75], 'color': "#a5d6a7"},   # Nível 3: Verde Claro
                {'range': [75, 100], 'color': "#34a853"}   # Nível 4: Verde Escuro
            ],
            # Linha que pode marcar um limite importante.
            'threshold': {
                'line': {'color': "black", 'width': 9},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    # --- 4. Customização do Layout (Opcional) ---
    fig.update_layout(
        font = {'color': "lightgray", 'family': "Arial"}
    )
    
    return fig

def get_bar(values):
    # --- 1. Preparação dos Dados ---
    # Defina os rótulos (categorias) para cada uma das quatro barras.
    categorias = ['Rank A', 'Rank B', 'Rank C', 'Rank D']

    # Defina os valores correspondentes para a altura de cada barra.
    # A ordem aqui deve corresponder à ordem das categorias acima.
    valores = values
    
    # --- 2. PREPARAÇÃO DAS CORES ---
    # Crie uma lista de cores. A ordem importa!
    # O número de cores deve ser igual ao número de categorias/valores.
    cores_das_barras = ['#34a853', "#a5d6a7", '#fbbc05', '#ea4335']

    # --- 3. Criação da Figura (aqui está a mágica) ---
    fig = go.Figure(data=[
        go.Bar(
            x=categorias, 
            y=valores, 
            marker_color=cores_das_barras 
        )
    ])

    # --- 3. Customização do Layout (Títulos, etc.) ---
    # É uma boa prática sempre nomear o gráfico e seus eixos.
    fig.update_layout(
        # title_text='Distribuição de Prospects por Status', # Título principal do gráfico
        # xaxis_title='Rank',                # Título do eixo X
        yaxis_title='Valor R$',                         # Título do eixo Y
    )
        
    return fig

def get_hist(resultados, simul_count):
    media = resultados.get("media_recuperacao", 0)
    p5 = resultados.get("percentil_5", 0)
    p95 = resultados.get("percentil_95", 0)
    
    fig = go.Figure()

    # Adicionar o histograma dos resultados
    fig.add_trace(go.Histogram(
        x=resultados.get("resultados"),
        name='Distribuição',
        marker_color='#330C73',
        opacity=0.75
    ))

    # Adicionar uma linha vertical para a Média
    fig.add_vline(
        x=media + 100, 
        line_width=3, 
        line_dash="dash", 
        line_color="firebrick",
        annotation_text=f"Média",
        annotation_position="top right"
    )

    # Adiciona linhas verticais para os cenários
    fig.add_vline(x=media, line_width=2, line_dash="dash", line_color="orange",
                  annotation_text="Média", annotation_position="top right")
    fig.add_vline(x=p5, line_width=2, line_dash="dash", line_color="#FF4B4B", # Vermelho Streamlit
                  annotation_text="Pessimista (5%)", annotation_position="top left")
    fig.add_vline(x=p95, line_width=2, line_dash="dash", line_color="#3D9970", # Verde
                  annotation_text="Otimista (95%)", annotation_position="top right")

    # Layout e design do gráfico
    fig.update_layout(
        title_text='<b>Distribuição do Valor Recuperado</b>',
        xaxis_title_text='Valor Recuperado por Simulação (R$)',
        yaxis_title_text=f'Frequência (x{simul_count})',
        bargap=0.1,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def get_scatter_pca(dataframe_resultado_pca):
    """Cria um gráfico de dispersão dos dois primeiros componentes principais (PCA)."""
    fig = px.scatter(
        dataframe_resultado_pca,
        x='PC_1',
        y='PC_2',
        title='<b>Análise de Componentes Principais (PCA)</b>',
        labels={'PC_1': 'Componente Principal 1', 'PC_2': 'Componente Principal 2'},
        template='plotly_white',
        # Adicionando cor e tamanho para dar mais informação
        color='valor_divida_mil', 
        size='tempo_inadimplencia_dias',
        hover_data=['id_cliente'],
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=0.5, color='DarkSlateGrey')))
    return fig