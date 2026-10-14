from price_model import predict_price


try:

    price = predict_price(
        crop="Wheat",
        state="Uttar Pradesh",
        season="Rabi",
        month=4
    )

    print()
    print("==============================")
    print("   KISAN MITRA AI")
    print("   Crop Price Prediction")
    print("==============================")
    print()
    print(f"Crop: Wheat")
    print(f"State: Uttar Pradesh")
    print(f"Season: Rabi")
    print(f"Month: 4")
    print()
    print(f"Predicted Price: ₹{price} per quintal")
    print()
    print("==============================")


except Exception as e:

    print()
    print("Prediction Error:")
    print(e)