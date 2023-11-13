# auto_train.py
import pandas as pd
import tweepy
from textblob import TextBlob
import joblib
import logging
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

logging.basicConfig(filename="auto_train.log", level=logging.INFO)

# Configuration (replace with your actual values)
CONSUMER_KEY = "ilBmO6j50lCo201poPxM1IZLJ"
CONSUMER_SECRET = "VLy1gDVXxIxbYN7ylIsJbtwX5prGPoJSFMMS35iYXPvfxSChoT"
ACCESS_TOKEN = "215601018-6wNrATVu9xAzSmmWXbAW4nyC34BWofAmElsN8dnd"
ACCESS_TOKEN_SECRET = "215601018-6wNrATVu9xAzSmmWXbAW4nyC34BWofAmElsN8dnd"

MODEL_FILENAME = "soccer_model_best.joblib"
CSV_FILENAME = "soccer_data.csv"


def setup_twitter_api(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def get_tweets(api, team_name, count=100):
    try:
        tweets = tweepy.Cursor(api.search, q=team_name, lang="en").items(count)
        return [tweet.text for tweet in tweets]
    except tweepy.TweepError as e:
        logging.error(f"Error fetching tweets for {team_name}: {str(e)}")
        return []


def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity


def fetch_and_analyze_tweets(api, data):
    for index, row in data.iterrows():
        team_name = row["Manchester United"]
        tweets = get_tweets(api, team_name)
        sentiments = [analyze_sentiment(tweet) for tweet in tweets]
        average_sentiment = sum(sentiments) / len(sentiments)
        data.at[index, "AverageSentiment"] = average_sentiment


def train_model_with_hyperparameter_tuning(X_train, y_train):
    model = RandomForestClassifier()
    param_grid = {
        "n_estimators": [10, 50, 100],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 5, 10],
    }
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring="accuracy")
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    return best_model


def main():
    try:
        # Load data from CSV
        data = pd.read_csv(CSV_FILENAME)

        # Set up Twitter API
        api = setup_twitter_api(
            CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )

        # Fetch and analyze tweets for each team
        fetch_and_analyze_tweets(api, data)

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            data[["AverageSentiment"]], data["Outcome"], test_size=0.2, random_state=42
        )

        # Train the model with hyperparameter tuning
        best_model = train_model_with_hyperparameter_tuning(X_train, y_train)

        # Save the best model
        joblib.dump(best_model, MODEL_FILENAME)

        # Predict outcomes and update the CSV
        data["PredictedOutcome"] = best_model.predict(data[["AverageSentiment"]])
        probabilities = best_model.predict_proba(data[["AverageSentiment"]])
        data["WinProbability"] = probabilities[:, 0]
        data["DrawProbability"] = probabilities[:, 1]
        data["LoseProbability"] = probabilities[:, 2]

        # Update the CSV file
        data.to_csv("soccer_data_updated.csv", index=False)
        logging.info("CSV file updated successfully")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
