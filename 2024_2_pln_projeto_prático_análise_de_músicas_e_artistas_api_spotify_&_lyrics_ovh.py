# -*- coding: utf-8 -*-
"""2024.2 - PLN - Projeto Prático - Análise de Músicas e Artistas - API Spotify & Lyrics.ovh.ipynb


---

# **Parte 1 - Configurações do ambiente**
---

No tópico a seguir, iremos realizar as **configurações do ambiente**, instalando as **bibliotecas e APIs** necessárias para o projeto.

##### **Instalação das bibliotecas e APIs que serão utilizadas**
"""

"""##### **Importando as bibliotecas que serão utilizadas**"""

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
from pprint import pprint
import getpass
import os
import json
import requests
import time
import pandas as pd
import streamlit as st
import altair as alt
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

"""##### **Configuração da API do Spotify**"""

#Configuração das credenciais da API do Spotify
client_id = "3dd5183184794d519b0b476b7e02c668"
client_secret = "0654a709156b4382860608b8db3b5074"

#Configuração da autenticação
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(auth_manager=auth_manager)
sp = spotipy.Spotify(auth_manager=auth_manager)

"""##### **Configuração da chave de acesso da LLM utilizada**"""

#Solicitar a API por parâmetro
api_key = getpass.getpass("Insira sua chave da API OpenAI: ")

#Armazenar a chave em uma variável de ambiente para usar diretamente com as bibliotecas
os.environ["OPENAI_API_KEY"] = api_key

"""# **Parte 2 - Extrair informações com a API do Spotify**
---

No tópico a seguir, iremos, principalmente, **realizar requisições nas APIs** para conseguir **extrair as informações** que utilizaremos como **base para a realização dos prompts** com a IA.

##### **Obtenção do input inicial do artista desejado**
"""

#Input inicial para informar o artista desejado
nome_artista = input("Digite o nome do artista que deseja usar como referência: ")
print(f"Nome do artista: {nome_artista}")

"""##### **Função para recuperar o identificador exclusivo do artista no Spotify**"""

#Função para buscar o identificador do artista no Spotify
def buscar_artista_id(nome_artista):
    #Fazer a requisição para localização do artista
    resultado = sp.search(q=nome_artista, type='artist')

    #Verificar se foi possível localizar o artista
    if resultado['artists']['items']:
        artista_id = resultado['artists']['items'][0]['id']
        artista_nome = resultado['artists']['items'][0]['name']

        return artista_id
    else:
        return None

#Armazenando as informações adquiridas
id_artista = buscar_artista_id(nome_artista)
artist_uri = f'spotify:artist:{id_artista}'
print(f"ID do artista: {id_artista}")

"""##### **Capturar o nome do álbum mais famoso do artista**


"""

#Função para buscar o nome do álbum mais famoso de um artista no Spotify usando o ID do artista
def nome_album_mais_famoso(sp, artista_id):
    # Obter todos os álbuns do artista
    albuns = sp.artist_albums(artista_id, album_type='album')['items']

    #Inicializar variáveis para armazenar o álbum mais famoso
    album_mais_famoso = None
    maior_popularidade = 0

    #Iterar sobre os álbuns para verificar sua popularidade
    for album in albuns:
        detalhes_album = sp.album(album['id'])
        popularidade = detalhes_album['popularity']

        #Atualizar se o álbum atual tiver maior popularidade
        if popularidade > maior_popularidade:
            maior_popularidade = popularidade
            album_mais_famoso = detalhes_album

    #Retorna o nome do álbum mais famoso
    return album_mais_famoso['name']

#Chama a função para obter o nome do álbum mais famoso e imprime o resultado
nome_album_mais_famoso = nome_album_mais_famoso(sp, id_artista)
print(nome_album_mais_famoso)

"""##### **Função para buscar o ID de um álbum**"""

#Função para buscar o ID de um álbum no Spotify pelo nome do álbum e opcionalmente pelo nome do artista
def buscar_album_id(sp, nome_album, nome_artista=None):
    query = f"album:{nome_album}"

    #Incluir o nome do artista na query, se fornecido
    if nome_artista:
        query += f" artist:{nome_artista}"

    resultados = sp.search(query, type='album', limit=1)

    #Verificar se algum álbum foi encontrado
    if resultados['albums']['items']:
        album = resultados['albums']['items'][0]
        album_id = album['id']
        album_nome = album['name']
        artista_nome = album['artists'][0]['name']

        return album_id
    else:
        print("Nenhum álbum encontrado.")
        return None

