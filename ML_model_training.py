import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


df = pd.read_csv("ev_dataset.csv")


df = df.dropna(subset=["brand", "battery_kwh", "range_km"])  # Ensure required data exists

# Encode brand names
brand_encoder = LabelEncoder()
df["brand_encoded"] = brand_encoder.fit_transform(df["brand"])

# Features and Targets
X = df[["brand_encoded"]]
y_battery = df["battery_kwh"]
y_range = df["range_km"]

# Train-test split
X_train, X_test, y_bat_train, y_bat_test, = train_test_split(X, y_battery, test_size=0.2, random_state=42)
X_train2, X_test2, y_rng_train, y_rng_test = train_test_split(X, y_range, test_size=0.2, random_state=42)

# Train two regression models
battery_model = LinearRegression()
battery_model.fit(X_train, y_bat_train)

range_model = LinearRegression()
range_model.fit(X_train2, y_rng_train)

# Evaluate performance
battery_pred = battery_model.predict(X_test)
range_pred = range_model.predict(X_test2)

print("Battery Prediction MAE:", mean_absolute_error(y_bat_test, battery_pred))
print("Range Prediction MAE:", mean_absolute_error(y_rng_test, range_pred))

#  Prediction Function 
def predict_ev_specs(brand_name):
    brand_code = brand_encoder.transform([brand_name])[0]
    battery_est = battery_model.predict([[brand_code]])[0]
    range_est = range_model.predict([[brand_code]])[0]
    return battery_est, range_est

# Example Usage:
brand = "Tata"
battery, range_km = predict_ev_specs(brand)
print(f"Predicted Specs for {brand}:")
print(f"Battery ≈ {battery:.1f} kWh")
print(f"Range ≈ {range_km:.0f} km")
