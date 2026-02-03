import streamlit as st
import pandas as pd
import plotly.express as px

# --- configuração da pagina ---
# define o titulo da pagina, o icone e o layout para ocupar a largura inteira.
st.set_page_config(
      page_title='dashboard de salarios na area de dados',
      page_icon='📊',
      layout='wide'
)

 # --- carregamento dos dados ---
df = pd.read_csv('https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv')

# --- barra lateral (filtros)
st.sidebar.header('🔍Filtros')

# filtro de ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect('Ano', anos_disponiveis, default=anos_disponiveis)

# filtro de senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect('Senioridades', senioridades_disponiveis, default=senioridades_disponiveis)

# filtro por tipo de contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect('Tipo de Contrato', contratos_disponiveis, default=contratos_disponiveis)

# fitro por tamanho da empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect('Tamanho da Empresa', tamanhos_disponiveis, default=tamanhos_disponiveis)


# --- filtragem do DataFrame ---
# o dataframe principal é filtrado com base nas seleçoes feitas na barra lateral.
df_filtrado = df[
      (df['ano'].isin(anos_selecionados)) &
      (df['senioridade'].isin(senioridades_selecionadas)) &
      (df['contrato'].isin(contratos_selecionados)) &
      (df['tamanho_empresa'].isin(tamanhos_selecionados))
]
# --- conteudo principal ---
st.title('🎲 Dashboard de Análise de Salários na Área de Dados')
st.markdown('Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.')

# --- metricas principais (KPIs) ---
st.subheader('Métricas gerais (Salário anual USD')

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric('salario medio', f'${salario_medio:,.0f}')
col2.metric('salario maximo', f'${salario_maximo:,.0f}')
col3.metric('Total de Registros', f'{total_registros:,.0f}')
col4.metric('Cargo mais Frequente', cargo_mais_frequente)

st.markdown('---')

#analise visuais com plotly
st.subheader('Gráficos')

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 cargos por salário médio',
            labels= {'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_cargos, width='stretch')
    else:
        st.warning('Nenhum dado para exibir no gráfico de cargos.')

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist= px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição de salários anuais',
            labels={'usd': 'Faixa salarial  (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, width='stretch')
    else:
        st.warning('Nenhum dado para exibir no gráfico de distribuição.')

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='proporçao dos tipos de trabalho',
            hole=0.5
            )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, width='stretch')
    else:
        st.warning('Nenhum dado para exibir no gráfico dos tipos de trabalho.')

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'data scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
        locations='residencia_iso3',
        color='usd',
        color_continuous_scale='rdylgn',
        title='Salário médio do Cientista de Dados por país',
        labels={'usd': 'salario medio (USD)', 'residencia_iso3': 'país'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, width='stretch')
    else:
        st.warning('Nenhum dado para exibir no gráfico de países.')

# --- tabela de dados detalhados ---
st.subheader('dados detalhados')
st.dataframe(df_filtrado)

