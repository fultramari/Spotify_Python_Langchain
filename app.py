import pickle
import streamlit as st
import altair as alt
import pandas as pd

#Carregar os dados salvos
with open('dados_musica.pkl', 'rb') as f:
    dados = pickle.load(f)


# Atribuir as variáveis
artista_favorito = dados["artista_favorito"]
top_tracks = dados["top_tracks"]
artistas_relacionados = dados["artistas_relacionados"]
recomendacoes = dados["recomendacoes"]
sentimentos = dados["sentimentos"]
genero = dados["genero"]
introducao = dados["introducao"]
imagem = dados["imagem"]
analise_letra = dados["analise_letra"]
grafico_popularidade = dados["grafico_popularidade"]
grafico_emocoes = dados["grafico_emocoes"]
followers = dados["followers"]
genres = dados["genres"]
popularity = dados["popularity"]
albuns = dados["albuns"]
analise_album = dados["analise_album"]
idiomaOriginal = dados["idiomaOriginal"]
idiomaTraducao = dados["idiomaTraducao"]
nomeMusica = dados["nomeMusica"]
lyricsOriginal = dados["lyricsOriginal"]
lyricsTraduzida = dados["lyricsTraduzida"]
lyricsTraduzida = dados["lyricsTraduzida"]
pergunta = dados["pergunta"]
resposta = dados["resposta"]



# Função principal para a interface
def main():
    st.sidebar.title("Seu artista favorito!")

    # Criar abas
    tab1, tab2,tab3,tab4 = st.tabs(["Dados do artista", "Analisando a musicalidade","Análise do album mais famoso", "Tradução da letra"])

    # Conteúdo da primeira aba (Dados do artista)
    with tab1:
        st.header(f"{artista_favorito}")
        if imagem:
            st.image(imagem, caption=f"Imagem de {artista_favorito}", width=320)
        st.write(f"**Seguidores:** {followers}")
        st.write(f"**Gêneros:** {', '.join(genres)}")
        st.write(f"**Popularidade:** {popularity}")
        st.header("Quem é?")
        st.write(f"{introducao}")
        st.header("Estilo musical")
        st.write(f"{genero}")

        st.header("Álbuns")
        # Mostrar os álbuns em fileiras horizontais

        num_cols = 3  # Define quantos álbuns por linha
        for i in range(0, len(albuns), num_cols):
            cols = st.columns(num_cols)
            for idx, col in enumerate(cols):
                if i + idx < len(albuns):
                    album = albuns[i + idx]
                    col.write(album['name'])
                    if album['images']:
                        for img in album['images']:
                            if img['height'] == 300 and img['width'] == 300:
                                col.image(img['url'], caption=f"Imagem de {album['name']}", width=150)

        st.header("Artistas relacionados")
        for artista in artistas_relacionados:
            st.write(artista)



    # Conteúdo da segunda aba (Analisando a musicalidade)
    with tab2:
        st.header("Músicas mais populares/ouvidas na plataforma")

        st.altair_chart(grafico_popularidade, use_container_width=True)

        st.header("Músicas mais ouvidas no momento!")
        for track in top_tracks:
            st.write(f"{track['name']}")

        st.header("Escute músicas na mesma pegada!")
        st.write(recomendacoes)

        st.write(analise_letra)


    # Conteúdo da terceira aba (Analisando o álbum mais famoso)
    with tab3:
      st.header("Emoções do álbum mais famoso")
      st.altair_chart(grafico_emocoes, use_container_width=True)

      st.header("Análise do álbum mais famoso")
      st.write(analise_album)

    # Conteúdo da quarta (Tradução de uma música)
    with tab4:
      st.header("Tradução da música")
      st.write (f"Nome da música: {nomeMusica}")
      st.write (f"Nome do artista: {artista_favorito}")
      st.write (f"Idioma original: {idiomaOriginal}")
      st.write (f"Idioma tradução: {idiomaTraducao}")


      st.header("Letra no idioma original: " + idiomaOriginal)
      st.write (lyricsOriginal)
      st.header("Letra no idioma traduzido: " + idiomaTraducao)
      st.write(lyricsTraduzida)

      st.header("Pergunta sobre a música!")
      st.write("**Pergunta**: " + pergunta)
      st.write("**Resposta**: " + resposta)

if __name__ == "__main__":
    main()
