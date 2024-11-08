# Python + OPENAI + APISPOTIFY + STREAMLIT : Processamento de linguagem natural

Link de acesso : https://spotify-python-langchain.streamlit.app/

* Aplicando conceitos de engenharia de prompt utilizando **LANGCHAIN** para montagem de uma interface sobre o artista do spotify favorito do usuário. 💻
* Linguagem de programação : Python
* API: Spotify 🎧
* LLM: OpenAI 🤖

# Observações
### Arquivos "2024_2_pln_projeto_prático_análise_de_músicas_e_artistas_api_spotify_&_lyrics_ovh.py" e "Código_explicado" :
* possuem o mesmo conteúdo, contudo, um está formatado em um notebook colab, de modo que a leitura do código seja facilitada. Ambos explicam como foram feitas as extrações de informações utilizando a API do spotify + API lyrics , além de como foi feita a engenharia de prompts para gerar conteúdo com o GPT-4o.
  
### dados_musica.pkl:
*  Após as requisições feitas nas API's e as respostas geradas pelo GPT4, as informações armazenadas pelas variáveis foi salva em um arquivo de leitura *pkl*, para serem lidos e exibidos na interface streamlit

### requirements.txt:
* Arquivo que lista as dependências e suas versões para o devido funcionamento da interface.
  
### **app.py** : 
* Finalmente, o arquivo que exibe todas as informações obtidas no StreamLit. No código , a exibição da interface é feita através do localtunnel. Contudo, pela plataforma do streamlit, o exemplo feito com o artista Bruno Mars está disponível para pronto acesso.
