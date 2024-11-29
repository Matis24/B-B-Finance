import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

def afficher_comparaison_actions():
    st.markdown("<h1 style='text-align: center; color: #DAA520; font-size:80px'>B&B Finance</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #444;'>", unsafe_allow_html=True)
    
    st.title("📈 Comparaison Avancée d'Actions")
    st.markdown("### Analysez et comparez les performances de plusieurs actions avec des outils avancés.")

    # Liste de symboles prédéfinis
    liste_actions = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NFLX", "META"]

    # Saisie utilisateur pour ajouter des symboles personnalisés
    symbole_personnalise = st.text_input(
        "Ajoutez des symboles personnalisés (séparés par des virgules)",
        placeholder="Exemple : AAPL, TSLA, GOOGL"
    )

    # Convertir les symboles personnalisés en liste et fusionner avec la liste prédéfinie
    if symbole_personnalise:
        symboles_ajoutes = [symbole.strip().upper() for symbole in symbole_personnalise.split(",")]
        liste_actions = sorted(list(set(liste_actions + symboles_ajoutes)))  # Éviter les doublons

    # Multisélecteur pour choisir parmi tous les symboles disponibles
    actions_selectionnees = st.multiselect(
        "Sélectionnez les actions à comparer",
        options=liste_actions,
        default=["AAPL", "MSFT"]  # Par défaut, AAPL et MSFT
    )

    # Sélecteur de période
    periode = st.selectbox(
        "Période de comparaison",
        options=["1 mois", "3 mois", "6 mois", "1 an", "5 ans", "Max"],
        index=3
    )

    # Correspondance entre la sélection et la période de yfinance
    dict_periode = {
        "1 mois": "1mo",
        "3 mois": "3mo",
        "6 mois": "6mo",
        "1 an": "1y",
        "5 ans": "5y",
        "Max": "max"
    }

    # Sélection de l'intervalle
    intervalle = st.selectbox(
        "Intervalle des données",
        options=["1 jour", "1 semaine", "1 mois"],
        index=0
    )

    dict_intervalle = {
        "1 jour": "1d",
        "1 semaine": "1wk",
        "1 mois": "1mo"
    }

    # Option de normalisation des données
    normaliser = st.checkbox("Normaliser les données pour la comparaison (base 100)")

    if actions_selectionnees:
        # Récupérer les données pour chaque action
        donnees_actions = {}
        infos_actions = {}
        for symbole in actions_selectionnees:
            action = yf.Ticker(symbole)
            historique = action.history(
                period=dict_periode[periode],
                interval=dict_intervalle[intervalle]
            )
            if not historique.empty:
                donnees_actions[symbole] = historique["Close"]
                infos_actions[symbole] = action.info
            else:
                st.warning(f"Aucune donnée disponible pour {symbole} sur la période sélectionnée.")

        if donnees_actions:
            # Créer un DataFrame avec toutes les actions
            df_comparaison = pd.DataFrame(donnees_actions)

            # Normaliser les données si l'option est cochée
            if normaliser:
                df_comparaison = df_comparaison / df_comparaison.iloc[0] * 100

            # Calcul des performances
            variations = df_comparaison.apply(
                lambda x: ((x.iloc[-1] - x.iloc[0]) / x.iloc[0]) * 100 if len(x) > 1 else None
            )

            # Calcul des statistiques supplémentaires
            prix_max = df_comparaison.max()
            prix_min = df_comparaison.min()
            volume_moyen = {}
            for symbole in actions_selectionnees:
                historique = yf.Ticker(symbole).history(
                    period=dict_periode[periode],
                    interval=dict_intervalle[intervalle]
                )
                volume_moyen[symbole] = historique["Volume"].mean()

            # Création du tableau des performances
            tableau = pd.DataFrame({
                "Symbole": actions_selectionnees,
                "Variation (%)": [variations[sym] for sym in actions_selectionnees],
                "Prix Max": [prix_max[sym] for sym in actions_selectionnees],
                "Prix Min": [prix_min[sym] for sym in actions_selectionnees],
                "Volume Moyen": [volume_moyen[sym] for sym in actions_selectionnees],
                "Capitalisation Boursière": [
                    f"${infos_actions[sym].get('marketCap', 'N/A'):,}" if 'marketCap' in infos_actions[sym] else "N/A"
                    for sym in actions_selectionnees
                ],
                "PER (TTM)": [
                    infos_actions[sym].get('trailingPE', 'N/A') if 'trailingPE' in infos_actions[sym] else "N/A"
                    for sym in actions_selectionnees
                ],
                "Secteur": [
                    infos_actions[sym].get('sector', 'N/A') if 'sector' in infos_actions[sym] else "N/A"
                    for sym in actions_selectionnees
                ]
            })

            # Ajustement des formats numériques
            tableau["Variation (%)"] = tableau["Variation (%)"].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
            tableau["Prix Max"] = tableau["Prix Max"].map(lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A")
            tableau["Prix Min"] = tableau["Prix Min"].map(lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A")
            tableau["Volume Moyen"] = tableau["Volume Moyen"].map(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")

            # Affichage du tableau avec styles conditionnels
            st.markdown("### 📊 Tableau des Performances")
            def style_variation(val):
                if isinstance(val, str) and val.endswith('%'):
                    val_float = float(val.strip('%'))
                    if val_float > 0:
                        color = 'green'
                    elif val_float < 0:
                        color = 'red'
                    else:
                        color = 'grey'
                    return f'color: {color}; font-weight: bold;'
                return ''

            st.write(
                tableau.style.applymap(style_variation, subset=["Variation (%)"]).set_properties(**{
                    'background-color': '#0e1117',
                    'color': '#e6e6e6',
                    'border-color': '#313131'
                }),
                unsafe_allow_html=True
            )

            # Graphique Comparatif avec Plotly
            st.markdown("### 📈 Graphique Comparatif")
            fig = go.Figure()
            for symbole in actions_selectionnees:
                fig.add_trace(go.Scatter(
                    x=df_comparaison.index,
                    y=df_comparaison[symbole],
                    mode='lines',
                    name=symbole
                ))

            fig.update_layout(
                title="Comparaison des Prix de Clôture",
                xaxis_title="Date",
                yaxis_title="Prix Normalisé" if normaliser else "Prix de Clôture",
                template="plotly_dark",
                hovermode="x unified",
                legend=dict(title="Symboles"),
                paper_bgcolor='#0e1117',
                plot_bgcolor='#0e1117',
                font=dict(color='#e6e6e6'),
                title_font=dict(color='#DAA520')
            )
            st.plotly_chart(fig, use_container_width=True)

            # Téléchargement des données
            st.markdown("### 💾 Télécharger les Données")
            csv = df_comparaison.to_csv(index=True)
            st.download_button(
                label="Télécharger les données en CSV",
                data=csv,
                file_name='comparaison_actions.csv',
                mime='text/csv',
            )

            # Affichage des données historiques
            st.markdown("### 🗒️ Données Historiques Sélectionnées")
            for symbole in actions_selectionnees:
                st.markdown(f"#### {symbole}")
                historique = yf.Ticker(symbole).history(
                    period=dict_periode[periode],
                    interval=dict_intervalle[intervalle]
                )
                st.dataframe(historique[['Open', 'High', 'Low', 'Close', 'Volume']].tail(5))
        else:
            st.error("Aucune donnée valide n'a été trouvée pour les symboles sélectionnés.")
    else:
        st.info("Veuillez sélectionner au moins une action pour commencer.")