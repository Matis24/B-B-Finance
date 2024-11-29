import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import base64

# Import des pages (le dossier 'modules')
from modules.marche_temps_reel import afficher_marche_temps_reel
from modules.recherche_actions import afficher_recherche_actions
from modules.comparaison_actions import afficher_comparaison_actions
from modules.alertes_personnalisees import afficher_alertes_personnalisees
from utils.data_fetcher import obtenir_donnees_indice
from modules.actualites_financieres import afficher_actualites_financieres
from modules.cryptomonnaies import afficher_cryptomonnaies
from modules.indicateurs_pays import afficher_indicateurs_pays

# Configuration globale de la page
st.set_page_config(
    page_title="Application Financière",
    page_icon="💹",
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

# Fonction pour afficher le logo et le titre
def afficher_logo():
    # Lecture et encodage de l'image en base64
    with open("assets/logo.png", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .custom-header {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 10px 20px;
            background-color: #0e1117;
            margin-bottom: 20px;
        }}
        .custom-header img {{
            height: 50px;
            margin-right: 10px;
        }}
        .custom-header .title {{
            font-size: 22px;
            color: #DAA520;
            font-weight: bold;
        }}
        </style>
        <div class="custom-header">
            <img src="data:image/png;base64,{encoded_image}" alt="Logo">
            <div class="title">Application Financière</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Fonction pour afficher le contenu de la barre latérale
def afficher_sidebar():
    # Logo dans la barre latérale (optionnel)
    # with st.sidebar:
    #     st.image("assets/logo.png", use_column_width=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## À propos")
    st.sidebar.markdown("""
    Cette application vous permet de :
    - Suivre les marchés financiers en temps réel.
    - Rechercher et comparer des actions.
    - Recevoir des alertes personnalisées.
    - Consulter les actualités financières.
    - Explorer les cryptomonnaies.
    - Visualiser les indicateurs économiques par pays.
    """)

    st.sidebar.markdown("## Contact")
    st.sidebar.markdown("""
    💼 **Développé par** : *BELKHITER*

    📧 **Email** : [mehdi.belkhiter9@gmail.com](mailto:votre.email@example.com)
        
        """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2024 Application Financière")

# Page d'accueil
def afficher_accueil():
    # Afficher l'en-tête avec logo
    afficher_logo()

    # Texte de bienvenue
    st.markdown("<h1 style='text-align: center; color: #DAA520;'>Bienvenue sur notre application de visualisation des données financières</h1>", unsafe_allow_html=True)
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
            historique = ticker.history(period="5d")
            if not historique.empty:
                fig.add_trace(go.Scatter(
                    x=historique.index,
                    y=historique["Close"],
                    mode='lines',
                    name=nom
                ))

        fig.update_layout(
            title="Indices Majeurs sur les 5 Derniers Jours",
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
            couleur = "#3ee144" if variation > 0 else "#e14444"
            fig_bar.add_trace(go.Bar(
                x=[nom],
                y=[variation],
                marker_color=couleur,
                text=f"{variation:.2f}%",
                textposition="auto",
                name=nom
            ))

    fig_bar.update_layout(
        title="Variation des Indices (%)",
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

    # Menu déroulant dans la barre latérale
    menu = ["Accueil", "Marchés en temps réel", "Recherche d'actions", "Comparaison d'actions", "Alertes personnalisées", "Actualités financières", "Cryptomonnaies", "Indicateurs par Pays"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Navigation entre les pages
    if choice == "Accueil":
        afficher_accueil()
    elif choice == "Marchés en temps réel":
        afficher_marche_temps_reel()
    elif choice == "Recherche d'actions":
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

if __name__ == "__main__":
    main()