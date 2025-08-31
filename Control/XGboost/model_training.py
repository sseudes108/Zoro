import pandas as pd
import numpy as np
import xgboost as xgb
import joblib # Usaremos joblib para salvar e carregar o modelo
import datetime

def gerar_dados_ficticios():
    # --- ETAPA 1: SIMULAR O CENÁRIO PASSADO (TREINAMENTO DO MODELO) ---
    # Esta parte gera a base histórica e treina o modelo, como fizemos antes.

    print("--- ETAPA 1: Treinando o modelo com dados históricos ---")

    # Gerar a base de dados histórica fictícia
    num_amostras_treino = 10000
    dados_treino = {
        'id_cliente': range(1, num_amostras_treino + 1),
        'valor_divida_mil': np.random.lognormal(mean=3.5, sigma=1.5, size=num_amostras_treino).round(2),
        'tempo_inadimplencia_dias': np.random.randint(30, 1800, size=num_amostras_treino),
        'porte_cliente': np.random.choice(['Pequeno', 'Médio', 'Grande'], size=num_amostras_treino, p=[0.5, 0.4, 0.1]),
        'ramo_atuacao_cliente': np.random.choice(['Produtor', 'Cooperativa', 'Distribuidor', 'Indústria'], size=num_amostras_treino, p=[0.4, 0.3, 0.2, 0.1]),
        'score_risco_interno': np.random.choice(['A', 'B', 'C', 'D', 'F'], size=num_amostras_treino, p=[0.1, 0.2, 0.4, 0.2, 0.1]),
        'regiao': np.random.choice(['Sul', 'Sudeste', 'Centro-Oeste', 'Nordeste', 'Norte'], size=num_amostras_treino, p=[0.3, 0.3, 0.2, 0.1, 0.1])
    }
    
    return dados_treino, num_amostras_treino

def processamento_treino(dados_treinamento, num_amostras_treino):
    df_treino = pd.DataFrame(dados_treinamento)
    prob_base = 0.5 - df_treino['valor_divida_mil'] * 0.001 - df_treino['tempo_inadimplencia_dias'] * 0.0002
    porte_map = {'Pequeno': -0.1, 'Médio': 0.05, 'Grande': 0.2}
    score_map = {'A': 0.3, 'B': 0.15, 'C': 0.0, 'D': -0.2, 'F': -0.4}
    prob_base += df_treino['porte_cliente'].map(porte_map) + df_treino['score_risco_interno'].map(score_map)
    prob_final_sigmoid = 1 / (1 + np.exp(-(prob_base + np.random.normal(0, 0.1, size=num_amostras_treino))))
    df_treino['status_final_pago'] = (prob_final_sigmoid > np.random.rand(num_amostras_treino)).astype(int)

    # Pré-processamento e Treinamento
    df_treino_encoded = pd.get_dummies(df_treino, columns=['porte_cliente', 'ramo_atuacao_cliente', 'score_risco_interno', 'regiao'])
    X_train = df_treino_encoded.drop(['id_cliente', 'status_final_pago'], axis=1)
    y_train = df_treino_encoded['status_final_pago']
    model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='auc', use_label_encoder=False)
    model.fit(X_train, y_train)
    
    return model, X_train
    
def salvar_modelo_treinado(model, X_train):
    artefatos_modelo = {
        'model': model,
        'columns': X_train.columns.tolist() # Salvamos a lista de nomes das colunas
    }
    
    # Pega a data de hoje
    data_hoje = datetime.date.today()
    # Formata a data no formato YYMMDD
    data_formatada = data_hoje.strftime("%y%m%d%H%M")

    # Salvar o dicionário (os "artefatos") em um único arquivo
    caminho_modelo = f'modelo_score_recuperacao_with_columns_v1_{data_formatada}.pkl'
    joblib.dump(artefatos_modelo, caminho_modelo) # Agora salvamos o dicionário

    # print(f"Artefatos do modelo (modelo + colunas) salvos em '{caminho_modelo}'")
    
def treinar_modelo(dados_treinamento, num_amostras_treino):
    model, X_train = processamento_treino(dados_treinamento, num_amostras_treino)
    salvar_modelo_treinado(model, X_train)