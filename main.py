import json
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup
import streamlit as st


# Fonction pour récupérer les paramètres de décodage
def get_decoding_params(gn_art_id):
    response = requests.get(f"https://news.google.com/rss/articles/{gn_art_id}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    div = soup.select_one("c-wiz > div")
    return {
        "signature": div.get("data-n-a-sg"),
        "timestamp": div.get("data-n-a-ts"),
        "gn_art_id": gn_art_id,
    }


# Fonction pour décoder les URLs
def decode_urls(articles):
    articles_reqs = [
        [
            "Fbv4je",
            f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{art["gn_art_id"]}",{art["timestamp"]},"{art["signature"]}"]',
        ]
        for art in articles
    ]
    payload = f"f.req={quote(json.dumps([articles_reqs]))}"
    headers = {"content-type": "application/x-www-form-urlencoded;charset=UTF-8"}
    response = requests.post(
        url="https://news.google.com/_/DotsSplashUi/data/batchexecute",
        headers=headers,
        data=payload,
    )
    response.raise_for_status()
    return [json.loads(res[2])[1] for res in json.loads(response.text.split("\n\n")[1])[:-2]]


# Interface Streamlit
st.title("Décodage d'URLs Google News")

# Entrée des URLs dans une zone de texte
urls_input = st.text_area(
    "Entrez les URLs encodées (une par ligne) :",
    placeholder="Exemple : https://news.google.com/rss/articles/CBMi..."
)

if st.button("Décoder les URLs"):
    if urls_input.strip():
        # Transformation des URLs en liste
        encoded_urls = [line.strip() for line in urls_input.split("\n") if line.strip()]

        try:
            # Extraction des paramètres pour chaque URL
            articles_params = [
                get_decoding_params(urlparse(url).path.split("/")[-1])
                for url in encoded_urls
            ]
            # Décodage des URLs
            decoded_urls = decode_urls(articles_params)

            # Affichage des résultats
            st.success("Voici les URLs décodées :")
            for url in decoded_urls:
                st.write(url)

        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
    else:
        st.warning("Veuillez entrer au moins une URL.")