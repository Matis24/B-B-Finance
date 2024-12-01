#%%
import pandas as pd
import numpy as np
import lightgbm as lgb

#%%
def prediction(ticker,periode):
    
    # Récupération des données
    historique_max_df = ticker.history(period='max')
    historique_max = pd.DataFrame(historique_max_df)

    # Exploration des données

    # Tri des données proche de 0
    mean_open = historique_max['Open'].mean()
    historique_max = historique_max[(historique_max['Open'] >= 0.2*mean_open)]

    # On ajoute les dates manquantes : pour les weeks-ends, jours fériés ou données non saisies
    date_range = pd.date_range(start=historique_max.index.min(), end=historique_max.index.max())
    historique_max = historique_max.reindex(date_range)

    # On remplace les valeurs manquantes par la denrière valeur connue
    historique_max = historique_max.ffill()

    # Ajoute d'un retard pour prédire chaque données grâce à l'historique des 30 derniers mois
    lags = [historique_max['Close'].shift(lag) for lag in range(1, 180)]
    lag_df = pd.concat(lags, axis=1)

    lag_df.columns = [f'Close_lag{lag}' for lag in range(1, 180)]

    historique_max = pd.concat([historique_max, lag_df], axis=1)

    historique_max['Target'] = historique_max['Close'].shift(-1)

    historique_max.dropna(inplace=True)

    #  Entrainement du model
    X = historique_max.drop(columns=['Target','Dividends','Stock Splits'])
    y = historique_max['Target']

    # Entraîner le modèle sur toutes les données disponibles
    model = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.5)
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
