import numpy as np

def calcular_estatisticas_simulacao(resultados, simulations_count_input):
    # Análise estatística dos resultados
    media_recuperacao = np.mean(resultados)
    desvio_padrao = np.std(resultados)
    percentil_5 = np.percentile(resultados, 5)  # Cenário pessimista (95% de chance de ser maior que isso)
    percentil_95 = np.percentile(resultados, 95) # Cenário otimista (5% de chance de ser maior que isso)
    dv_1 = media_recuperacao - desvio_padrao
    dv_11 = media_recuperacao + desvio_padrao
    dv_2 = media_recuperacao - (desvio_padrao * 2)
    dv_22 = media_recuperacao + (desvio_padrao * 2)
    
    results = {
        "simulacoes": simulations_count_input,
        "resultados": resultados,
        "media_recuperacao": media_recuperacao,
        "desvio_padrao": desvio_padrao,
        "percentil_5": percentil_5,
        "percentil_95": percentil_95,
        "1_DV": dv_1,
        "11_DV": dv_11,
        "2_DV": dv_2,
        "22_DV": dv_22
    }
    
    return results

def estimar_valor_carteira(ve, cop_percent, retorno_percent):
    cop = ve * (cop_percent/100)
    rle = ve - cop
    pmv = rle / (1 + retorno_percent/100)
    roi = rle - pmv
    
    results = {
        "COP": cop,
        "RLE": rle,
        "PMV": pmv,
        "ROI": roi
    }
    
    return results


#O Preço da Carteira é Presumido? Não, ele é o Resultado da Sua Análise!

# Este é o ponto mais importante: você não "presume" o preço da carteira para fazer a análise. O objetivo de todo o seu trabalho (XGBoost + Monte Carlo + Análise de COP) é justamente calcular o Preço Máximo Viável (PMV) que o banco deveria pagar.

# O fluxo de trabalho não é:
# Se o Preço for X, qual o lucro?

# O fluxo correto é:
# Para ter o lucro que queremos (TMA), qual deve ser o Preço Máximo (PMV) que podemos pagar?

# Como Calcular o Preço Máximo Viável (PMV) na Prática

# Vamos usar os números do nosso exemplo anterior:

#     Valor Esperado (VE) da Carteira: R$ 18.000.000 (calculado pelo seu modelo)

#     Custo da Operação (COP) Estimado: Vamos usar o cenário de 25% do VE.

#         COP = 25% * R$ 18.000.000 = R$ 4.500.000

#     Recuperação Líquida Esperada (RLE): É o que sobra depois de pagar a operação.

#         RLE = VE - COP = R$ 18.000.000 - R$ 4.500.000 = R$ 13.500.000

#     Este valor de R$ 13,5 milhões é o total de dinheiro que se espera que sobre para (1) pagar pela carteira e (2) gerar o lucro do banco.

#     Calcular o Preço Máximo (PMV): Agora, o banco precisa decidir qual o retorno que ele quer sobre o capital que vai investir (o preço da carteira). Vamos supor que o banco queira um retorno de 50% sobre o valor investido (uma TMA bem agressiva).

#         A fórmula é: RLE = PMV + (PMV * Retorno Desejado)

#         RLE = PMV * (1 + Retorno Desejado)

#         PMV = RLE / (1 + Retorno Desejado)

#         PMV = R$ 13.500.000 / (1 + 0.50)

#         PMV = R$ 13.500.000 / 1.5

#         PMV = R$ 9.000.000

# A Conclusão para o Banco:

# Sua apresentação final não é uma presunção, é uma recomendação estratégica e defensável:

# "Baseado em nossa projeção de recuperação de R$ 18 milhões e uma estimativa de custo operacional de 25%, a recuperação líquida esperada é de R$ 13,5 milhões. Para que o banco atinja um retorno de 50% sobre o capital investido, nossa recomendação é que a oferta de compra por esta carteira não exceda R$ 9 milhões. Este é o preço máximo que mantém a viabilidade econômica e o retorno desejado para este projeto."

# É o seu modelo que define o preço, e não o contrário.