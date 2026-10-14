import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_csv("crop_price_data.csv")

print("Dataset loaded successfully!")
print(df.head())

print("\nDataset shape:", df.shape)


# ==========================================
# INPUT FEATURES
# ==========================================

X = df[
    [
        "crop",
        "state",
        "season",
        "month"
    ]
]


# TARGET

y = df["avg_price"]


# ==========================================
# CATEGORICAL + NUMERICAL FEATURES
# ==========================================

categorical_features = [
    "crop",
    "state",
    "season"
]

numerical_features = [
    "month"
]


# ==========================================
# PREPROCESSING
# ==========================================

preprocessor = ColumnTransformer(

    transformers=[

        (
            "categorical",

            OneHotEncoder(
                handle_unknown="ignore"
            ),

            categorical_features
        ),

        (
            "numerical",

            "passthrough",

            numerical_features
        )

    ]
)


# ==========================================
# RANDOM FOREST MODEL
# ==========================================

model = RandomForestRegressor(

    n_estimators=200,

    random_state=42,

    max_depth=10

)


# ==========================================
# PIPELINE
# ==========================================

pipeline = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )

    ]

)


# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.2,

    random_state=42

)


# ==========================================
# TRAIN
# ==========================================

print("\nTraining model...")

pipeline.fit(
    X_train,
    y_train
)


# ==========================================
# EVALUATION
# ==========================================

predictions = pipeline.predict(
    X_test
)


mae = mean_absolute_error(
    y_test,
    predictions
)


print("\nModel training completed!")

print(
    f"Mean Absolute Error: ₹{mae:.2f}"
)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    pipeline,
    "crop_price_model.pkl"
)


print(
    "\nModel saved as crop_price_model.pkl"
)