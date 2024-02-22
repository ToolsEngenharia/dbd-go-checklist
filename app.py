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

colores = [ 'blue', 'green', 'orange', 'red', 'violet', 'rainbow']
def grafico_pizza(df, empresa):
	fig = px.pie(df[df['EMPRESA'] == empresa], names='STATUS')
	return fig

def grafico_barras(df, xis, yis, categoria='STATUS'):
	fig = px.bar(df, x=xis, y=yis, color=categoria)
	return fig

filData = st.sidebar.date_input('Selecione a data', datetime.now().date())
# filIntervalo = st.sidebar.date_input('Selecione o intervalo de datas', (datetime.now().date(), datetime(2025, 1, 1).date()))
# filIntervalo = st.sidebar.slider('Selecione o intervalo de datas', min_value=datetime(2020, 1, 1).date(), max_value=datetime(2025, 1, 1).date(), value=(datetime.now().date(), datetime.now().date()), format="DD/MM/YYYY")
filStatus = st.sidebar.multiselect('Selecione o Status', listStatus, default=listStatus)
filCriticidade = st.sidebar.multiselect('Selecione a Criticidade', listCriticidade, default=listCriticidade)

with st.expander('PROGRAMADAS X REALIZADAS', expanded=True):
	programadas = df.shape[0]
	previstas = df[df['PREVISÃO DE CONCLUSÃO'] <= str(filData)].shape[0]
	realizadas = df[df['STATUS'] == 'Concluído'].shape[0]
	col1, col2 = st.columns([3, 1.5])
	with col1:
		c = st.container(border=True)
		c.subheader('TOTAL DE ATIVIDADES PROGRAMADAS PARA CONCLUSÃO')
		c.plotly_chart(px.bar(x=[programadas, previstas, realizadas], y=['PROGRAMADAS', 'PREVISTAS', 'REALIZADAS'], color=['PROGRAMADAS', 'PREVISTAS', 'REALIZADAS']), use_container_width=True)
	with col2:
		c = st.container(border=True)
		c.subheader('% ATIVIDADES REALIZADAS')
		c.plotly_chart(px.pie(names=['REALIZADAS', 'NÃO REALIZADAS'], values=[(realizadas/programadas)*100, 100-(realizadas/programadas)*100]), use_container_width=True)

	c = st.container(border=True)
	c.subheader('ACOMPANHAMENTO PRODUÇÃO')
	col1, col2, col3 = c.columns(3)
	with col1:
		st.container(border=True).metric(f':blue[PROGRAMADO]', programadas)
	with col2:
		st.container(border=True).metric(f':red[PREVISTO]', previstas)
	with col3:
		st.container(border=True).metric(f':green[REALIZADO]', realizadas)

st.divider()
st.subheader('PRÓXIMAS ATIVIDADES')

# periodo = st.slider('Qual intervalo de datas deseja filtrar?',value=(datetime.now().date(), datetime(2025, 1, 1).date()), format="DD/MM/YYYY")
df_proximas_tarefas = df[(df['PREVISÃO DE CONCLUSÃO'] >= str(filData)) & (df['STATUS'].isin(filStatus)) & (df['CRITICIDADE'].isin(filCriticidade))]
col1, col2 = st.columns(2)
with col1:
	st.metric(f'TOTAL DE ATIVIDADES:  PERÍODO - {filData}', df_proximas_tarefas.shape[0])

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
	df_filtro = df_proximas_tarefas[df_proximas_tarefas['EMPRESA'] == empresa]
	c = st.container(border=True)
	c.subheader(f':{colores[np.random.randint(0, 5)]}[{empresa}]')

	metric1, metric2, metric3, metric4, metric5 = c.columns(5)
	with metric1:
		st.container(border=True).metric('Total de Tarefas', df_filtro.shape[0])
	with metric2:
		st.container(border=True).metric('Em Andamento', df_filtro[df_filtro['STATUS'] == 'Em andamento'].shape[0])
	with metric3:
		st.container(border=True).metric('Aguardando Data', df_filtro[df_filtro['STATUS'] == 'Aguardando data'].shape[0])
	with metric4:
		st.container(border=True).metric('Aguardando Data/Atrasado', df_filtro[df_filtro['STATUS'] == 'Aguardando data/Atrasado'].shape[0])
	with metric5:
		st.container(border=True).metric('Atrasado', df_filtro[df_filtro['STATUS'] == 'Atrasado'].shape[0])

	with c.expander('GRÁFICO', expanded=True):
		programadas = df.shape[0]
		previstas = df[df['PREVISÃO DE CONCLUSÃO'] <= str(filData)].shape[0]
		realizadas = df[df['STATUS'] == 'Concluído'].shape[0]
		col1, col2 = st.columns([3, 1.5])
		with col1:
			c1 = st.container(border=True)
			c1.subheader('TOTAL DE ATIVIDADES POR STATUS')
			c1.plotly_chart(px.bar(df_filtro.groupby('STATUS').size().reset_index(name='QUANTIDADE'), x='QUANTIDADE', y='STATUS', color='STATUS'), use_container_width=True)

		with col2:
			c1 = st.container(border=True)
			c1.subheader('% ATIVIDADES POR STATUS')
			c1.plotly_chart(grafico_pizza(df_proximas_tarefas, empresa), use_container_width=True)

	with c.expander('ATIVIDADES', expanded=True):
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

