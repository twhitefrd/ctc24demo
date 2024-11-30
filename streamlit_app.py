import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit_authenticator as stauth

# Retrieve secrets for authentication
auth_username = st.secrets["auth"]["username"]
auth_password = st.secrets["auth"]["password"]

# Authentication Setup
auth_config = {
    "credentials": {
        "usernames": {
            auth_username: {
                "name": "Trivia Host",
                "password": stauth.Hasher([auth_password]).generate()[0],
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

authenticator = stauth.Authenticate(
    auth_config["credentials"], 
    auth_config["cookie"]["name"], 
    auth_config["cookie"]["key"], 
    auth_config["cookie"]["expiry_days"]
)

name, authentication_status, username = authenticator.login("Login", "main")

# File to store game data
DATA_FILE = "trivia_games.csv"

@st.cache_data
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Game Date", "Location", "Team Name", "Score"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Main App
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.write(f"Welcome, {name}!")

    # Load game data
    trivia_data = load_data()

    st.title("Trivia Admin Panel")

    # Add a new game
    st.subheader("Add a New Game")
    game_date = st.date_input("Game Date", value=datetime.now().date())
    location = st.text_input("Location")

    st.markdown("### Team Scores")
    team_count = st.number_input("Number of Teams", min_value=1, step=1, value=2)
    
    teams = []
    for i in range(team_count):
        team_name = st.text_input(f"Team {i+1} Name")
        team_score = st.number_input(f"Team {i+1} Score", min_value=0, step=1)
        if team_name:
            teams.append({"Team Name": team_name, "Score": team_score})

    if st.button("Add Game"):
        if location and teams:
            for team in teams:
                new_entry = {
                    "Game Date": game_date, 
                    "Location": location, 
                    "Team Name": team["Team Name"], 
                    "Score": team["Score"]
                }
                trivia_data = pd.concat([trivia_data, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(trivia_data)
            st.success("Game data added successfully!")
        else:
            st.error("Please provide a location and at least one team with scores.")

    # Display existing records
    st.subheader("Game Records")
    st.dataframe(trivia_data)

    # Download CSV
    csv_data = trivia_data.to_csv(index=False).encode("utf-8")
    st.download_button(label="Download Data as CSV", data=csv_data, file_name="trivia_games.csv", mime="text/csv")

elif authentication_status == False:
    st.error("Invalid username or password.")
elif authentication_status == None:
    st.warning("Please enter your username and password.")
