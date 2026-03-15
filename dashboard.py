import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Configuração da página
# -------------------------
st.set_page_config(page_title="(nome da empresa)", layout="wide")

st.title("(nome da empresa) Dashboard")
st.markdown("Garrafeira B2B – Análise de Vendas")

# -------------------------
# Carregar dados
# -------------------------
sales = pd.read_excel("wine_dashboard_fictitious_data_5years.xlsx", sheet_name="sales")
clients = pd.read_excel("wine_dashboard_fictitious_data_5years.xlsx", sheet_name="clients")

# -------------------------
# Converter data
# -------------------------
sales["date"] = pd.to_datetime(sales["date"])

# -------------------------
# Filtro de anos
# -------------------------
st.sidebar.header("Filtros")

years = sorted(sales["date"].dt.year.unique())

selected_years = st.sidebar.multiselect(
    "Selecionar anos",
    years,
    default=years
)

if not selected_years:
    st.warning("Selecione pelo menos um ano.")
    st.stop()

# Filtrar dataframe
sales_filtered = sales[sales["date"].dt.year.isin(selected_years)]

# -------------------------
# KPIs
# -------------------------
total_sales = sales_filtered["revenue"].sum()

num_orders = sales_filtered["order_id"].nunique()

num_clients = sales_filtered["client_id"].nunique()

ticket_medio = total_sales / num_orders if num_orders > 0 else 0

freq_compra = num_orders / num_clients if num_clients > 0 else 0

# Crescimento vs ano anterior
current_year = max(selected_years)
prev_year = current_year - 1

current_sales = sales[sales["year"] == current_year]["revenue"].sum()
prev_sales = sales[sales["year"] == prev_year]["revenue"].sum()

growth = ((current_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0

# Objetivo de crescimento +20%
target_sales = prev_sales * 1.2
progress = current_sales / target_sales if target_sales > 0 else 0

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

monthly_sales = (
    sales_filtered
    .groupby(["year", "month"])["revenue"]
    .sum()
    .reset_index()
)

fig_month = px.line(
    monthly_sales,
    x="month",
    y="revenue",
    color="year",
    markers=True,
    title="Evolução das vendas por mês"
)

st.plotly_chart(fig_month, width="stretch")

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
st.subheader("Frequência de Compra dos Clientes")

# número de encomendas por cliente
orders_per_client = (
    sales_filtered
    .groupby("client_id")["order_id"]
    .count()
    .reset_index(name="num_orders")
)

# criar faixas de frequência
bins = [0, 1, 3, 6, 100]
labels = ["1 compra", "2-3 compras", "4-6 compras", "7+ compras"]

orders_per_client["frequency_group"] = pd.cut(
    orders_per_client["num_orders"],
    bins=bins,
    labels=labels
)

# contar clientes por grupo
freq_distribution = (
    orders_per_client
    .groupby("frequency_group")
    .size()
    .reset_index(name="num_clients")
)

# gráfico
fig_freq = px.bar(
    freq_distribution,
    x="frequency_group",
    y="num_clients",
    title="Clientes por Frequência de Compra",
    labels={
        "frequency_group": "Frequência de Compra",
        "num_clients": "Número de Clientes"
    }
)

st.plotly_chart(fig_freq, width="stretch")