#Exemplo de uso: buscar o ID de um álbum
album_id = buscar_album_id(sp, nome_album_mais_famoso, nome_artista)
print(f"ID do álbum: {album_id}")

"""##### **Função para obter as faixas de um álbum**"""

#Função para obter as faixas de um álbum pelo ID do álbum
def album_mais_famoso_musicas(id_album_mais_famoso):
    musicas = sp.album_tracks(id_album_mais_famoso)['items']
    return musicas

#Obter as faixas do álbum mais famoso
album_mais_famoso_musicas = album_mais_famoso_musicas(album_id)

#Imprimir o nome de cada faixa
for i in album_mais_famoso_musicas:
    print(i['name'])

#Armazena os dados como uma lista
tracks_album_mais_famoso = [track['name'] for track in album_mais_famoso_musicas]

"""# **Parte 3 - Informações gerais do artista**
---

No tópico a seguir, realizaremos **análises adicionais** sobre o artista e o **álbum mais famoso**, incluindo a **obtenção de álbuns**, **músicas mais ouvidas**, **imagens** e **artistas relacionados**.

##### **Função para obter todos os álbuns do artista**
"""

#Função para obter todos os álbuns do artista, incluindo paginação
def albuns(artist_uri):
    #Obtém os álbuns do artista
    results = sp.artist_albums(artist_uri, album_type='album')
    albums = results['items']

    #Paginação para obter todos os álbuns
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])
        time.sleep(0.2)

    return albums

#Obtém e imprime todos os álbuns do artista
albuns = albuns(artist_uri)
for i in albuns:
  print(i['name'])

"""##### **Função para obter as músicas mais ouvidas do artista**"""

#Função para obter as músicas mais ouvidas do artista
def top10_tracks(artist_uri):
    # Obtém as músicas mais ouvidas do artista
    tracks = []
    response = sp.artist_top_tracks(artist_uri)
    for musica in response['tracks']:
      tracks.append(musica) # Adiciona a música à lista de faixas
    return tracks

#Obtém e imprime as 10 músicas mais ouvidas do artista
top_tracks = top10_tracks(id_artista)
for i in top_tracks:
  print(i['name'])

#Armazena os dados como uma lista
top_tracks_lista = [track['name'] for track in top_tracks]

"""##### **Função para obter a imagem do artista**


"""

#Função para obter a imagem do artista
def imagem(artist_uri):
    response = sp.artist(artist_uri)
    image_url_160 = next(image['url'] for image in response['images'] if image['width'] == 320)
    return image_url_160

#Obtém e armazena a URL da imagem do artista
imagem = imagem(id_artista)
print(imagem)

"""##### **Função para obter artistas relacionados**"""

#Função para obter artistas relacionados ao artista fornecido
def artistas_relacionados(id_artista):
  artistas_relacionados = sp.artist_related_artists(id_artista)
  nomes_artistas = [artista['name'] for artista in artistas_relacionados['artists']]
  return nomes_artistas

#Obtém e imprime os nomes dos artistas relacionados
artistas_relacionados = artistas_relacionados(id_artista)
print(artistas_relacionados)

"""# **Parte 4 - Utilização da API Lyrics.ovh**
---

Neste tópico, abordaremos como obter as letras das músicas utilizando a `API Lyrics.ovh`, já que, **infelizmente**, o Spotify  **NÃO fornece letras de músicas**.

##### **Função para obter a letra de uma música**
"""

#Função para extrair a letra de uma música usando a API Lyrics.ovh
def lyrics(nome_artista, nome_musica):
    url = f'https://api.lyrics.ovh/v1/{nome_artista}/{nome_musica}'

    #Fazendo a requisição para a API
    response = requests.get(url)
    letra = ''
    if response.status_code == 200:
        data = response.json()
        letra = data['lyrics']
    else:
        print(f"Erro na requisição. Código de status: {response.status_code}")
    return letra

