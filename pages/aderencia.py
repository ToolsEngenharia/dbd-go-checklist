import pandas as pd
import streamlit as st
import numpy as np
from getDados import getDadosSheet


st.set_page_config(layout="wide", page_title="ADERÊNCIA EQUIPE")


st.title('ACOMPANHAMENTO EQUIPE DE PRODUÇÃO')

inpData = st.date_input('', value=pd.to_datetime('today').date())

df = pd.DataFrame(getDadosSheet())

colores = [ 'blue', 'green', 'orange', 'red', 'violet', 'rainbow']
empresas = np.sort(df['EMPRESA'].unique())

def card(empresa):
	c = st.container(border=True)
	nome = empresa.strip().upper()
	c.subheader(f':{colores[np.random.randint(0, 5)]}[{nome}]')
	metric1, metric2 = c.columns(2)
	with metric1:
		c1 = st.container(border=True)
		programado = df[(df['EMPRESA'] == empresa)].shape[0]
		c1.metric('PROGRAMADO', programado)
		
	with metric2:
		c2 = st.container(border=True)
		realizado = df[(df['EMPRESA'] == empresa) & (df['STATUS'] == 'Concluído')].shape[0]
		c2.metric('REALIZADO', realizado)
	
	c3 = c.container(border=True)
	c3.metric('DESENVOLVIDO', f'{realizado/programado:.2%}')
	

col1, col2, col3 = st.columns(3)
for index, empresa in enumerate(empresas):
	if index % 3 == 0:
		with col1:
			card(empresa=empresa)
				
	elif index % 3 == 1:
		with col2:
			card(empresa=empresa)
	else:
		with col3:
			card(empresa=empresa)


# with st.expander('Tabela de Dados'):
# 	st.write(df)

# empresas = np.insert(empresas, 0, 'TODOS')

# st.title('Análise de Dados - Google Sheets')
# st.write(df)
