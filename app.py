import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.colors import make_colorscale
import base64
from pathlib import Path

# Import des pages (le dossier 'modules')
from modules.marche_temps_reel import afficher_marche_temps_reel
from modules.recherche_predict_actions import afficher_recherche_actions
from modules.comparaison_actions import afficher_comparaison_actions
from modules.alertes_personnalisees import afficher_alertes_personnalisees
from utils.data_fetcher import obtenir_donnees_indice
from modules.actualites_financieres import afficher_actualites_financieres
from modules.cryptomonnaies import afficher_cryptomonnaies
from modules.indicateurs_pays import afficher_indicateurs_pays

    
# Configuration globale de la page
st.set_page_config(
    page_title="B&B Finance",
    page_icon="./assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Suppression des éléments de navigation par défaut de Streamlit via CSS
st.markdown(
    """
    <style>
    /* Masquer le header et le footer */
    header, footer {visibility: hidden;}
    /* Supprimer l'espace en haut de la page */
    .block-container {padding-top: 0rem;}
    </style>
    """,
    unsafe_allow_html=True
)


# Fonction pour afficher le logo
def afficher_logo():
    # Fonction pour convertire image, icon, gif en base 64 pour streamlit cloud
    def get_base64(file_path):
        with open(file_path, "rb") as file:
            data = file.read()
        return base64.b64encode(data).decode()
    
    # Logo :
    logo_path = Path("./assets/logo.png")
    logo_base64 = get_base64(logo_path)
    
    gif_path = Path("./assets/etoile.gif")
    gif_base64 = get_base64(gif_path)
    
    st.sidebar.markdown(
            f"""
            <style>
            .custom-header {{
                position: relative;
                width: 100%;
                height: 200px; /* Ajustez la hauteur selon vos besoins */
                display: flex;
                align-items: center;
                justify-content: center;
                background-image: url("data:image/gif;base64,{gif_base64}");
                background-size: cover; /* Adapte la taille du GIF au conteneur */
                background-repeat: no-repeat;
                background-position: center;
            }}
            .custom-header img {{
                position: relative;
                z-index: 10; /* S'assure que le logo reste au-dessus du GIF */
                height: 150px; /* Ajustez la taille du logo */
            }}
            </style>
            <div class="custom-header">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo">
            </div>
            """,
            unsafe_allow_html=True
        )



# Fonction pour afficher le contenu de la barre latérale
def afficher_sidebar():

    #Logo du site
    afficher_logo()
    
    # Navigation entre les pages
    menu = ["Accueil", "Marchés en temps réel", "Recherche et prédiction d'actions", "Comparaison d'actions", "Alertes personnalisées", "Actualités financières", "Cryptomonnaies", "Indicateurs par Pays"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Accueil":
        afficher_accueil()
    elif choice == "Marchés en temps réel":
        afficher_marche_temps_reel()
    elif choice == "Recherche et prédiction d'actions":
        afficher_recherche_actions()
    elif choice == "Comparaison d'actions":
        afficher_comparaison_actions()
    elif choice == "Alertes personnalisées":
        afficher_alertes_personnalisees()
    elif choice == "Actualités financières":
        afficher_actualites_financieres()
    elif choice == "Cryptomonnaies":
        afficher_cryptomonnaies()
    elif choice == "Indicateurs par Pays":
        afficher_indicateurs_pays()

    # Pied de page
    st.sidebar.markdown("---")
    st.sidebar.markdown("## À propos")
    st.sidebar.markdown("""
    Cette application vous permet de :
    - Suivre les marchés financiers en temps réel.
    - Rechercher et comparer des actions et leur prédiction.
    - Recevoir des alertes personnalisées.
    - Consulter les actualités financières.
    - Explorer les cryptomonnaies.
    - Visualiser les indicateurs économiques par pays.
    """)

    # Contact
    st.sidebar.markdown("## Contact")
    st.sidebar.markdown("""
    💼 **Développé par** : """)
    st.sidebar.markdown("""*BELKHITER & BREILLAD*""")

    st.sidebar.markdown(""" 📧 **Email** : """)
    st.sidebar.markdown("""
    [mehdi.belkhiter9@gmail.com](mailto:votre.email@example.com)
    [mbreillad@gmail.com](mailto:votre.email@example.com)
        
    """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2024 B&B Finance. Tous droits réservés.")

# Page d'accueil
def afficher_accueil():
    
    st.markdown("<h1 style='text-align: center; color: #DAA520; font-size:80px'>B&B Finance</h1>", unsafe_allow_html=True)

    # Texte de bienvenue
    st.markdown("<p style='text-align: center; color: #DAA520; font-size:20px'>Bienvenue sur notre application de visualisation des données financières</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:18px;'>Explorez les marchés financiers avec des outils interactifs et des données en temps réel.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #444;'>", unsafe_allow_html=True)

    # Liste des indices majeurs pour le tableau de bord
    indices = {
        "Dow Jones": "^DJI",
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "CAC 40": "^FCHI",
        "DAX": "^GDAXI",
        "FTSE 100": "^FTSE"
    }

    # Conteneurs de mise en page
    col1, col2 = st.columns(2)

    # Colonne 1 : Tableau des indices clés
    with col1:
        st.markdown("### 📈 Marchés Clés en Temps Réel")
        data = []
        for nom, symbole in indices.items():
            prix, variation = obtenir_donnees_indice(symbole)
            if prix is not None and variation is not None:
                direction = "🔼" if variation > 0 else "🔽"
                data.append([nom, prix, f"{variation:.2f}% {direction}"])
            else:
                data.append([nom, "N/A", "⚪"])
        df_indices = pd.DataFrame(data, columns=["Indice", "Prix Actuel", "Variation"])
        st.table(df_indices)

    # Colonne 2 : Graphique de synthèse
    with col2:
        st.markdown("### 📊 Tendance des Marchés")
        fig = go.Figure()
        for nom, symbole in indices.items():
            ticker = yf.Ticker(symbole)
            historique = ticker.history(period="1y")
            if not historique.empty:
                fig.add_trace(go.Scatter(
                    x=historique.index,
                    y=historique["Close"],
                    mode='lines',
                    name=nom
                ))

        fig.update_layout(
            title="Indices Majeurs depuis le début de l'année",
            xaxis_title="Date",
            yaxis_title="Prix de Clôture",
            template="plotly_dark",
            legend_title="Indices",
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            font=dict(color='#e6e6e6'),
            title_font=dict(color='#DAA520')
        )
        st.plotly_chart(fig, use_container_width=True)

    # Graphique des performances
    st.markdown("### 📌 Performances des Indices")
    fig_bar = go.Figure()

    for nom, symbole in indices.items():
        prix, variation = obtenir_donnees_indice(symbole)
        if prix is not None and variation is not None:
            if variation > 0:
                couleur = f"rgba(62, 225, 68, {abs(variation)})"
            else:
                couleur = f"rgba(225, 68, 68, {abs(variation)})"
            fig_bar.add_trace(go.Bar(
                x=[nom],
                y=[variation],
                marker_color=couleur,
                text=f"{variation:.2f}%",
                textposition="auto",
                name=nom
            ))

    fig_bar.update_layout(
        title="Variation des Indices pendant les 5 derniers jours (%)",
        xaxis_title="Indices",
        yaxis_title="Variation (%)",
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        font=dict(color='#e6e6e6'),
        title_font=dict(color='#DAA520')
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Fonction principale
def main():
    
    # Afficher le contenu de la barre latérale
    afficher_sidebar()
    

if __name__ == "__main__":
    main()