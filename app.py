import streamlit as st
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
import plotly.express as px

from  getDados import getDadosSheet
from datetime import datetime

# settings
st.set_page_config(layout="wide", page_title="CHECKLIST")

col1, col2, col3 = st.columns([2, 4, 1])
with col1:
	st.image('./images/Logo Verde.png', width=200)
with col2:
	st.header('RELATÓRIO DE ATIVIDADES - CHECKLIST')
with col3:
	if st.button('Atualizar Dados'):
		st.cache_data.clear()
		st.experimental_rerun()

df = pd.DataFrame(getDadosSheet())
df['EMPRESA'] = df['EMPRESA'].str.upper()
df['DATA'] = df['DATA'].apply(lambda x: str(x).split('T')[0])
df['PREVISÃO DE CONCLUSÃO'] = df['PREVISÃO DE CONCLUSÃO'].apply(lambda x: str(x).split('T')[0])
df['CRONOGRAMA BASELINE'] = df['CRONOGRAMA BASELINE'].apply(lambda x: str(x).split('T')[0])
df['CRITICIDADE'] = np.where(df['CRITICIDADE'] == 0, '(0) Urgente e Critica',
								np.where(df['CRITICIDADE'] == 1, '(1) Impede Inicio de Qualificação',
									np.where(df['CRITICIDADE'] == 2, '(2) Impede Conclusão de Qualificação',
										np.where(df['CRITICIDADE'] == 3, '(3) Acabamentos', 'N/A'))))

empresas = np.sort( df['EMPRESA'].unique())
listStatus = np.sort( df['STATUS'].unique())
listCriticidade = np.sort( df['CRITICIDADE'].unique())

def grafico_pizza(df, empresa):
	fig = px.pie(df[df['EMPRESA'] == empresa], names='STATUS')
	return fig

def grafico_barras(df, xis, yis, categoria='STATUS'):
	fig = px.bar(df, x=xis, y=yis, color=categoria)
	return fig

# verificar se a data é válida e encontrar a data mínima e máxima
# dat_min = df['PREVISÃO DE CONCLUSÃO'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").date()).min()
# st.write(f'Data mínima: {dat_min}')
# st.write(f'Data mínima: {datetime.strptime(dat_min, "%Y-%m-%d").date()}')


# # filter input data slice
# st.write(f'Filtrando dados para a data: {dataFilter}')
# stll = st.slider('Qual intervalo de datas deseja filtrar?',value=(datetime.now().date(), datetime(2025, 1, 1).date()), format="DD/MM/YYYY")

# st.write(f'Filtrando dados para o intervalo de datas: {stll}')

dataFilter = st.sidebar.date_input('Selecione a data', datetime.now().date())
filStatus = st.sidebar.multiselect('Selecione o Status', listStatus, default=listStatus)
filCriticidade = st.sidebar.multiselect('Selecione a Criticidade', listCriticidade, default=listCriticidade)

with st.expander('PROGRAMADAS X REALIZADAS', expanded=True):
	programadas = df.shape[0]
	previstas = df[df['PREVISÃO DE CONCLUSÃO'] <= str(dataFilter)].shape[0]
	realizadas = df[df['STATUS'] == 'Concluído'].shape[0]
	col1, col2 = st.columns([3, 1.5])
	with col1:
		st.container(border=True).plotly_chart(px.bar(x=[programadas, previstas, realizadas], y=['PROGRAMADAS', 'PREVISTAS', 'REALIZADAS'], color=['PROGRAMADAS', 'PREVISTAS', 'REALIZADAS']), use_container_width=True)
	with col2:
		st.container(border=True).plotly_chart(px.pie(names=['PROGRAMADAS', 'REALIZADAS'], values=[(realizadas/programadas)*100, 100-(realizadas/programadas)*100]), use_container_width=True)

	c = st.container(border=True)
	c.caption('ACOMPANHAMENTO PRODUÇÃO')
	col1, col2, col3 = c.columns(3)
	with col1:
		st.container(border=True).metric(f':blue[PROGRAMADO]', programadas)
	with col2:
		st.container(border=True).metric(f':red[PREVISTO]', previstas)
	with col3:
		st.container(border=True).metric(f':green[REALIZADO]', realizadas)

st.divider()
st.subheader('TAREFAS FUTURAS')

	# periodo = st.slider('Qual intervalo de datas deseja filtrar?',value=(datetime.now().date(), datetime(2025, 1, 1).date()), format="DD/MM/YYYY")
