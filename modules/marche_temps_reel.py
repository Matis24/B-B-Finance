import streamlit as st
import pandas as pd
import time
import random  # Pour générer des données aléatoires
# from utils.data_fetcher import obtenir_donnees_indice  # Réactivez cette ligne pour utiliser les données réelles
from streamlit_autorefresh import st_autorefresh

def afficher_marche_temps_reel():
    st.title("📈 Marchés en Temps Réel")
    st.markdown("### Visualisez les variations des principaux indices boursiers en temps réel.")

    # Liste des indices boursiers
    indices = {
        "Dow Jones": "^DJI",
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "CAC 40": "^FCHI",
        "DAX": "^GDAXI",
        "FTSE 100": "^FTSE",
        "Nikkei 225": "^N225",
        "Hang Seng": "^HSI",
        "Apple": "AAPL"
    }

    # Sélection de l'intervalle de rafraîchissement
    refresh_rate = st.sidebar.slider("Intervalle de rafraîchissement (secondes)", 5, 60, 5, key="refresh_rate")

    # Bouton pour démarrer/arrêter la mise à jour en temps réel
    if 'start' not in st.session_state:
        st.session_state['start'] = True

    start = st.sidebar.checkbox("Démarrer la mise à jour en temps réel", value=st.session_state['start'], key="start_checkbox")
    st.session_state['start'] = start

    # Si la mise à jour en temps réel est activée, rafraîchir la page automatiquement
    if start:
        st_autorefresh(interval=refresh_rate * 1000, key="data_refresh")
        # Le nombre de rafraîchissements est masqué en supprimant la ligne suivante
        # count = st_autorefresh(interval=refresh_rate * 1000, key="data_refresh")
        # st.write(f"Rafraîchissement numéro : {count}")

    data = []
    for nom, symbole in indices.items():
        try:
            # Utiliser des données aléatoires pour le test
            prix = round(random.uniform(100, 200), 2)
            variation = round(random.uniform(-5, 5), 2)
            variation_str = f"{variation:.2f}%"
            data.append([nom, prix, variation_str])

            # Si vous souhaitez utiliser les données réelles, décommentez les lignes suivantes et commentez les lignes ci-dessus
            # prix, variation = obtenir_donnees_indice(symbole)
            # if prix is not None and variation is not None:
            #     variation_str = f"{variation:.2f}%"
            #     data.append([nom, prix, variation_str])
            # else:
            #     data.append([nom, "N/A", "N/A"])

        except Exception as e:
            st.warning(f"Erreur pour {nom} ({symbole}) : {str(e)}")
            data.append([nom, "N/A", "N/A"])

    # Créer un DataFrame
    df = pd.DataFrame(data, columns=["Indice", "Prix Actuel", "Variation (%)"])

    # Appliquer le style à la colonne Variation (%) uniquement
    def highlight_variation(val):
        try:
            val_float = float(val.strip('%'))
            if val_float > 0:
                color = 'green'  # Vert
                icon = '🔼'
            elif val_float < 0:
                color = 'red'  # Rouge
                icon = '🔽'
            else:
                color = 'grey'  # Gris
                icon = ''
            return f'color: {color}; font-weight: bold;', icon
        except:
            return 'color: grey;', ''

    # Appliquer le style et ajouter les icônes
    df['Direction'] = ''
    for index, row in df.iterrows():
        style, icon = highlight_variation(row['Variation (%)'])
        df.at[index, 'Direction'] = icon
        df.at[index, 'Variation (%)'] = f"<span style='{style}'>{row['Variation (%)']}</span>"

    # Afficher le tableau avec styles
    st.markdown(
        df[['Indice', 'Prix Actuel', 'Variation (%)', 'Direction']].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    # Afficher l'heure de la dernière mise à jour
    st.markdown(f"**Dernière mise à jour :** {time.strftime('%H:%M:%S')}")

    if not start:
        st.info("La mise à jour en temps réel est arrêtée. Cochez la case dans la barre latérale pour la démarrer.")