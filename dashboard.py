# -*- coding: utf-8 -*-
# Importando as bibliotecas:
import pandas as pd
#import json
#import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from textwrap import wrap
import streamlit as st
import plotly.graph_objects as go
import pymongo

#lendo arquivo com os dados de historico de musicas
#spotify_com_id = pd.read_csv('C:/Users/letic/projetos/spotify/Dash/dados/StreamingHistory_music.csv')

# Conectar ao banco de dados MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Insira sua URI de conexão
db = client["Spotify"]
collection = db["StreamingHistory_music"]
#_id, endTime, artistName, trackName, msPlayed

st.title("Analisando dados do Spotify")


texto = f'''
Os dados a serem analisados são referentes a um período de um ano (03/04/2023 
a 03/04/2024) e foram obtidos do Spotify mediante solicitação de dados da conta 
da própria analista. 

Esta análise visa responder às seguintes perguntas:
1. Quanto tempo foi dedicado ao consumo de conteúdo no Spotify?
2. Quais são as 10 músicas mais escutadas?
3. Quais são os 5 artistas mais ouvidos?
4. Qual é o podcast mais ouvido?
'''
st.text(texto)


st.subheader('1. Quanto tempo foi dedicado ao consumo de conteúdo no Spotify?')

# Recuperar os dados do banco de dados
dados = collection.find({},{'_id':0,'endTime':1, 'msPlayed':1})  # Aqui você pode adicionar filtros, se necessário
# Criar um DataFrame com os dados
df = pd.DataFrame(dados)

#convertendo a coluna endTime (string) para o tipo datetime
df['endTime'] = pd.to_datetime(df['endTime'])
# Extrair apenas a data (ignorando a hora e o minuto)
df['endTime'] = df['endTime'].dt.date

# Adicionar uma nova coluna 'hrPlayed' ao DataFrame com o tempo em horas para cada música
df['hrPlayed'] = df['msPlayed'] / 3600000

tempo_total_musica_ano = df['hrPlayed'].sum()
#agrupando os dados pelo endTime e somando o msPlayed
df_agrupado = df.groupby('endTime')['hrPlayed'].sum().reset_index()

#print (df_agrupado)
#print (tempo_total_musica_ano)

texto = f'''
Durante o período de 03/04/2023 a 03/04/2024, foram escutadas um total de {round(tempo_total_musica_ano,2)} 
horas de música. Quando convertido para dias, isso equivale a {round((tempo_total_musica_ano/24),2)} dias seguidos 
escutando música sem parar. 

No gráfico abaixo (Tempo de Streaming por dia), podemos ver quantas horas de música 
foram escutadas em cada dia do período analisado.
'''
st.text(texto)

fig_tempo_dia = go.Figure()
fig_tempo_dia.add_trace(go.Scatter(x=df_agrupado['endTime'], y=df_agrupado['hrPlayed'], mode='lines', name='Streaming por dia'))

# Configurar título e rótulos dos eixos
fig_tempo_dia.update_layout(title='Tempo de Streaming por dia',
                      xaxis_title='Data',
                      yaxis_title='Tempo (hr)')

# Exibir gráfico usando Streamlit
st.plotly_chart(fig_tempo_dia)

st.subheader('2. Quais são as 10 músicas mais escutadas?')
# Recuperar os dados do banco de dados
dados = collection.find({},{'_id':0,'trackName':1, 'msPlayed':1})  # Aqui você pode adicionar filtros, se necessário
# Criar um DataFrame com os dados
df = pd.DataFrame(dados)

# Adicionar uma nova coluna 'hrPlayed' ao DataFrame com o tempo em horas para cada música
df['hrPlayed'] = df['msPlayed'] / 3600000

#agrupando os dados pelo endTime e somando o msPlayed
df_agrupado = df.groupby('trackName')['hrPlayed'].sum().reset_index()
df_agrupado = df_agrupado.sort_values(by='hrPlayed', ascending=False)

texto = f'''
O top 10 de músicas reproduzidas por mais tempo foi:
{df_agrupado[['trackName', 'hrPlayed']].head(10)}

Não foi analisado o número de reproduções de cada Track, mas sim o tempo de 
reprodução de cada um.

No gráfico interativo abaixo (Tempo de Streaming por música), são mostradas todas 
as músicas escutadas durante o período analisado e seus respectivos tempos de 
reprodução. 
'''
st.text(texto)

fig_tempo_musica = go.Figure()
#fig_tempo_musica.add_trace(go.Scatter(x=df_agrupado['trackName'], y=df_agrupado['msPlayed'], mode='lines', name='Streaming por música'))
fig_tempo_musica.add_trace(go.Bar(x=df_agrupado['trackName'], y=df_agrupado['hrPlayed'], name='Tempo de Streaming por música'))

# Configurar título e rótulos dos eixos
fig_tempo_musica.update_layout(title='Tempo de Streaming por música',
                      xaxis_title='Música',
                      yaxis_title='Tempo (hr)')

# Exibir gráfico usando Streamlit
st.plotly_chart(fig_tempo_musica)

df_musicas = df_agrupado

st.subheader('3. Quais são os 5 artistas mais ouvidos?')

dados = collection.find({},{'_id':0,'artistName':1, 'msPlayed':1})  # Aqui você pode adicionar filtros, se necessário
df = pd.DataFrame(dados)
df['hrPlayed'] = df['msPlayed'] / 3600000

df_agrupado = df.groupby('artistName')['hrPlayed'].sum().reset_index()
df_agrupado = df_agrupado.sort_values(by='hrPlayed', ascending=False)

texto = f'''
O top 5 de artistas reproduzidos por mais tempo foi:
{df_agrupado[['artistName', 'hrPlayed']].head(5)}

No gráfico interativo abaixo (Tempo de Streaming por artista), são mostrados todos 
os artistas e seus respectivos tempos de reprodução. 
'''
st.text(texto)

fig_tempo_artista = go.Figure()
fig_tempo_artista.add_trace(go.Bar(x=df_agrupado['artistName'], y=df_agrupado['hrPlayed'], name='Tempo de Streaming por artista'))

fig_tempo_artista.update_layout(title='Tempo de Streaming por artista',
                      xaxis_title='Artista',
                      yaxis_title='Tempo (hr)')

st.plotly_chart(fig_tempo_artista)

df_artistas = df_agrupado
st.subheader('4. Qual é o podcast mais ouvido?')

collection = db["StreamingHistory_podcast"]
dados = collection.find({},{'_id':0,'podcastName':1, 'msPlayed':1})  # Aqui você pode adicionar filtros, se necessário
df = pd.DataFrame(dados)
df['hrPlayed'] = df['msPlayed'] / 3600000

df_agrupado = df.groupby('podcastName')['hrPlayed'].sum().reset_index()
df_agrupado = df_agrupado.sort_values(by='hrPlayed', ascending=False)

texto = f'''
O podcast mais ouvido foi:
{df_agrupado[['podcastName', 'hrPlayed']].head(1)}

No gráfico interativo abaixo (Tempo de Streaming por podcast), são mostrados todos 
os podcasts ouvidos e seus respectivos tempos de reprodução. 
'''
st.text(texto)

fig_tempo_artista = go.Figure()
fig_tempo_artista.add_trace(go.Bar(x=df_agrupado['podcastName'], y=df_agrupado['hrPlayed'], name='Tempo de Streaming por podcast'))

fig_tempo_artista.update_layout(title='Tempo de Streaming por podcast',
                      xaxis_title='Podcast',
                      yaxis_title='Tempo (hr)')

st.plotly_chart(fig_tempo_artista)

df_podcast = df_agrupado

