import pandas as pd
import requests as req
import streamlit as st

## Função para obter os dados - GOOGLE SHEETS
@st.cache_data()
def getDadosSheet():
	url = "https://script.google.com/macros/s/AKfycbxBemeIG-iFCz_FHeCwy0WTlyPTqKrEiAJLsvrM6FSomivdJZc4PmMrkD3i7mhZGD6t-A/exec"
	response = req.get(url)
	dados = response.json()
	return dados['dados']
