import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

def afficher_indicateurs_pays():
    st.markdown("<h1 style='text-align: center; color: #DAA520; font-size:80px'>B&B Finance</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #444;'>", unsafe_allow_html=True)
    
    # Application de styles CSS personnalisés
    st.markdown(
        """
        <style>
        /* Style global */
        body {
            background-color: #0e1117;
            color: #c9d1d9;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        /* En-tête */
        .main > div {
            padding-top: 0rem;
        }
        /* Titres */
        h1, h2, h3, h4, h5, h6 {
            color: #58a6ff;
        }
        /* Boutons et sélecteurs */
        .stButton>button, .stSlider, .stSelectbox, .stMultiSelect {
            background-color: #161b22;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 5px;
        }
        /* Graphiques */
        .stPlotlyChart {
            background-color: #0d1117;
        }
        /* Tableau de données */
        .stDataFrame {
            background-color: #0d1117;
        }
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #161b22;
        }
        ::-webkit-scrollbar-thumb {
            background: #30363d;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Titre principal avec icône
    st.markdown("<h1 style='text-align: center; color: #58a6ff;'>🌐 Analyse Économique Mondiale</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:18px;'>Explorez les indicateurs économiques clés par pays pour une prise de décision informée.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #30363d'>", unsafe_allow_html=True)

    # Barre latérale pour les sélections
    with st.sidebar:
        st.markdown("<h2 style='color: #58a6ff;'>🔎 Paramètres</h2>", unsafe_allow_html=True)

        # Sélection des indicateurs avec possibilité de recherche
        indicateurs = {
            "PIB par habitant (USD actuel)": "NY.GDP.PCAP.CD",
            "Croissance du PIB (% annuel)": "NY.GDP.MKTP.KD.ZG",
            "Taux d'inflation (% annuel)": "FP.CPI.TOTL.ZG",
            "Taux de chômage (% de la population active)": "SL.UEM.TOTL.ZS",
            "Dette publique (% du PIB)": "GC.DOD.TOTL.GD.ZS",
            "Balance commerciale (% du PIB)": "NE.RSB.GNFS.ZS",
            "Indice de développement humain": "HD.HCI.OVRL",
            "Espérance de vie à la naissance (années)": "SP.DYN.LE00.IN",
            "Population totale": "SP.POP.TOTL",
            "Émissions de CO2 (tonnes métriques par habitant)": "EN.ATM.CO2E.PC",
            "Accès à l'électricité (% de la population)": "EG.ELC.ACCS.ZS",
            "Dépenses en éducation (% du PIB)": "SE.XPD.TOTL.GD.ZS",
        }

        indicateur_nom = st.selectbox("Choisissez un indicateur économique", sorted(indicateurs.keys()))
        code_indicateur = indicateurs[indicateur_nom]

        # Sélection de l'année
        annee = st.slider("Sélectionnez l'année", 2000, 2021, 2021)

    # Récupération des données
    @st.cache_data
    def get_data(indicateur, annee):
        url = f"https://api.worldbank.org/v2/country/all/indicator/{indicateur}?format=json&date={annee}&per_page=300"
        response = requests.get(url)
        data = response.json()
        if len(data) > 1:
            df = pd.DataFrame(data[1])
            return df
        else:
            return pd.DataFrame()

    df = get_data(code_indicateur, annee)

    if df.empty:
        st.warning("Aucune donnée disponible pour cet indicateur et cette année.")
        return

    # Traitement des données
    df = df[['country', 'value']]
    df = df.dropna()
    df['Country'] = df['country'].apply(lambda x: x['value'])
    df['Country Code'] = df['country'].apply(lambda x: x['id'])
    df['Value'] = df['value'].astype(float)

    # Charger les données géographiques pour la carte
    df_geo = px.data.gapminder().query("year==2007")[['country', 'iso_alpha']].drop_duplicates()
    df = pd.merge(df, df_geo, left_on='Country', right_on='country', how='left')

    # Supprimer les pays sans code ISO
    df = df.dropna(subset=['iso_alpha'])

    # Affichage de la carte avec amélioration esthétique
    fig_map = px.choropleth(
        df,
        locations="iso_alpha",
        color="Value",
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Turbo,
        template='plotly_dark',
        labels={'Value': indicateur_nom},
        hover_data={'iso_alpha': False, 'Value': ':.2f'},
        projection='natural earth',
    )

    # Personnalisation supplémentaire de la carte
    fig_map.update_geos(
        showcoastlines=False,
        showland=True,
        landcolor="#0d1117",
        showocean=True,
        oceancolor="#010409",
        showlakes=False,
        showrivers=False,
    )

    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(
            title=indicateur_nom,
            tickvals=[df['Value'].min(), df['Value'].max()],
            ticktext=[f"{df['Value'].min():.2f}", f"{df['Value'].max():.2f}"],
        ),
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        geo_bgcolor='#0e1117',
        dragmode=False,
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # Ligne de séparation stylisée
    st.markdown("<hr style='border:1px solid #30363d'>", unsafe_allow_html=True)

    # Affichage du top 10 des pays
    st.markdown(f"<h2 style='text-align: center; color: #58a6ff;'>🏆 Top 10 des pays pour {indicateur_nom} en {annee}</h2>", unsafe_allow_html=True)
    df_top10 = df.sort_values(by='Value', ascending=False).head(10)
    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        x=df_top10['Value'][::-1],
        y=df_top10['Country'][::-1],
        orientation='h',
        marker=dict(
            color=df_top10['Value'][::-1],
            colorscale='Turbo',
        ),
        hovertemplate='<b>%{y}</b><br>Valeur: %{x:.2f}<extra></extra>',
    ))

    fig_bar.update_layout(
        template='plotly_dark',
        margin={"r":0,"t":30,"l":0,"b":0},
        xaxis_title=indicateur_nom,
        yaxis_title="Pays",
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # Ligne de séparation stylisée
    st.markdown("<hr style='border:1px solid #30363d'>", unsafe_allow_html=True)

    # Affichage de l'évolution temporelle pour un ou plusieurs pays
    st.markdown(f"<h2 style='text-align: center; color: #58a6ff;'>📈 Évolution de {indicateur_nom} au fil du temps</h2>", unsafe_allow_html=True)

    # Liste des pays disponibles
    pays_disponibles = df['Country'].unique()

    # Sélection multiple des pays pour le graphique en courbes
    pays_selectionnes_evolution = st.multiselect(
        "Sélectionnez les pays à afficher dans le graphique d'évolution temporelle (max 5)",
        options=sorted(pays_disponibles),
        default=pays_disponibles[:5]
    )

    if not pays_selectionnes_evolution:
        st.warning("Veuillez sélectionner au moins un pays pour afficher le graphique d'évolution.")
        return

    pays_selectionnes_evolution = pays_selectionnes_evolution[:5]  # Limiter à 5 pays pour la lisibilité

    @st.cache_data
    def get_historical_data(indicateur, pays_codes):
        frames = []
        for code in pays_codes:
            url = f"https://api.worldbank.org/v2/country/{code}/indicator/{indicateur}?format=json&date=2000:2021&per_page=300"
            response = requests.get(url)
            data = response.json()
            if len(data) > 1:
                df_hist = pd.DataFrame(data[1])
                df_hist['Country Code'] = code
                frames.append(df_hist)
        if frames:
            return pd.concat(frames, ignore_index=True)
        else:
            return pd.DataFrame()

    # Obtenir les codes pays ISO2 pour les pays sélectionnés
    country_info = df[df['Country'].isin(pays_selectionnes_evolution)][['Country', 'Country Code']].drop_duplicates()
    country_codes = country_info['Country Code'].tolist()

    df_hist = get_historical_data(code_indicateur, country_codes)
    if not df_hist.empty:
        df_hist = df_hist[['country', 'date', 'value']]
        df_hist = df_hist.dropna()
        df_hist['Value'] = df_hist['value'].astype(float)
        df_hist['Year'] = df_hist['date'].astype(int)
        df_hist['Country'] = df_hist['country'].apply(lambda x: x['value'])
        df_hist = df_hist.sort_values('Year')

        fig_line = go.Figure()
        for country in pays_selectionnes_evolution:
            df_country = df_hist[df_hist['Country'] == country]
            fig_line.add_trace(go.Scatter(
                x=df_country['Year'],
                y=df_country['Value'],
                mode='lines+markers',
                name=country,
                line=dict(width=3),
                marker=dict(size=8),
                hovertemplate='Année %{x}: %{y:.2f}<extra></extra>',
            ))

        fig_line.update_layout(
            template='plotly_dark',
            margin={"r":0,"t":30,"l":0,"b":0},
            xaxis_title="Année",
            yaxis_title=indicateur_nom,
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            xaxis=dict(showgrid=False, tickmode='linear'),
            yaxis=dict(showgrid=False),
            legend_title="Pays",
        )

        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Aucune donnée historique disponible pour les pays sélectionnés.")

    # Ligne de séparation stylisée
    st.markdown("<hr style='border:1px solid #30363d'>", unsafe_allow_html=True)

    # Affichage du tableau des données avec options avancées
    st.markdown("<h2 style='text-align: center; color: #58a6ff;'>📊 Données détaillées</h2>", unsafe_allow_html=True)
    df_display = df[['Country', 'Value']].sort_values(by='Country').reset_index(drop=True)
    df_display = df_display.style.background_gradient(cmap='Blues').set_properties(**{'color': '#c9d1d9', 'background-color': '#0e1117'})
    st.table(df_display)

    # Bouton pour télécharger les données en CSV
    csv = df[['Country', 'Value']].to_csv(index=False)
    st.download_button(
        label="📥 Télécharger les données en CSV",
        data=csv,
        file_name='indicateurs_pays.csv',
        mime='text/csv',
    )

    # Pied de page
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:12px;'>Données fournies par la Banque mondiale.</p>", unsafe_allow_html=True)