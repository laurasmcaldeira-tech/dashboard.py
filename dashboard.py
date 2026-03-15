import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------
st.set_page_config(page_title="(Nome da Empresa)", layout="wide")

COLOR_PRIMARY = "#7B1E3A"
COLOR_SECONDARY = "#C49A6C"

st.title("🍷 (Nome da Empresa)")
st.caption("Garrafeira B2B – Dashboard de Vendas")

st.markdown("---")

# -------------------------
# CARREGAR DADOS
# -------------------------
sales = pd.read_excel(
    "wine_dashboard_fictitious_data_dashboard_full.xlsx",
    sheet_name="sales"
)

clients = pd.read_excel(
    "wine_dashboard_fictitious_data_dashboard_full.xlsx",
    sheet_name="clients"
)

sales["date"] = pd.to_datetime(sales["date"])
sales["year"] = sales["date"].dt.year
sales["month"] = sales["date"].dt.month

# -------------------------
# SIDEBAR FILTROS
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

if not selected_years:
    st.warning("Selecione pelo menos um ano.")
    st.stop()

# -------------------------
# FILTRAR DATAFRAME
# -------------------------
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

col1, col2, col3, col4 = st.columns(4)

col1.metric("Vendas Totais (€)", f"{total_sales:,.0f}")
col2.metric("Crescimento (%)", f"{growth:.1f}%")
col3.metric("Número de Clientes", num_clients)
col4.metric("Ticket Médio (€)", f"{ticket_medio:,.2f}")

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

# -------------------------
# Evolução mensal
# -------------------------
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

fig_month.update_layout(
    xaxis_title="Mês",
    yaxis_title="Vendas (€)"
)

st.plotly_chart(fig_month, width="stretch")


# -------------------------
# Comparação anual
# -------------------------
year_sales = (
    sales_filtered
    .groupby("year")["revenue"]
    .sum()
    .reset_index()
)

year_sales = year_sales.sort_values("year")

fig_year = px.bar(
    year_sales,
    x="year",
    y="revenue",
    color_discrete_sequence=[COLOR_PRIMARY],
    title="Comparação de Vendas por Ano"
)

# garantir apenas anos inteiros no eixo
fig_year.update_xaxes(type="category")

fig_year.update_layout(
    xaxis_title="Ano",
    yaxis_title="Vendas (€)"
)

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

# -------------------------
# Novos clientes por ano
# -------------------------
new_clients = (
    clients
    .groupby("start_year")
    .size()
    .reset_index(name="new_clients")
)

# aplicar filtro de anos selecionados
new_clients = new_clients[new_clients["start_year"].isin(selected_years)]

new_clients = new_clients.sort_values("start_year")

fig_clients = px.bar(
    new_clients,
    x="start_year",
    y="new_clients",
    color_discrete_sequence=[COLOR_PRIMARY],
    title="Número de Novos Clientes por Ano"
)

fig_clients.update_layout(
    xaxis_title="Ano",
    yaxis_title="Novos Clientes"
)

fig_clients.update_xaxes(type="category")

# -------------------------
# TOP 3 clientes
# -------------------------
medals = ["🥇", "🥈", "🥉"]

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_clients, width="stretch")

with col2:

    st.subheader("🏆 Top 3 Clientes por Vendas")

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
