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

def get_hist(resultados):
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
        x=resultados.get("media_recuperacao") + 100, 
        line_width=3, 
        line_dash="dash", 
        line_color="firebrick",
        annotation_text=f"Média",
        annotation_position="top right"
    )

    # Adicionar linhas para os percentis
    fig.add_vline(x=resultados.get("percentil_5"), line_width=2, line_dash="dot", line_color="orange", annotation_text="P5")
    fig.add_vline(x=resultados.get("percentil_95"), line_width=2, line_dash="dot", line_color="limegreen", annotation_text="P95")
    # fig.add_vline(x=resultados.get("1_DV"), line_width=2, line_dash="dot", line_color="white", annotation_text="1 DV")
    # fig.add_vline(x=resultados.get("11_DV"), line_width=2, line_dash="dot", line_color="white", annotation_text="11 DV")
    # fig.add_vline(x=resultados.get("2_DV"), line_width=2, line_dash="dot", line_color="blue", annotation_text="2 DV")
    # fig.add_vline(x=resultados.get("22_DV"), line_width=2, line_dash="dot", line_color="blue", annotation_text="22 DV")

    # Customizar o layout
    fig.update_layout(
        # title_text='Distribuição de Resultados da Simulação de Monte Carlo',
        xaxis_title='Valor Total Recuperado (R$)',
        yaxis_title=f'Frequência (x{resultados.get("simulacoes")})',
        bargap=0.1
    )
    
    return fig

def get_scatter_pca(dataframe):
    # Criar um gráfico de dispersão interativo
    fig = px.scatter(
        dataframe,
        x='PC_1',
        y='PC_2',
        color='score_risco_interno', # Colorir os pontos pelo score de risco
        hover_data=['id_cliente', 'valor_divida_mil'],
        title='Visualização de Clientes com os 2 Primeiros Componentes Principais'
    )
        
    return fig