from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import logging
import joblib
import os  # Add this import

app = Flask(__name__)
auth = HTTPBasicAuth()

logging.basicConfig(filename="logs.txt", level=logging.INFO)

# Load model
model_filename = "soccer_model_best.joblib"
if os.path.exists(model_filename):
    model = joblib.load(model_filename)
else:
    logging.warning(
        f"Model file '{model_filename}' not found. Make sure to run the training script."
    )
    model = None

@auth.verify_password
def verify(username, password):
    if username == "foo" and password == "bar":
        return username

@app.route("/predict", methods=["POST"])
@auth.login_required
def predict():
    if model is None:
        return (
            jsonify(
                {"error": "Model not found. Make sure to run the training script."}
            ),
            500,
        )

    try:
        data = request.json
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
    except Exception as e:
        # Point 5: Handle exceptions and log errors
        logging.error(f"Error predicting: {e}")
        return (
            jsonify({"error": "Failed to make predictions. Check input data format."}),
            500,
        )

if __name__ == "__main__":
    app.run(debug=True)
