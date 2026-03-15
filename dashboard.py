import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Configuração da página
# -------------------------
st.set_page_config(page_title="Wine Sales Dashboard", layout="wide")

st.title("Wine Sales Dashboard")
st.caption("Garrafeira B2B – Dashboard de Vendas")

# -------------------------
# Carregar dados
# -------------------------
sales = pd.read_excel("wine_dashboard_fictitious_data_dashboard_full.xlsx", sheet_name="sales")
clients = pd.read_excel("wine_dashboard_fictitious_data_dashboard_full.xlsx", sheet_name="clients")

sales["date"] = pd.to_datetime(sales["date"])
sales["year"] = sales["date"].dt.year
sales["month"] = sales["date"].dt.month

# -------------------------
# SIDEBAR FILTROS
# -------------------------
st.sidebar.header("Filtros")

# filtro anos
years = sorted(sales["year"].unique())

selected_years = st.sidebar.multiselect(
    "Selecionar anos",
    years,
    default=years
)

# filtro região
regions = sorted(sales["region"].unique())

selected_regions = st.sidebar.multiselect(
    "Selecionar região",
    regions,
    default=regions
)

# filtro tipo cliente
retail_types = sorted(sales["retail_type"].unique())

selected_retail = st.sidebar.multiselect(
    "Tipo de cliente",
    retail_types,
    default=retail_types
)

if not selected_years:
    st.warning("Selecione pelo menos um ano.")
    st.stop()

# -------------------------
# FILTRO DATAFRAME
# -------------------------
sales_filtered = sales[
    (sales["year"].isin(selected_years)) &
    (sales["region"].isin(selected_regions)) &
    (sales["retail_type"].isin(selected_retail))
]

st.caption(f"Anos selecionados: {selected_years}")

# -------------------------
# KPIs
# -------------------------
total_sales = sales_filtered["revenue"].sum()

num_orders = sales_filtered["order_id"].nunique()

num_clients = sales_filtered["client_id"].nunique()

ticket_medio = total_sales / num_orders if num_orders > 0 else 0

# crescimento vs ano anterior
current_year = max(selected_years)
prev_year = current_year - 1

current_sales = sales[sales["year"] == current_year]["revenue"].sum()
prev_sales = sales[sales["year"] == prev_year]["revenue"].sum()

growth = ((current_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0

# -------------------------
# Mostrar KPIs
# -------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Vendas Totais (€)", f"{total_sales:,.0f}")
col2.metric("Crescimento (%)", f"{growth:.1f}%")
col3.metric("Número de Clientes", num_clients)
col4.metric("Ticket Médio (€)", f"{ticket_medio:,.2f}")

st.divider()

# -------------------------
# OBJETIVO 2026 (+20%)
# -------------------------
st.subheader("Vendas vs Objetivo 2026 (+20%)")

sales_2025 = sales[sales["year"] == 2025]["revenue"].sum()
target_2026 = sales_2025 * 1.20

sales_2026 = sales[sales["year"] == 2026]
sales_2026_ytd = sales_2026["revenue"].sum()

current_month = sales_2026["month"].max()

expected_progress = current_month / 12
expected_sales = target_2026 * expected_progress

performance_ratio = sales_2026_ytd / expected_sales if expected_sales > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("Objetivo anual 2026", f"€{target_2026:,.0f}")
col2.metric("Esperado até agora", f"€{expected_sales:,.0f}")
col3.metric("Vendas atuais 2026", f"€{sales_2026_ytd:,.0f}")

st.progress(min(performance_ratio, 1.0))

st.metric(
    "Performance vs esperado",
    f"{performance_ratio*100:.1f}%"
)

st.divider()

# -------------------------
# EVOLUÇÃO MENSAL
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
# COMPARAÇÃO ANUAL
# -------------------------
st.subheader("Comparação de Vendas por Ano")

year_sales = (
    sales_filtered
    .groupby("year")["revenue"]
    .sum()
    .reset_index()
)

fig_year = px.bar(
    year_sales,
    x="year",
    y="revenue",
    title="Vendas Totais por Ano"
)

st.plotly_chart(fig_year, width="stretch")

# -------------------------
# VENDAS POR REGIÃO
# -------------------------
st.subheader("Vendas por Região")

sales_region = (
    sales_filtered
    .groupby("region")["revenue"]
    .sum()
    .reset_index()
)

fig_region = px.bar(
    sales_region,
    x="region",
    y="revenue",
    title="Vendas por Região"
)

st.plotly_chart(fig_region, width="stretch")

# -------------------------
# VENDAS POR TIPO DE CLIENTE
# -------------------------
st.subheader("Vendas por Tipo de Cliente")

sales_retail = (
    sales_filtered
    .groupby("retail_type")["revenue"]
    .sum()
    .reset_index()
)

fig_retail = px.bar(
    sales_retail,
    x="retail_type",
    y="revenue",
    title="Vendas por Tipo de Cliente"
)

st.plotly_chart(fig_retail, width="stretch")

# -------------------------
# NOVOS CLIENTES POR ANO
# -------------------------
st.subheader("Novos Clientes por Ano")

new_clients = (
    clients[clients["start_year"].isin(selected_years)]
    .groupby("start_year")
    .size()
    .reset_index(name="new_clients")
)

fig_clients = px.bar(
    new_clients,
    x="start_year",
    y="new_clients",
    title="Novos Clientes por Ano",
    labels={
        "start_year": "Ano",
        "new_clients": "Número de Novos Clientes"
    }
)

st.plotly_chart(fig_clients, width="stretch")