#Teste para ver se a função funciona com a primeira música da lista de músicas mais ouvidas
print(lyrics(nome_artista, top_tracks_lista[2]))

"""##### **Função para salvar letras das músicas em um arquivo**
`POR SER MUITAS REQUISIÇÕES, ESSE CÓDIGO PODE DEMORAR ALGUNS MINUTOS PARA SER REALIZADO.`
"""

#Função para salvar letras das músicas em um arquivo de texto
def save_musics_database(nome_artista, tracks_lista, nome_arquivo):
    #Abrir o arquivo para escrita
    with open(f'{nome_arquivo}.txt', 'w', encoding='utf-8') as file:
        for musica in tracks_lista:
            letra = lyrics(nome_artista, musica)

            #Verifica se a letra não está vazia
            if letra:
                #Escreve a letra da música no arquivo
                file.write(f'Letra da música: {musica}\n')
                file.write(letra + '\n')
                #Adiciona uma linha separadora
                file.write('-' * 80 + '\n')

#Obtém e salva a letra das músicas do álbum mais famoso
letra_das_musicas_mais_famosas_do_album = save_musics_database(nome_artista, tracks_album_mais_famoso, "letra_das_musicas_mais_famosas_do_album")

#Obtém e salva a letra das músicas mais ouvidas
letra_musicas_mais_ouvidas = save_musics_database(nome_artista, top_tracks_lista, "letra_musicas_mais_ouvidas")

#Observação: Caso ocorram erros na requisição, isso indica que uma das letras da música não foi encontrada, mas o arquivo contém apenas os que foi possível baixar

"""# **Parte 5 - Integração prática com GPT-4o**
---

Nesta parte do projeto, o foco é a **integração prática com o nosso modelo de IA** para **gerar respostas** baseadas em **letras de músicas, analisar sentimentos, realizar traduções e recomendações para o usuário**. Em cada parte, iremos deixar explícito **qual a técnica de PLN que está sendo utilizada**. Além disso, em todos os códigos, nos baseamos em **langchain, engenharia de prompts e demais técnicas de processamento**.

##### **Definição do modelo padrão de IA a ser utilizado**
"""

#Definir o modelo padrão que será utilizado no projeto prático
modelo = ChatOpenAI(
    openai_api_key= api_key,     #Define a chave da API
    model="gpt-4o",              #Escolhe o modelo a ser utilizado
    temperature=0.7,             #Configura a temperatura da resposta
    n=1                          #Define o número de respostas que serão geradas
)

"""## **1) Sumarização e Geração de Textos:**
Uma introdução inicial do artista, resumindo seu lado artístico a partir de suas músicas mais ouvidas.

##### **Geração de texto sobre o gênero musical do artista**
"""

#Cria uma lista de mensagens a serem enviadas para o modelo de chat
mensagens = [
    SystemMessage(content=f"Based on the name of the artist {nome_artista} and its most listened {top_tracks}, answer the human message in Portuguese."),
    HumanMessage("Mention the musical genres the artist fits.")
]

#Envio das mensagens para o modelo e exibição da resposta
genero = modelo.invoke(mensagens)
print(genero.content)

"""##### **Realização de sumarização abstrativa para a introdução do artista**"""

#Criar uma lista de mensagens para auxiliar o modelo a gerar uma sumarização abstrativa do artista
mensagens = [
    SystemMessage(content=f"You are a music assistant specializing in summarizations. Perform an abstractive summarization. Answer in Portuguese."),
    HumanMessage(content=f"Make an introduction about the artist '{nome_artista}' explaining about his musical style based on the songs '{top_tracks}'.")
]

#Captura o resultado da sumarização abstrativa + geração de conteúdo.
introducao = modelo.invoke(mensagens)
print(introducao.content)

"""## **2) Extração de Documento e Sumarização de Textos**
Resumo abstrativo dado um conjunto de letras. A partir disso, tentar descrever os temas gerais abordados em suas músicas.

##### **Extrair as letras do arquivo e analisar seu conteúdo**
"""

#Caminho para o arquivo txt extraído contendo as letras das músicas mais ouvidas
caminho_arquivo = '/content/letra_musicas_mais_ouvidas.txt'

#Ler o conteúdo do arquivo capturado
with open(caminho_arquivo, 'r', encoding='utf-8') as file:
    conteudo = file.read()

