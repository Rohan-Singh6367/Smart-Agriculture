import joblib
import pandas as pd


# Load trained model
model = joblib.load("crop_price_model.pkl")


def predict_price(crop, state, season, month):

    data = pd.DataFrame({
        "crop": [crop],
        "state": [state],
        "season": [season],
        "month": [month]
    })

    prediction = model.predict(data)[0]

    return round(float(prediction), 2)