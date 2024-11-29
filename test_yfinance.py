import yfinance as yf

def test_yfinance():
    symbol = "AAPL"  # Apple Inc.
    ticker = yf.Ticker(symbol)
    historique = ticker.history(period="5d", interval="1d")  # Utilisation de '5d' au lieu de '2d'
    print(f"\nHistorique pour {symbol}:\n{historique}\n")

    if historique.empty:
        print(f"Aucune donnée trouvée pour {symbol}.")
        return

    if len(historique) < 2:
        print(f"Données insuffisantes pour calculer la variation pour {symbol}.")
        return

    dernier_prix = historique['Close'].iloc[-1]
    prix_precedent = historique['Close'].iloc[-2]
    variation = ((dernier_prix - prix_precedent) / prix_precedent) * 100

    print(f"Symbole: {symbol}")
    print(f"Dernier Prix de Clôture : {dernier_prix}")
    print(f"Prix de Clôture Précédent : {prix_precedent}")
    print(f"Variation : {variation:.2f}%")

if __name__ == "__main__":
    test_yfinance()