import streamlit as st
import pandas as pd
from utils.data_fetcher import obtenir_donnees_indice

def afficher_alertes_personnalisees():
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
        /* Titres */
        h1, h2, h3, h4, h5, h6 {
            color: #58a6ff;
        }
        /* Boutons et sélecteurs */
        .stButton>button, .stTextInput, .stNumberInput, .stSelectbox {
            background-color: #161b22;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 5px;
        }
        /* Messages */
        .stAlert {
            background-color: #161b22;
            color: #c9d1d9;
            border: 1px solid #30363d;
        }
        /* Tables */
        .stDataFrame {
            background-color: #0d1117;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='text-align: center;'>🔔 Alertes Personnalisées</h1>", unsafe_allow_html=True)
    st.write("Recevez des notifications en temps réel en fonction des conditions que vous définissez.")

    # Initialiser les états
    if "alertes" not in st.session_state:
        st.session_state["alertes"] = []  # Liste des alertes actives
    if "alertes_history" not in st.session_state:
        st.session_state["alertes_history"] = []  # Historique des alertes déclenchées

    # Formulaire pour ajouter une alerte
    st.markdown("### ➕ Ajouter une nouvelle alerte")
    with st.form("form_ajouter_alerte"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            symbole = st.text_input("Symbole de l'action", value="", placeholder="Ex : AAPL, TSLA")
        with col2:
            condition = st.selectbox(
                "Condition",
                options=["Prix supérieur à", "Prix inférieur à", "Variation en % supérieur à", "Variation en % inférieur à"]
            )
        with col3:
            valeur = st.number_input("Valeur", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Ajouter l'alerte")

        if submit:
            if symbole.strip() == "":
                st.error("Veuillez entrer un symbole valide.")
            else:
                # Vérifier si le symbole est valide
                prix, variation = obtenir_donnees_indice(symbole.strip().upper())
                if prix is None:
                    st.error(f"Le symbole {symbole.strip().upper()} est invalide ou les données ne sont pas disponibles.")
                else:
                    # Ajouter l'alerte à la liste
                    alerte = {"symbole": symbole.strip().upper(), "condition": condition, "valeur": valeur}
                    st.session_state["alertes"].append(alerte)
                    st.success(f"Alerte ajoutée pour {symbole.strip().upper()} : {condition} {valeur}")

    # Afficher les alertes actives
    st.markdown("### 📋 Alertes Actives")
    if st.session_state["alertes"]:
        for i, alerte in enumerate(st.session_state["alertes"]):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(
                    f"**{alerte['symbole']}** - {alerte['condition']} {alerte['valeur']}"
                )
            with col2:
                if st.button("✏️ Modifier", key=f"mod_{i}"):
                    # Implémenter la modification de l'alerte
                    with st.form(f"mod_form_{i}"):
                        new_symbole = st.text_input("Symbole de l'action", value=alerte['symbole'])
                        new_condition = st.selectbox(
                            "Condition",
                            options=["Prix supérieur à", "Prix inférieur à", "Variation en % supérieur à", "Variation en % inférieur à"],
                            index=["Prix supérieur à", "Prix inférieur à", "Variation en % supérieur à", "Variation en % inférieur à"].index(alerte['condition'])
                        )
                        new_valeur = st.number_input("Valeur", min_value=0.0, step=0.01, value=alerte['valeur'])
                        submit_mod = st.form_submit_button("Enregistrer les modifications")
                        if submit_mod:
                            st.session_state["alertes"][i] = {
                                "symbole": new_symbole.strip().upper(),
                                "condition": new_condition,
                                "valeur": new_valeur
                            }
                            st.success("Alerte modifiée avec succès.")
                            st.experimental_rerun()
            with col3:
                if st.button("🗑️ Supprimer", key=f"sup_{i}"):
                    del st.session_state["alertes"][i]
                    st.success("Alerte supprimée.")
                    st.experimental_rerun()
    else:
        st.info("Aucune alerte active.")

    # Vérifier les alertes en temps réel
    st.markdown("### 🔄 Vérification des Alertes")
    if st.session_state["alertes"]:
        for alerte in st.session_state["alertes"]:
            symbole = alerte["symbole"]
            condition = alerte["condition"]
            valeur = alerte["valeur"]

            # Récupérer les données actuelles
            prix, variation = obtenir_donnees_indice(symbole)

            # Vérifier si l'alerte est déclenchée
            if prix is not None:
                alerte_declenchee = False
                if condition == "Prix supérieur à" and prix > valeur:
                    alerte_declenchee = True
                elif condition == "Prix inférieur à" and prix < valeur:
                    alerte_declenchee = True
                elif condition == "Variation en % supérieur à" and variation > valeur:
                    alerte_declenchee = True
                elif condition == "Variation en % inférieur à" and variation < valeur:
                    alerte_declenchee = True

                if alerte_declenchee:
                    # Ajouter à l'historique si non déjà présent
                    if not any(h["symbole"] == symbole and h["condition"] == condition and h["valeur"] == valeur for h in st.session_state["alertes_history"]):
                        st.session_state["alertes_history"].append(
                            {
                                "symbole": symbole,
                                "condition": condition,
                                "valeur": valeur,
                                "prix_actuel": prix,
                                "variation_actuelle": variation,
                            }
                        )
                        st.warning(f"🚨 Alerte déclenchée : {symbole} - {condition} {valeur}")
            else:
                st.info(f"Aucune donnée disponible pour {symbole}")

    # Afficher l'historique des alertes déclenchées
    st.markdown("### 🕒 Historique des Alertes Déclenchées")
    if st.session_state["alertes_history"]:
        historique_df = pd.DataFrame(st.session_state["alertes_history"])
        st.dataframe(
            historique_df.style.applymap(
                lambda val: 'color: green;' if val > 0 else 'color: red;',
                subset=['prix_actuel', 'variation_actuelle']
            )
        )
    else:
        st.info("Aucune alerte déclenchée pour le moment.")