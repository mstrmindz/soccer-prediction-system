from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import logging
import joblib
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

logging.basicConfig(filename="logs.txt", level=logging.INFO)

# Load model
model_filename = "soccer_model_best.joblib"
model = None  # Initialize the model outside the condition

if os.path.exists(model_filename):
    model = joblib.load(model_filename)
else:
    logging.warning(
        f"Model file '{model_filename}' not found. Make sure to run the training script."
    )

@auth.verify_password
def verify(username, password):
    return username == "foo" and password == "bar"

@app.route("/predict", methods=["POST"])
@auth.login_required
def predict():
    if model is None:
        return (
            jsonify({"error": "Model not found. Make sure to run the training script."}),
            500,
        )

    data = request.get_json()

    if "features" not in data:
        return jsonify({"error": "Invalid request. 'features' not found in the request."}), 400

    features = data["features"]

    logging.info(f"Received prediction request: {data}")

    prediction = model.predict([features])[0]
    probabilities = model.predict_proba([features])

    prediction_data = {
        "prediction": prediction,
        "probability": {
            "win": probabilities[0, 0],
            "draw": probabilities[0, 1],
            "lose": probabilities[0, 2],
        },
    }

    logging.info(f"Prediction result: {prediction_data}")

    return jsonify(prediction_data)

if __name__ == "__main__":
    app.run(debug=True)
