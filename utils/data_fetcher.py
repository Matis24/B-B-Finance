import yfinance as yf

def obtenir_donnees_indice(symbole):
    """
    Récupère les données d'un indice boursier via l'API yfinance.

    Arguments :
        symbole (str) : Le symbole de l'indice ou de l'action (ex: ^DJI, AAPL).

    Retourne :
        tuple : Dernier prix de clôture, variation en pourcentage.
    """
    try:
        ticker = yf.Ticker(symbole)
        # Télécharger les 5 derniers jours de données
        historique = ticker.history(period="5d", interval="1d")

        if historique.empty or len(historique) < 2:
            print(f"Aucune donnée suffisante trouvée pour {symbole}")
            return None, None

        # Obtenir les deux derniers prix de clôture
        dernier_prix = historique['Close'].iloc[-1]
        prix_precedent = historique['Close'].iloc[-2]

        # Calculer la variation en pourcentage
        if prix_precedent == 0:
            print(f"Prix précédent pour {symbole} est 0, impossible de calculer la variation.")
            variation = None
        else:
            variation = ((dernier_prix - prix_precedent) / prix_precedent) * 100

        return round(dernier_prix, 2), round(variation, 2) if variation is not None else None
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {symbole}: {e}")
        return None, None