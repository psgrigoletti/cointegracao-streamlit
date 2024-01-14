import datetime

# import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

# import seaborn as sn
import statsmodels.api as sm
import streamlit as st
import yfinance as yf


@st.cache_data
def buscar_dados(ticker1, ticker2, data_inicial, data_final):
    dados = pd.DataFrame()
    for t in [ticker1, ticker2]:
        dados[t] = yf.download(t, start=data_inicial, end=data_final, progress=False)[
            "Adj Close"
        ]
        if len(dados[t]) == 0:
            frase = f"Erro ao buscar os dados de {t}. Verifique os parâmetros usados."
            st.error(frase, icon="🚨")
            st.stop()
    dados.dropna(inplace=True)
    return dados


pd.options.plotting.backend = "plotly"

st.title("Correlação")

col1, col2, col3, col4 = st.columns(4)
with col1:
    ticker1 = st.text_input("Ticker 1", "PETR3.SA")

with col2:
    ticker2 = st.text_input("Ticker 2", "PETR4.SA")

with col3:
    data_inicial = st.date_input("Data inicial", datetime.date(2022, 1, 1))
with col4:
    data_final = st.date_input("Data final", datetime.date(2024, 1, 13))
analisar = st.button("Analisar")

if analisar:
    dados = buscar_dados(ticker1, ticker2, data_inicial, data_final)

    tab0, tab1, tab2, tab3, tab4 = st.tabs(
        ["Dados", "Preço", "Retorno normalizado", "Dispersão", "Statsmodels"]
    )
    with tab0:
        st.write(dados)

    with tab1:
        # st.write(dados)
        preco1_ticker1 = dados[ticker1].iloc[0]
        preco2_ticker1 = dados[ticker1].iloc[-1]
        variacao_preco_ticker1 = preco2_ticker1 - preco1_ticker1
        variacao_percentual_ticker1 = variacao_preco_ticker1 / preco1_ticker1 * 100.0

        preco1_ticker2 = dados[ticker2].iloc[0]
        preco2_ticker2 = dados[ticker2].iloc[-1]
        variacao_preco_ticker2 = preco2_ticker2 - preco1_ticker2
        variacao_percentual_ticker2 = variacao_preco_ticker2 / preco1_ticker2 * 100.0

        tab1_col1, tab1_col2 = st.columns(2)
        with tab1_col1:
            st.metric(
                label=f"Preço inicial {ticker1}",
                value="R$ " + str(round(preco1_ticker1, 2)),
            )
            st.metric(
                label=f"Preço final {ticker1}",
                value="R$ " + str(round(preco2_ticker1, 2)),
            )
            st.metric(
                label=f"Variação {ticker1}",
                value="R$ " + str(round(variacao_preco_ticker1, 2)),
                delta=f"{round(variacao_percentual_ticker1, 2)} %",
            )

        with tab1_col2:
            st.metric(
                label=f"Preço inicial {ticker2}",
                value="R$ " + str(round(preco1_ticker2, 2)),
            )
            st.metric(
                label=f"Preço final {ticker2}",
                value="R$ " + str(round(preco2_ticker2, 2)),
            )
            st.metric(
                label=f"Variação {ticker2}",
                value="R$ " + str(round(variacao_preco_ticker2, 2)),
                delta=f"{round(variacao_percentual_ticker2, 2)} %",
            )

        fig1 = dados.plot()
        fig1.update_layout(
            title=f"Gráfico de Preços: {ticker1} vs {ticker2}",
            xaxis_title="Data",
            yaxis_title="Preço (R$)",
        )
        fig1.update_layout(
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor="LightGray"),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor="LightGray"),
        )
        fig1.update_layout(legend_title_text="Tickers")
        st.plotly_chart(fig1)

    with tab2:
        retorno_acumulado = (dados / dados.iloc[0] - 1) * 100.0
        fig2 = retorno_acumulado.plot()
        fig2.update_layout(
            title=f"Gráfico de retorno normalizado: {ticker1} vs {ticker2}",
            xaxis_title="Data",
            yaxis_title="Retorno (%)",
        )
        fig2.update_layout(legend_title_text="Tickers")
        fig2.update_layout(
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor="LightGray"),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor="LightGray"),
        )
        # st.write(retorno_acumulado)

        st.plotly_chart(fig2)

    # correlacao = dados.corr()
    # fig2 = sn.heatmap(correlacao, annot=True, fmt=".1f", linewidths=0.6).get_figure()
    # st.write(fig2)

    with tab3:
        fig = px.scatter(
            x=dados[ticker1],
            y=dados[ticker2],
            labels={"x": f"Cotação {ticker1}", "y": f"Cotação {ticker2}"},
        )
        fig.update_layout(
            title=f"Gráfico de Dispersão: {ticker1} vs {ticker2}",
            xaxis_title=f"Cotação {ticker1}",
            yaxis_title=f"Cotação {ticker2}",
        )

        fig.update_layout(
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor="LightGray"),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor="LightGray"),
        )
        st.plotly_chart(fig)
    with tab4:
        X = sm.add_constant(dados[ticker1])
        modelo = sm.OLS(dados[ticker2], X)
        resultados = modelo.fit()
        st.write(resultados.summary())
