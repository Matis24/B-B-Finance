import streamlit as st
import pandas as pd
import time
import random 
from streamlit_autorefresh import st_autorefresh

def afficher_marche_temps_reel():
    st.markdown("<h1 style='text-align: center; color: #DAA520; font-size:80px'>B&B Finance</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #444;'>", unsafe_allow_html=True)
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

    data = []
    for nom, symbole in indices.items():
        try:
            # Utiliser des données aléatoires pour le test
            prix = round(random.uniform(100, 200), 2)
            variation = round(random.uniform(-5, 5), 2)
            variation_str = f"{variation:.2f}%"
            data.append([nom, prix, variation_str])

        except Exception as e:
            st.warning(f"Erreur pour {nom} ({symbole}) : {str(e)}")
            data.append([nom, "N/A", "N/A"])

    df = pd.DataFrame(data, columns=["Indice", "Prix Actuel", "Variation (%)"])

    # Appliquer le style à la colonne Variation (%) uniquement
    def highlight_variation(val):
        try:
            val_float = float(val.strip('%'))
            if val_float > 0:
                color = 'green' 
                icon = '🔼'
            elif val_float < 0:
                color = 'red' 
                icon = '🔽'
            else:
                color = 'grey'
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