df_proximas_tarefas = df[(df['PREVISÃO DE CONCLUSÃO'] >= str(dataFilter)) & (df['STATUS'].isin(filStatus)) & (df['CRITICIDADE'].isin(filCriticidade))]
col1, col2 = st.columns(2)
with col1:
	st.metric(f'TOTAL DE ATIVIDADES:  PERÍODO - {dataFilter}', df_proximas_tarefas.shape[0])

df_Status = df_proximas_tarefas.groupby(['EMPRESA', 'STATUS']).size().reset_index(name='QUANTIDADE')
df_Criticidade = df_proximas_tarefas.groupby(['EMPRESA', 'CRITICIDADE']).size().reset_index(name='QUANTIDADE')

tab1, tab2 = st.tabs(['STATUS', 'CRITICIDADE'])
with tab1:
	st.plotly_chart(grafico_barras(df_Status, 'EMPRESA', 'QUANTIDADE'), use_container_width=True)
with tab2:
	st.plotly_chart(grafico_barras(df_Criticidade, xis='EMPRESA', yis='QUANTIDADE', categoria='CRITICIDADE'), use_container_width=True)

# with st.expander('TAREFAS FUTURAS'):
# 	for atividade in df_proximas_tarefas['PENDENCIA']:
# 		st.subheader(f'{atividade}')
		

empresasP = np.sort( df_proximas_tarefas['EMPRESA'].unique())
for empresa in empresasP:
	c = st.container(border=True)
	c.subheader(f':blue[{empresa.strip()}]')

	metric1, metric2, metric3, metric4, metric5 = c.columns(5)
	metric1.metric('Total de Tarefas', df_proximas_tarefas[df_proximas_tarefas['EMPRESA'] == empresa].shape[0])
	metric2.metric('Em Andamento', df_proximas_tarefas[(df_proximas_tarefas['EMPRESA'] == empresa) & (df_proximas_tarefas['STATUS'] == 'Em andamento')].shape[0])
	metric3.metric('Aguardando Data', df_proximas_tarefas[(df_proximas_tarefas['EMPRESA'] == empresa) & (df_proximas_tarefas['STATUS'] == 'Aguardando data')].shape[0])
	metric4.metric('Aguardando Data/Atrasado', df_proximas_tarefas[(df_proximas_tarefas['EMPRESA'] == empresa) & (df_proximas_tarefas['STATUS'] == 'Aguardando data/Atrasado')].shape[0])
	metric5.metric('Atrasado', df_proximas_tarefas[(df_proximas_tarefas['EMPRESA'] == empresa) & (df_proximas_tarefas['STATUS'] == 'Atrasado')].shape[0])

	c.expander('Gráfico').plotly_chart(grafico_pizza(df_proximas_tarefas, empresa), use_container_width=True)

	with c.expander('Atividades', expanded=True):
		st.dataframe(df_proximas_tarefas[df_proximas_tarefas['EMPRESA'] == empresa])
		# for atividade in df_proximas_tarefas[df_proximas_tarefas['EMPRESA'] == empresa]['PENDENCIA']:
		# 	st.subheader(f'{atividade}')

# st.dataframe(df_proximas_tarefas)

# tab1, tab2 = st.tabs(['Tab1', 'Tab2'])
# with tab1:
# 	st.title('Empresas por Status')
# 	for empresa in empresas:
# 		st.subheader(f'{empresa}')
# 		st.bar_chart((df[df['EMPRESA'] == empresa]['STATUS'].value_QUAs().sort_index()), use_container_width=True)

# with tab2:
# 	col1, col2, col3 = st.columns(3)
# 	for index, empresa in enumerate(empresas):
# 		if index % 3 == 0:
# 			with col1:
# 				c = st.container(border=True)
# 				c.subheader(f':blue[{empresa}]')
# 				c.bar_chart((df[df['EMPRESA'] == empresa]['STATUS'].value_QUAs().sort_index()), use_container_width=True)

# 		elif index % 3 == 1:
# 			with col2:
# 				c = st.container(border=True)
# 				c.subheader(f':blue[{empresa}]')
# 				c.bar_chart((df[df['EMPRESA'] == empresa]['STATUS'].value_QUAs().sort_index()), use_container_width=True)
# 		else:
# 			with col3:
# 				c = st.container(border=True)
# 				c.subheader(f':green[{empresa}]')
# 				c.bar_chart((df[df['EMPRESA'] == empresa]['STATUS'].value_QUAs().sort_index()), use_container_width=True)

# with st.expander('Tabela de Dados'):
# 	st.write(df)

# empresas = np.insert(empresas, 0, 'TODOS')

# st.title('Análise de Dados - Google Sheets')
# st.write(df)

