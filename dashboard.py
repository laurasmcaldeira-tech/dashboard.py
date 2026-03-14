import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Configuração da página
# -------------------------
st.set_page_config(page_title="Wine Sales Dashboard", layout="wide")

st.title("Wine Sales Dashboard")
st.markdown("Garrafeira B2B – Análise de Vendas")

# -------------------------
# Carregar dados
# -------------------------
sales = pd.read_excel("wine_dashboard_fictitious_data_5years.xlsx", sheet_name="sales")
clients = pd.read_excel("wine_dashboard_fictitious_data_5years.xlsx", sheet_name="clients")

# -------------------------
# Filtros
# -------------------------
st.sidebar.header("Filtros")

year_filter = st.sidebar.selectbox(
    "Selecionar Ano",
    sorted(sales["year"].unique())
)

sales_year = sales[sales["year"] == year_filter]

# -------------------------
# KPIs principais
# -------------------------
total_sales = sales_year["revenue"].sum()
num_orders = sales_year["order_id"].nunique()
num_clients = sales_year["client_id"].nunique()
ticket_medio = total_sales / num_orders
freq_compra = num_orders / num_clients

# Crescimento vs ano anterior
prev_year_sales = sales[sales["year"] == year_filter - 1]["revenue"].sum()

if prev_year_sales > 0:
    growth = (total_sales - prev_year_sales) / prev_year_sales * 100
else:
    growth = 0

# Objetivo de crescimento +20%
target_sales = prev_year_sales * 1.2
progress = total_sales / target_sales if target_sales > 0 else 0

# -------------------------
# Mostrar KPIs
# -------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Vendas Totais (€)", f"{total_sales:,.0f}")
col2.metric("Crescimento (%)", f"{growth:.1f}%")
col3.metric("Número de Clientes", num_clients)
col4.metric("Ticket Médio (€)", f"{ticket_medio:,.2f}")
col5.metric("Frequência Compra", f"{freq_compra:.2f}")

st.divider()

# -------------------------
# Vendas vs objetivo
# -------------------------
st.subheader("Vendas vs Objetivo (+20%)")

progress_value = min(progress, 1.0)

st.progress(progress_value)

st.write(f"Objetivo: €{target_sales:,.0f}")
st.write(f"Vendas atuais: €{total_sales:,.0f}")

st.divider()

# -------------------------
# Evolução mensal das vendas
# -------------------------
st.subheader("Evolução das Vendas (Mensal)")

monthly_sales = sales_year.groupby("month")["revenue"].sum().reset_index()

fig_month = px.line(
    monthly_sales,
    x="month",
    y="revenue",
    markers=True,
    title="Vendas por Mês"
)

st.plotly_chart(fig_month, use_container_width=True)

# -------------------------
# Comparação entre anos
# -------------------------
st.subheader("Comparação de Vendas por Ano")

year_sales = sales.groupby("year")["revenue"].sum().reset_index()

fig_year = px.bar(
    year_sales,
    x="year",
    y="revenue",
    title="Vendas Totais por Ano"
)

st.plotly_chart(fig_year, use_container_width=True)

# -------------------------
# Frequência de compra
# -------------------------
st.subheader("Distribuição da Frequência de Compra")

orders_per_client = sales_year.groupby("client_id")["order_id"].count()

fig_freq = px.histogram(
    orders_per_client,
    nbins=20,
    title="Número de Compras por Cliente"
)

st.plotly_chart(fig_freq, use_container_width=True)