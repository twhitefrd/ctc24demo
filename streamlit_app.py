import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit_authenticator as stauth

# Retrieve secrets for authentication
try:
    auth_username = st.secrets["auth"]["username"]
    auth_password = st.secrets["auth"]["password"]
    auth_name = st.secrets["auth"].get("name", "Trivia Host")  # Default to 'Trivia Host' if name not found
except KeyError:
    st.error("Authentication secrets not found. Make sure to define them in secrets.toml or Streamlit Cloud settings.")
    st.stop()

# Authentication Configuration
auth_config = {
    "credentials": {
        "usernames": {
            auth_username: {
                "name": auth_name,  # Use the name from the secrets
                "password": auth_password,  # Plain-text password, auto-hashed
            }
        }
    },
    "cookie": {
        "expiry_days": 1,
        "key": "trivia_cookie",
        "name": "trivia_admin",
    },
    "preauthorized": []
}

# Initialize the authenticator
authenticator = stauth.Authenticate(
    auth_config["credentials"],
    auth_config["cookie"]["name"],
    auth_config["cookie"]["key"],
    auth_config["cookie"]["expiry_days"],
)

# Login UI
name, authentication_status, username = authenticator.login("Login", "main")

DATA_FILE = "trivia_games.csv"

# Main App Logic
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.write(f"Welcome, {name}!")  # Displays the dynamic name

    # Admin input interface to record game data
    st.title("Record Trivia Game Scores")
    game_date = st.date_input("Game Date", datetime.today())
    game_location = st.text_input("Game Location")
    num_teams = st.number_input("Number of Teams", min_value=1, step=1)

    scores = {}
    for i in range(1, num_teams + 1):
        team_name = st.text_input(f"Team {i} Name")
        team_score = st.number_input(f"Team {i} Score", min_value=0, step=1)
        if team_name:
            scores[team_name] = team_score

    if st.button("Save Scores"):
        # Load existing data
        try:
            existing_data = pd.read_csv(DATA_FILE)
        except FileNotFoundError:
            existing_data = pd.DataFrame(columns=["Date", "Location", "Team", "Score"])

        # Append new data
        for team, score in scores.items():
            new_row = {"Date": game_date, "Location": game_location, "Team": team, "Score": score}
            existing_data = pd.concat([existing_data, pd.DataFrame([new_row])], ignore_index=True)

        # Save data
        existing_data.to_csv(DATA_FILE, index=False)
        st.success("Scores saved successfully!")

elif authentication_status == False:
    st.error("Invalid username or password.")
elif authentication_status == None:
    st.warning("Please enter your username and password.")
