import streamlit as st
import requests

# URL de base de l'API NewsData.io
BASE_URL = "https://newsdata.io/api/1/news"

# Liste des catégories valides initiales
CATEGORIES_VALIDES = {
    "Entreprises": "business",
    "Technologie": "technology",
    "Science": "science",
    "Santé": "health",
    "Monde": "world"
}

def tester_combinaison(categorie, langue):
    """
    Teste si une combinaison de catégorie et de langue retourne des résultats.
    """
    params = {
        "apikey": st.secrets["NEWS_API_KEY"],
        "category": categorie,
        "language": langue
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return bool(response.json().get("results", []))
    return False

def recuperer_actualites(categorie, langue):
    """
    Récupère les actualités depuis NewsData.io.
    """
    try:
        params = {
            "apikey": st.secrets["NEWS_API_KEY"],
            "category": categorie,
            "language": langue
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        elif response.status_code == 422:
            st.warning(f"La catégorie '{categorie}' ou la langue '{langue}' n'est pas valide.")
            return []
        else:
            st.error(f"Erreur {response.status_code} lors de la récupération des actualités.")
            return []
    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")
        return []

def afficher_cartes_actualites(articles):
    """
    Affiche les actualités sous forme de cartes modernes et stylées.
    """
    # Styles CSS globaux
    st.markdown(
        """
        <style>
            .card {
                background-color: #1e1e1e;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                transition: transform 0.2s;
            }
            .card:hover {
                transform: scale(1.02);
            }
            .card-title {
                font-size: 1.5rem;
                color: #DAA520;
                margin-bottom: 10px;
                font-weight: bold;
            }
            .card-description {
                font-size: 1rem;
                color: #e6e6e6;
                margin-bottom: 15px;
            }
            .card-link {
                text-decoration: none;
                color: #00d4ff;
                font-weight: bold;
                font-size: 1rem;
            }
            .card-link:hover {
                text-decoration: underline;
                color: #00a3cc;
            }
            .card-image {
                width: 100%;
                height: auto;
                border-radius: 10px;
                margin-bottom: 15px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    for article in articles:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            # Image
            if article.get('image_url'):
                st.markdown(
                    f'<img src="{article["image_url"]}" alt="Image de l\'article" class="card-image">',
                    unsafe_allow_html=True
                )

            # Titre
            st.markdown(
                f'<div class="card-title">{article.get("title", "Sans titre")}</div>',
                unsafe_allow_html=True
            )

            # Description
            if article.get('description'):
                st.markdown(
                    f'<div class="card-description">{article["description"]}</div>',
                    unsafe_allow_html=True
                )

            # Bouton pour lire l'article complet
            st.markdown(
                f'<a class="card-link" href="{article.get("link", "#")}" target="_blank">Lire l\'article complet</a>',
                unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

def afficher_actualites_financieres():
    """
    Page principale pour afficher les actualités financières.
    """
    st.title("📰 Actualités Financières et Globales")
    st.write("Consultez les dernières nouvelles sur les entreprises, la technologie, la science, la santé, et le monde.")

    # Filtres
    categorie_affichable = st.selectbox("Catégorie", list(CATEGORIES_VALIDES.keys()))
    langue = st.selectbox("Langue", ["fr", "en"])

    # Correspondance avec les catégories valides
    categorie = CATEGORIES_VALIDES[categorie_affichable]

    # Tester la validité de la combinaison
    if not tester_combinaison(categorie, langue):
        st.warning(f"Aucune donnée disponible pour la catégorie '{categorie_affichable}' en langue '{langue}'.")
        st.info("Basculer sur la langue 'en' et la catégorie 'business'.")
        categorie = "business"
        langue = "en"

    # Récupérer les actualités
    articles = recuperer_actualites(categorie, langue)

    # Afficher les actualités
    if articles:
        afficher_cartes_actualites(articles)
    else:
        st.info(f"Aucune actualité disponible pour la catégorie '{categorie_affichable}' en langue '{langue}'.")