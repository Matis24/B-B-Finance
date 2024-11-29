#%%
import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBRegressor

#%%
def prediction(ticker,periode):
    
    # Récupération des données
    historique_max_df = ticker.history(period='max')
    historique_max = pd.DataFrame(historique_max_df)

    # Exploration des données
    #plt.plot(historique_max['Close'])

    # Tri des données proche de 0
    # On supprime les périodes où la valeur de l'action est très éloigné de la moyenne (une action est proche de 0 pendant des années)
    mean_open = historique_max['Open'].mean()
    historique_max = historique_max[(historique_max['Open'] >= 0.5*mean_open)]

    # Ajout des journées non ouvrables
    # On ajoute les dates manquantes : pour les weeks-ends, jours fériés ou données non saisies
    date_range = pd.date_range(start=historique_max.index.min(), end=historique_max.index.max())
    historique_max = historique_max.reindex(date_range)

    # On remplace les valeurs manquantes par la denrière valeur connue
    historique_max = historique_max.ffill()

    # Ajoute d'un retard pour prédire chaque données grâce à l'historique des 30 derniers mois
    for lag in range(1, 365):
        historique_max[f'Close_lag{lag}'] = historique_max['Close'].shift(lag)

    historique_max['Target'] = historique_max['Close'].shift(-1)

    historique_max.dropna(inplace=True)

    # Exploration des données après traitement
    #plt.plot(historique_max['Close'])

    #  Entrainement du model
    # Caractéristiques (features) et cible (target)
    X = historique_max.drop(columns=['Target'])
    y = historique_max['Target']

    # Entraîner le modèle sur toutes les données disponibles
    model = XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.5)
    model.fit(X, y)

    # Prévoir les 30 prochains jours
    predictions = []
    last_date = X.iloc[-1].values

    period = periode

    for _ in range(period):
        predict = model.predict(last_date.reshape(1, -1))[0]
        predictions.append(predict)
        last_date = np.roll(last_date, -1)  
        last_date[-1] = predict 

    # Résultats des prédictions
    future_dates = pd.date_range(historique_max_df.index[-1], periods=period)  # 30 jours ouvrables
    predict_df = pd.DataFrame({'Date': future_dates, 'Predictions': predictions}).set_index('Date')
    predict_df.reset_index(inplace=True)
    
    return predict_df
    # 
    #plt.plot(historique_max['Close'])
    #plt.plot(predicted_df['Predicted_Close'])
    
    
# %% Test graphique
# predict_df = prediction(yf.Ticker('AAPL'))
# predict_df.reset_index(inplace=True)

# # %%
# historique_max_df = yf.Ticker('AAPL').history(period='max')

# fig = go.Figure()
# fig.add_trace(go.Scatter(
#     x=historique_max_df.index,
#     y=historique_max_df["Close"],
#     mode='lines',
#     name='Prix de clôture'
# ))
# fig.add_trace(go.Scatter(
#     x=predict_df['Date'],
#     y=predict_df["Predictions"],
#     mode='lines',
#     name='Prédictions',
#     line=dict(dash='dash')
# ))
# %%
