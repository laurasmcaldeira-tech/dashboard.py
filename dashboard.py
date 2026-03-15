# -------------------------
# CONFIGURAÇÃO
# -------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# configuração da página
st.set_page_config(
    page_title="Wine Sales Dashboard",
    page_icon="🍷",
    layout="wide"
)

# cores do dashboard
COLOR_PRIMARY = "#7B1E3A"   # vinho
COLOR_SECONDARY = "#C49A6C" # dourado

# caminho para assets
BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")

# -------------------------
# CABEÇALHO DO DASHBOARD
# -------------------------

logo_path = "assets/logo.png"

col1, col2 = st.columns([1,4])

with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

with col2:
    st.title("Wine Sales Dashboard")
    st.caption("Garrafeira B2B – Dashboard de Vendas")

st.markdown("---")markdown("---")

# -------------------------
# CARREGAR DADOS
# -------------------------
sales = pd.read_excel(
    "wine_dashboard_fictitious_data_full_with_leads.xlsx",
    sheet_name="sales"
)

clients = pd.read_excel(
    "wine_dashboard_fictitious_data_full_with_leads.xlsx",
    sheet_name="clients"
)

leads = pd.read_excel(
    "wine_dashboard_fictitious_data_full_with_leads.xlsx",
    sheet_name="leads"
)

sales["date"] = pd.to_datetime(sales["date"])
sales["year"] = sales["date"].dt.year
sales["month"] = sales["date"].dt.month

# -------------------------
# FILTROS
# -------------------------
st.sidebar.header("Filtros")

years = sorted(sales["year"].unique())

selected_years = st.sidebar.multiselect(
    "Selecionar anos",
    years,
    default=years
)

regions = sorted(sales["region"].unique())

selected_regions = st.sidebar.multiselect(
    "Selecionar região",
    regions,
    default=regions
)

retail_types = sorted(sales["retail_type"].unique())

selected_retail = st.sidebar.multiselect(
    "Tipo de cliente",
    retail_types,
    default=retail_types
)

sales_filtered = sales[
    (sales["year"].isin(selected_years)) &
    (sales["region"].isin(selected_regions)) &
    (sales["retail_type"].isin(selected_retail))
]

# -------------------------
# KPIs
# -------------------------
st.header("📊 Performance de Vendas")

total_sales = sales_filtered["revenue"].sum()

num_orders = sales_filtered["order_id"].nunique()

num_clients = sales_filtered["client_id"].nunique()

ticket_medio = total_sales / num_orders if num_orders > 0 else 0

current_year = max(selected_years)
prev_year = current_year - 1

current_sales = sales[sales["year"] == current_year]["revenue"].sum()
prev_sales = sales[sales["year"] == prev_year]["revenue"].sum()

growth = ((current_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0

# -------------------------
# TAXA DE CONVERSÃO
# -------------------------
leads_filtered = leads[leads["year"].isin(selected_years)]

total_leads = len(leads_filtered)

converted_leads = leads_filtered["converted"].sum()

conversion_rate = converted_leads / total_leads if total_leads > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Vendas Totais (€)", f"{total_sales:,.0f}")
col2.metric("Crescimento (%)", f"{growth:.1f}%")
col3.metric("Número de Clientes", num_clients)
col4.metric("Ticket Médio (€)", f"{ticket_medio:,.2f}")
col5.metric("Taxa de Conversão", f"{conversion_rate*100:.1f}%")

st.markdown("---")

# -------------------------
# OBJETIVO 2026
# -------------------------
st.header("🎯 Vendas vs Objetivo 2026 (+20%)")

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

st.markdown("---")

# -------------------------
# EVOLUÇÃO DAS VENDAS
# -------------------------
st.header("📈 Evolução das Vendas")

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

fig_month.update_traces(line=dict(width=3))

st.plotly_chart(fig_month, width="stretch")

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
    color_discrete_sequence=[COLOR_PRIMARY],
    title="Comparação de Vendas por Ano"
)

fig_year.update_xaxes(type="category")

st.plotly_chart(fig_year, width="stretch")

st.markdown("---")

# -------------------------
# SEGMENTAÇÃO
# -------------------------
st.header("🧭 Segmentação de Clientes")

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
    color_discrete_sequence=[COLOR_PRIMARY],
    title="Vendas por Região"
)

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
    color_discrete_sequence=[COLOR_SECONDARY],
    title="Vendas por Tipo de Cliente"
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_region, width="stretch")

with col2:
    st.plotly_chart(fig_retail, width="stretch")

st.markdown("---")

# -------------------------
# CLIENTES
# -------------------------
st.header("👥 Clientes")

new_clients = (
    clients
    .groupby("start_year")
    .size()
    .reset_index(name="new_clients")
)

new_clients = new_clients[new_clients["start_year"].isin(selected_years)]

fig_clients = px.bar(
    new_clients,
    x="start_year",
    y="new_clients",
    color_discrete_sequence=[COLOR_PRIMARY],
    title="Número de Novos Clientes por Ano"
)

fig_clients.update_xaxes(type="category")

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_clients, width="stretch")

with col2:

    st.subheader("🏆 Top 3 Clientes por Vendas")

    medals = ["🥇", "🥈", "🥉"]

    for year in selected_years:

        st.markdown(f"**📅 Ano {year}**")

        top_clients = (
            sales_filtered[sales_filtered["year"] == year]
            .groupby("client_id")["revenue"]
            .sum()
            .reset_index()
        )

        top_clients = top_clients.sort_values(
            by="revenue",
            ascending=False
        ).head(3)

        top_clients["Posição"] = medals[:len(top_clients)]

        top_clients = top_clients.rename(
            columns={
                "client_id": "Cliente ID",
                "revenue": "Vendas (€)"
            }
        )

        top_clients["Vendas (€)"] = top_clients["Vendas (€)"].map(
            lambda x: f"€{x:,.0f}"
        )

        table = top_clients[["Posição", "Cliente ID", "Vendas (€)"]]

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True
        )
