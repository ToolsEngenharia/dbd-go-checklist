import pandas as pd
import requests as req
import streamlit as st

## Função para obter os dados - GOOGLE SHEETS
@st.cache_data()
def getDadosSheet():
	url = "https://script.google.com/macros/s/AKfycbyDdODiPH0uyVx42JRe59MAsOPYL-4DPLTsIUIchmhoZfJB8nYKli3voiTHK-1xtUpxpQ/exec"
	response = req.get(url)
	dados = response.json()
	return dados['dados']
