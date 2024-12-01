import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# URL de l'API CoinGecko
COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"

@st.cache_data(ttl=3600)
def recuperer_donnees_crypto(devise="usd", nb_cryptos=20):
    """
    Récupère les données des principales cryptomonnaies depuis CoinGecko.
    """
    try:
        params = {
            "vs_currency": devise,
            "order": "market_cap_desc",
            "per_page": nb_cryptos,
            "page": 1,
            "sparkline": "true",
            "price_change_percentage": "1h,24h,7d"
        }
        response = requests.get(COINGECKO_API, params=params)
        if response.status_code == 200:
            data = pd.DataFrame(response.json())
            return data
        else:
            st.error(f"Erreur {response.status_code} lors de la récupération des données.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")
        return pd.DataFrame()

def afficher_graphiques_crypto(data, devise):
    """
    Affiche des graphiques avancés pour les cryptomonnaies.
    """
    st.write("### Comparaison des Prix Historiques (7 Derniers Jours)")
    selection_cryptos = st.multiselect(
        "Sélectionnez les cryptos à comparer :",
        options=data["name"],
        default=[data["name"].iloc[0], data["name"].iloc[1]] if len(data) >= 2 else data["name"].tolist()
    )

    # Vérifier si des cryptos ont été sélectionnées
    if not selection_cryptos:
        st.warning("Veuillez sélectionner au moins une cryptomonnaie.")
        return

    # Option de normalisation des données
    normaliser = st.checkbox("Normaliser les données pour la comparaison (base 100)")

    # Graphique 1 : Courbes des prix historiques
    fig1 = go.Figure()
    for _, row in data[data["name"].isin(selection_cryptos)].iterrows():
        sparkline_data = row["sparkline_in_7d"]  # Dictionnaire contenant 'price' ou liste de prix
        if isinstance(sparkline_data, dict) and 'price' in sparkline_data:
            sparkline = sparkline_data['price']  # Extraire la liste des prix
        elif isinstance(sparkline_data, list):
            sparkline = sparkline_data
        else:
            st.warning(f"Données sparkline manquantes pour {row['name']}.")
            continue  # Passer à l'itération suivante si les données sont manquantes

        if normaliser:
            # Normaliser les données à la valeur initiale (base 100)
            sparkline = [ (price / sparkline[0]) * 100 for price in sparkline ]

        timestamps = [datetime.now() - timedelta(minutes=5 * (len(sparkline) - i)) for i in range(len(sparkline))]
        fig1.add_trace(go.Scatter(
            x=timestamps,
            y=sparkline,
            mode="lines",
            name=row["name"],
            line=dict(width=2)
        ))
    y_axis_title = "Prix Normalisé (Base 100)" if normaliser else f"Prix ({devise.upper()})"
    fig1.update_layout(
        title="Prix Historiques sur 7 Jours",
        xaxis_title="Date",
        yaxis_title=y_axis_title,
        legend_title="Cryptos",
        template="plotly_dark",
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        ),
        hovermode="x unified",
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        font=dict(color='#e6e6e6'),
        title_font=dict(color='#DAA520')
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Graphique 2 : Heatmap des Variations
    st.write("### Heatmap des Variations de Prix")
    variations = data[data["name"].isin(selection_cryptos)][[
        "name",
        "price_change_percentage_1h_in_currency",
        "price_change_percentage_24h_in_currency",
        "price_change_percentage_7d_in_currency"
    ]].set_index("name")
    fig3 = go.Figure(data=go.Heatmap(
        z=variations.values,
        x=["Variation 1h (%)", "Variation 24h (%)", "Variation 7j (%)"],
        y=variations.index,
        colorscale="RdYlGn",
        reversescale=True,
        hoverongaps=False
    ))
    fig3.update_layout(
        title="Heatmap des Variations de Prix",
        xaxis_title="Période",
        yaxis_title="Cryptomonnaie",
        template="plotly_dark",
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        font=dict(color='#e6e6e6'),
        title_font=dict(color='#DAA520')
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Graphique 3 : Graphique 3D
    st.write("### Graphique 3D des Cryptomonnaies")
    # Choix des axes pour le graphique 3D
    x_axis = st.selectbox("Sélectionnez la variable pour l'axe X :", options=["market_cap", "total_volume", "current_price"])
    y_axis = st.selectbox("Sélectionnez la variable pour l'axe Y :", options=["price_change_percentage_24h_in_currency", "price_change_percentage_7d_in_currency"])
    z_axis = st.selectbox("Sélectionnez la variable pour l'axe Z :", options=["current_price", "market_cap", "total_volume"])

    fig2 = go.Figure()
    selected_data = data[data["name"].isin(selection_cryptos)]
    fig2.add_trace(go.Scatter3d(
        x=selected_data[x_axis],
        y=selected_data[y_axis],
        z=selected_data[z_axis],
        mode='markers+text',
        text=selected_data["symbol"].str.upper(),
        textposition="top center",
        marker=dict(
            size=8,
            color=selected_data["current_price"],
            colorscale='Viridis',
            opacity=0.8,
            colorbar=dict(title='Prix actuel')
        )
    ))
    fig2.update_layout(
        scene = dict(
            xaxis_title=x_axis.replace('_', ' ').capitalize(),
            yaxis_title=y_axis.replace('_', ' ').capitalize(),
            zaxis_title=z_axis.replace('_', ' ').capitalize(),
            bgcolor='#0e1117'
        ),
        title="Graphique 3D des Cryptomonnaies",
        template="plotly_dark",
        margin=dict(l=0, r=0, b=0, t=50),
        paper_bgcolor='#0e1117',
        font=dict(color='#e6e6e6'),
        title_font=dict(color='#DAA520')
    )
    st.plotly_chart(fig2, use_container_width=True)

def afficher_tableau_crypto(data):
    """
    Affiche un tableau interactif avec les informations principales des cryptomonnaies.
    """
    if not data.empty:
        data_table = data[[
            "name", "symbol", "current_price", "price_change_percentage_1h_in_currency",
            "price_change_percentage_24h_in_currency", "price_change_percentage_7d_in_currency",
            "market_cap", "total_volume"
        ]].copy()
        data_table.columns = [
            "Nom", "Symbole", "Prix Actuel", "Variation 1h (%)",
            "Variation 24h (%)", "Variation 7j (%)", "Capitalisation", "Volume Échangé"
        ]

        # Style conditionnel pour la variation
        def style_variation(val):
            try:
                color = "green" if float(val) > 0 else "red"
                return f"color: {color}; font-weight: bold;"
            except:
                return ""

        st.write("### Tableau des Cryptomonnaies")
        st.dataframe(
            data_table.style.applymap(style_variation, subset=["Variation 1h (%)", "Variation 24h (%)", "Variation 7j (%)"]),
            use_container_width=True
        )

def afficher_cryptomonnaies():
    """
    Page principale pour afficher les données sur les cryptomonnaies.
    """
    st.markdown("<h1 style='text-align: center; color: #DAA520; font-size:80px'>B&B Finance</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #444;'>", unsafe_allow_html=True)
    
    st.title("💰 Cryptomonnaies")
    st.markdown("### Consultez les données en temps réel sur les principales cryptomonnaies.")

    col1, col2 = st.columns(2)
    with col1:
        devise = st.selectbox("Sélectionnez la devise :", options=["usd", "eur", "btc", "eth"], index=0)
    with col2:
        nb_cryptos = st.slider("Nombre de cryptos à afficher :", min_value=5, max_value=50, value=10, step=5)

    # Récupérer les données
    data_crypto = recuperer_donnees_crypto(devise, nb_cryptos)

    if not data_crypto.empty:
        st.subheader("Graphiques")
        afficher_graphiques_crypto(data_crypto, devise)

        st.subheader("Tableau des Cryptos")
        afficher_tableau_crypto(data_crypto)
    else:
        st.warning("Aucune donnée disponible pour les cryptomonnaies.")

if __name__ == "__main__":
    afficher_cryptomonnaies()