#Através do conteúdo do arquivo, realizar uma análise da letra
mensagens = [
    SystemMessage(content="You are a song lyrics analyst. Make a abstractive summarization and try to explain why the artist is so famous. Answer in Portuguese"),
    HumanMessage(content=f"Analyze the lyrics: {conteudo}")
]

#Capturar a análise da letra gerada pela IA
analise_letra = modelo.invoke(mensagens)
print(analise_letra.content)

"""## **3) Extração e Detecção de Emoções**

##### **Obter as principais emoções de um texto do usuário para sugerir 10 músicas para uma playlist**
"""

#Definição do texto do usuário
texto_usuario = '''Hoje eu tive um dia bem cansativo, tanto na faculdade como no trabalho.
 Recebi a devolutiva de uma nota e fui pior do que esperava, e ainda no ambiente corporativo,
 recebi uma bronca do meu chefe. Gostaria agora apenas de deitar na minha cama e ouvir algumas músicas.
 '''

#Classe para recuperar apenas as informações relevantes do texto do usuário
class AnaliseSentimentoTexto(BaseModel):
  emocoes: str = Field(description="Quais as emoções mais presentes no texto?")
  forcaEmocoes: str = Field(description="Qual a força geral dessas emoções?", enum=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

#Criação de template de prompt para recuperar o sentimento
prompt = ChatPromptTemplate.from_template(
    """
    Extract only the properties mentioned in the class 'AnaliseSentimentoTexto'

    User text:
    {texto_usuario}
    """
)

#Configuração do modelo estruturado
modelo_estruturado = modelo.with_structured_output(AnaliseSentimentoTexto)

#Inicializa o segundo modelo com o template e as respostas estruturadas
chain = prompt | modelo_estruturado

retorno_estruturado = chain.invoke({"texto_usuario": texto_usuario})
emocoes = retorno_estruturado.emocoes
forcaEmocoes = retorno_estruturado.forcaEmocoes

prompt = ChatPromptTemplate.from_template(
    """
    Given the main emotions and its strengths from the user's text, and considering related artists to the main artist, suggest 10 songs for a playlist that matches the sentiment and strength.

    Emotions: {emocoes}
    Emotions Strength: {forcaEmocoes}
    Related Artists: {artistasRelacionados}

    Please provide only the list of 10 song suggestions with artist names.
    """
)

chain = prompt | modelo

recomendacoes = chain.invoke({"emocoes": emocoes, "forcaEmocoes": forcaEmocoes, "artistasRelacionados": artistas_relacionados})
print(recomendacoes.content)

"""### **Realizar gráfico de pizza com extração de emoções**

##### **Extrair as letras das músicas mais famosas do álbum para gerar um gráfico de pizza**
"""

#Caminho para o arquivo txt extraído contendo as letras das músicas do álbum mais famoso
caminho_arquivo = '/content/letra_das_musicas_mais_famosas_do_album.txt'

modelo_unico = ChatOpenAI(
    openai_api_key= api_key,
    model="gpt-4o",
    temperature=0,
    n=1
)

#Ler o conteúdo do arquivo capturado
with open(caminho_arquivo, 'r', encoding='utf-8') as file:
    conteudo = file.read()

#Solicitar para que a IA extraia as emoções das letras e gere um retorno em porcentagem, para montarmos um gráfico de pizza
mensagens = [
    SystemMessage(content="You are a lyric analyst. Name all the emotions present and try to do an analysis of the percentage of each emotion present in the album."),
    HumanMessage(content=f"{conteudo}. Return only the emotions and their percentages, NOTHING ELSE. Your output will be used to create a graph. Remove any markdown formatting from the text. Awnser in Portuguese.")
]

sentimentos = modelo_unico.invoke(mensagens)
print(sentimentos.content)

"""##### **Colocando as emoções e porcentagens em uma lista para montagem do gráfico**"""

#String fornecida
dados = sentimentos.content

#Remover aspas duplas
dados = dados.replace('"', '')

#Processar a string para extrair categorias e percentuais
categorias = []
percentuais = []

#Dividir a string em linhas
linhas = dados.strip().split('\n')

for linha in linhas:
    #Verificar se a linha contém um separador (:)
    if ':' in linha:
        #Separar a linha em categoria e percentual
        parte_categoria, parte_percentual = linha.split(':')
        categoria = parte_categoria.strip('- ').strip()
        percentual = parte_percentual.strip('% ').strip()

        #Adicionar os valores às listas
        categorias.append(categoria)
        percentuais.append(float(percentual))
    else:
        #Lidar com linhas que não contêm o separador
        print(f"Linha ignorada (sem separador): {linha}")

#Exibir as listas para verificação
print("Categorias:", categorias)
print("Percentuais:", percentuais)

"""##### **Montar o gráfico de pizza dos sentimentos com a biblioteca pandas**"""

#Processar a string para extrair categorias e percentuais
categorias = []
percentuais = []

#Dividir a string em linhas
linhas = dados.strip().split('\n')

for linha in linhas:
    #Separar a linha em categoria e percentual
    parte_categoria, parte_percentual = linha.split(':')
    categoria = parte_categoria.strip('- ').strip()
    percentual = parte_percentual.strip('% ').strip()

    #Adicionar os valores às listas
    categorias.append(categoria)
    percentuais.append(float(percentual))

#Criar um DataFrame com os dados
df = pd.DataFrame({
    'Emoção': categorias,
    'Percentual': percentuais
})

# Criar gráfico de pizza usando Altair
grafico_emocoes = alt.Chart(df).mark_arc().encode(
    theta=alt.Theta(field='Percentual', type='quantitative'),
    color=alt.Color(field='Emoção', type='nominal'),
    tooltip=['Emoção', 'Percentual']
).properties(
    title='Distribuição das Emoções',
    width=600,
    height=400
).interactive()

"""### **4) Extração de Palavras-Chave**
- Analisar o álbum mais famoso do artista, descrevendo os temas mais abordados, palavras-chave e seu impacto.

- A análise é feita em cima do arquivo.txt elaborado que armazena todas as letras desse álbum.

##### **Extrair as palavras chaves das músicas do álbum mais famoso do artista**
"""

#Caminho para o arquivo txt extraído contendo as letras das músicas do álbum mais famoso
caminho_arquivo = '/content/letra_das_musicas_mais_famosas_do_album.txt'

#Ler o conteúdo do arquivo capturado
with open(caminho_arquivo, 'r', encoding='utf-8') as file:
    conteudo = file.read()

#Definir a classe estruturada para retornar as palavras-chave das letras
class ExtracaoPalavrasChave(BaseModel):
    significadoLetra: str = Field(description="Quais os temas abordados no álbum?")
    palavra_chave: str = Field(description="Quais são as palavras-chave do álbum?")
    impactoCultural: str = Field(description="Qual o impacto cultural do álbum?")
    receitaGerada: str = Field(description="Qual foi a receita gerada pelo álbum?")

#Configuração do modelo estruturado
modelo_estruturado3 = modelo.with_structured_output(ExtracaoPalavrasChave)

#Criação do template de prompt para extrair apenas as propriedades da classe criada
prompt = ChatPromptTemplate.from_template(
    """
    You're a really prestative worker. You'll receive lyrics of the most listened album of an artist. By the lyrics, you'll have to describe what the album is about. Try to find a logic between the tracks. Mention key words .Answer the human message in Portuguese.Answer in markdown and separate the topics in the answer using Markdown.

    Extract only the properties mentioned in the class 'ExtracaoPalavrasChave'

    Content:
    {content}
    """
)

chain = prompt | modelo_estruturado3

retorno_estruturado = chain.invoke({"content": conteudo})

significadoLetra = retorno_estruturado.significadoLetra
impactoCultural = retorno_estruturado.impactoCultural
receitaGerada = retorno_estruturado.receitaGerada
palavra_chave = retorno_estruturado.palavra_chave

analise_album = ("Significado da letra: " + significadoLetra +"\n\nPalavras-Chave:"+ palavra_chave + "\n\nImpacto cultura do álbum: " + impactoCultural + "\n\nReceita gerada pelo álbum:" + receitaGerada)
print(analise_album)

"""## **5) Tradução de Textos**

### **Realizar a tradução de uma música especificada pelo usuário**

##### **Receber o nome do artista e da música**
`OBS: Precisa ser uma música do artista escolhido inicialmente para não dar erro.`
"""

#Definir a música desejada para a tradução
nome_musica = input("Digite o nome da música que deseja saber a tradução: ")
print(f"Nome da música: {nome_musica}")


#Definir a música desejada para a tradução
idioma_traducao = input("Digite o idioma que deseja a tradução: ")
print(f"Idioma escolhido: {idioma_traducao}")

"""##### **Criação de ferramenta (tool) para recuperar a lyrics desejada**"""

#Criação de ferramenta para recuperar a lyrics desejada para a tradução
@tool
def CapturarLyrics(nome_artista: str, nome_musica: str):
    """Captura a lyrics desejada dado o nome do artista e da música"""
    #Monta a URL da API com o nome do artista e da música
    url = f'https://api.lyrics.ovh/v1/{nome_artista}/{nome_musica}'

    #Fazendo a requisição para a API
    response = requests.get(url)
    letra = None
    #Verifica se a resposta da API foi bem-sucedida
    if response.status_code == 200:
        #Caso bem-sucedida, extrai a letra da resposta JSON
        data = response.json()
        letra = data['lyrics']
    else:
        #Em caso de erro, imprime o código de status da requisição
        print(f"Erro na requisição. Código de status: {response.status_code}")
    return letra

"""##### **Realizar a requisição da tool para captura da letra desejada e o idioma da música**"""

#Definir a calsse estruturada para retornar o idioma em que o texto está escrito
class IdiomaLyricsDesejada(BaseModel):
    idioma: str = Field(description="O idioma em que o texto está escrito")

#Configuração do modelo estruturado
modelo_estruturado2 = modelo.with_structured_output(IdiomaLyricsDesejada)

#Criação do template de prompt para extrair apenas as propriedades da classe criada
prompt = ChatPromptTemplate.from_template(
    """
    Extract only the properties mentioned in the class 'IdiomaLyricsDesejada'

    Lyrcs:
    {lyrics}
    """
)

chain = prompt | modelo_estruturado2

lyrics = CapturarLyrics.invoke({"nome_artista": nome_artista, "nome_musica": nome_musica})

if lyrics:
    retorno_estruturado = chain.invoke({"lyrics": lyrics})
    idiomaOriginal = retorno_estruturado.idioma
else:
    print("Não foi possível recuperar a letra da música.")

"""##### **Realizar a tradução da letra**"""

#Definição das mensagens para tradução da letra
mensagens = [
    # Mensagem de sistema que configura o comportamento da IA
    SystemMessage(content="You are a really prestative worker. You will receive the lyrics of a song, the language it is in and which language the translation was desired for. Answer with the translated lyrics. If the lyrics is already in the desired language, show the original lyrics."),

    #Mensagem humana que solicita a tradução das letras
    HumanMessage(content=f"Translate the lyrics from {idiomaOriginal} to {idioma_traducao}. Consider the following song lyrics: {lyrics}")
]

lyrics_traduzida = modelo.invoke(mensagens)
print(lyrics_traduzida.content)

"""## **6) Sistema de Perguntas e Respostas**

##### **Solicitação da pergunta do usuário**
"""

#Defina a pergunta a ser realizada
pergunta = input("Qual dúvida você possui sobre a letra da música/artista?")
print(f"Pergunta: {pergunta}")

"""##### **Criação de template para resposta da pergunta realizada pelo usuário**"""

# Criação de template de prompt para as perguntas
prompt = ChatPromptTemplate.from_template(
    """
    Answer the following question, given its lyrics, the name of the artist and the name of the song. Be succinct in your answer. Answer in Portuguese.

    Letra da Música: {lyrics}
    Nome do artista: {nomeArtista}
    Nome da música: {nomeMusica}
    Pergunta: {pergunta}
    """
)

chain = prompt | modelo

#Para cada pergunta, o modelo é invocado, gerando uma resposta com base na letra
resposta = chain.invoke({"lyrics": lyrics, "nomeArtista": nome_artista, "nomeMusica": nome_musica, "pergunta": pergunta})

#Exibe a pergunta e a resposta gerada
print("Pergunta: " + pergunta + "\n" + "Resposta: " + resposta.content)

"""# **Parte 6 - Apresentação dos dados no streamlit**
---

Nesta parte do projeto, o foco é a **exibição dos dados no Streamlit**, permitindo uma **visualização interativa e acessível** das informações processadas.
A cada etapa, **explicamos claramente como os dados foram organizados** e apresentados, **utilizando componentes do Streamlit** para criar uma **interface amigável**.

##### **Definição de informações gerais do artista para montagem da interface**
"""

#Obtém informações sobre o artista e extrai dados importantes
artista_info = sp.artist(id_artista)
followers = artista_info['followers']['total']  #Número total de seguidores
genres = artista_info['genres']  # Gêneros musicais
popularity = artista_info['popularity']  #Popularidade do artista

#Exibe as informações do artista
print(f"Artista: {nome_artista}")
print(f"Seguidores: {followers}")
print(f"Gêneros: {', '.join(genres)}")
print(f"Popularidade: {popularity}")

"""##### **Montagem de gráfico de barra para a exibição**"""

# Função para extrair nomes das músicas
def musicas_eixoy(top_tracks):
  track_names = [track['name'] for track in top_tracks]# Extrai os nomes das músicas
  return track_names

# Função para extrair a popularidade das músicas
def popularidade_eixoy(top_tracks):
  popularidade = [track['popularity'] for track in top_tracks]# Extrai a popularidade das músicas
  return popularidade

musicas_eixoy = musicas_eixoy(top_tracks)
popularidade_eixox = popularidade_eixoy(top_tracks)

# Criar um DataFrame com os dados
df = pd.DataFrame({
    'Música': musicas_eixoy,
    'Popularidade': popularidade_eixox
})

# Criar gráfico usando Altair
grafico_popularidade = alt.Chart(df).mark_bar().encode(
    x='Popularidade:Q',# Eixo X com a popularidade
    y=alt.Y('Música:N', sort='-x'),# Eixo Y com as músicas, ordenado pela popularidade
    tooltip=['Música', 'Popularidade']# Exibe o nome da música e a popularidade ao passar o mouse
).properties(
    title='Popularidade das músicas',
    width=600,
    height=400
).interactive()

#Suponha que essas variáveis já estejam definidas
import pickle

dados = {
    "artista_favorito": nome_artista,
    "albuns" : albuns,
    "top_tracks": top_tracks,
    "artistas_relacionados": artistas_relacionados,
    "imagem": imagem,
    "recomendacoes": recomendacoes.content,
    "sentimentos": sentimentos.content,
    "analise_album" : analise_album,
    "introducao": introducao.content,
    "genero": genero.content,
    "analise_letra": analise_letra.content,
    "grafico_popularidade": grafico_popularidade,
    "grafico_emocoes": grafico_emocoes,
    "followers": followers,
    "genres": genres,
    "popularity": popularity,
    "idiomaOriginal": idiomaOriginal,
    "idiomaTraducao": idioma_traducao,
    "nomeMusica": nome_musica,
    "lyricsOriginal": lyrics,
    "lyricsTraduzida": lyrics_traduzida.content,
    "pergunta": pergunta,
    "resposta": resposta.content
}

with open('dados_musica.pkl', 'wb') as f:
    pickle.dump(dados, f)

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# import pickle
# import streamlit as st
# import altair as alt
# import pandas as pd
# 
# #Carregar os dados salvos
# with open('dados_musica.pkl', 'rb') as f:
#     dados = pickle.load(f)
# 
# 
# # Atribuir as variáveis
# artista_favorito = dados["artista_favorito"]
# top_tracks = dados["top_tracks"]
# artistas_relacionados = dados["artistas_relacionados"]
# recomendacoes = dados["recomendacoes"]
# sentimentos = dados["sentimentos"]
# genero = dados["genero"]
# introducao = dados["introducao"]
# imagem = dados["imagem"]
# analise_letra = dados["analise_letra"]
# grafico_popularidade = dados["grafico_popularidade"]
# grafico_emocoes = dados["grafico_emocoes"]
# followers = dados["followers"]
# genres = dados["genres"]
# popularity = dados["popularity"]
# albuns = dados["albuns"]
# analise_album = dados["analise_album"]
# idiomaOriginal = dados["idiomaOriginal"]
# idiomaTraducao = dados["idiomaTraducao"]
# nomeMusica = dados["nomeMusica"]
# lyricsOriginal = dados["lyricsOriginal"]
# lyricsTraduzida = dados["lyricsTraduzida"]
# lyricsTraduzida = dados["lyricsTraduzida"]
# pergunta = dados["pergunta"]
# resposta = dados["resposta"]
# 
# 
# 
# # Função principal para a interface
# def main():
#     st.sidebar.title("Seu artista favorito!")
# 
#     # Criar abas
#     tab1, tab2,tab3,tab4 = st.tabs(["Dados do artista", "Analisando a musicalidade","Análise do album mais famoso", "Tradução da letra"])
# 
#     # Conteúdo da primeira aba (Dados do artista)
#     with tab1:
#         st.header(f"{artista_favorito}")
#         if imagem:
#             st.image(imagem, caption=f"Imagem de {artista_favorito}", width=320)
#         st.write(f"**Seguidores:** {followers}")
#         st.write(f"**Gêneros:** {', '.join(genres)}")
#         st.write(f"**Popularidade:** {popularity}")
#         st.header("Quem é?")
#         st.write(f"{introducao}")
#         st.header("Estilo musical")
#         st.write(f"{genero}")
# 
#         st.header("Álbuns")
#         # Mostrar os álbuns em fileiras horizontais
# 
#         num_cols = 3  # Define quantos álbuns por linha
#         for i in range(0, len(albuns), num_cols):
#             cols = st.columns(num_cols)
#             for idx, col in enumerate(cols):
#                 if i + idx < len(albuns):
#                     album = albuns[i + idx]
#                     col.write(album['name'])
#                     if album['images']:
#                         for img in album['images']:
#                             if img['height'] == 300 and img['width'] == 300:
#                                 col.image(img['url'], caption=f"Imagem de {album['name']}", width=150)
# 
#         st.header("Artistas relacionados")
#         for artista in artistas_relacionados:
#             st.write(artista)
# 
# 
# 
#     # Conteúdo da segunda aba (Analisando a musicalidade)
#     with tab2:
#         st.header("Músicas mais populares/ouvidas na plataforma")
# 
#         st.altair_chart(grafico_popularidade, use_container_width=True)
# 
#         st.header("Músicas mais ouvidas no momento!")
#         for track in top_tracks:
#             st.write(f"{track['name']}")
# 
#         st.header("Escute músicas na mesma pegada!")
#         st.write(recomendacoes)
# 
#         st.write(analise_letra)
# 
# 
#     # Conteúdo da terceira aba (Analisando o álbum mais famoso)
#     with tab3:
#       st.header("Emoções do álbum mais famoso")
#       st.altair_chart(grafico_emocoes, use_container_width=True)
# 
#       st.header("Análise do álbum mais famoso")
#       st.write(analise_album)
# 
#     # Conteúdo da quarta (Tradução de uma música)
#     with tab4:
#       st.header("Tradução da música")
#       st.write (f"Nome da música: {nomeMusica}")
#       st.write (f"Nome do artista: {artista_favorito}")
#       st.write (f"Idioma original: {idiomaOriginal}")
#       st.write (f"Idioma tradução: {idiomaTraducao}")
# 
# 
#       st.header("Letra no idioma original: " + idiomaOriginal)
#       st.write (lyricsOriginal)
#       st.header("Letra no idioma traduzido: " + idiomaTraducao)
#       st.write(lyricsTraduzida)
# 
#       st.header("Pergunta sobre a música!")
#       st.write("**Pergunta**: " + pergunta)
#       st.write("**Resposta**: " + resposta)
# 
# if __name__ == "__main__":
#     main()

"""# **Parte 7 - Resultado final!**
---

##### **Agora, basta executar o seguinte bloco de código a seguir para ter acesso à página montada do Streamlit contendo todas as informações geradas pela IA e com a utilização dos métodos práticos de PLN! Divirta-se!**
"""

!npm install localtunnel

"""**- Acesse o link abaixo e insira o IP fornecido para acessar a interface**"""

!streamlit run app.py &>/content/logs.txt &
!npx localtunnel --port 8501 & curl ipv4.icanhazip.com
