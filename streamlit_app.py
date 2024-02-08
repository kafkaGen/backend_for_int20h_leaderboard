import os

import pandas as pd
import requests
from dotenv import load_dotenv

import streamlit_app as st

load_dotenv()


def login():
    teamname = st.sidebar.text_input("Teamname")
    username = st.sidebar.text_input("Username")
    apikey = st.sidebar.text_input("Apikey", type="password")
    return teamname, username, apikey


def authenticate(teamname, username, apikey):
    params = {
        "teamname": teamname,
        "username": username,
        "apikey": apikey,
    }

    url = f"{os.getenv('APP_HOST')}/login/register/"
    response = requests.post(url, json=params)

    if response.status_code == 200:
        return True
    else:
        return False


def get_leaderboard():
    url = f"{os.getenv('APP_HOST')}/leaderboard/accuracy_scores/"
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    df.sort_values(by="score", inplace=True, ascending=False)
    return df


def refresh_leaderboard():
    url = f"{os.getenv('APP_HOST')}/leaderboard/refresh_accuracy_scores/"
    requests.post(url)


def main():
    st.title("INT20H Data Science Test Task Leaderboard")
    st.write("Please, provide your Kaggle credentials and team name to access the leaderboard.")

    creds = login()

    if st.sidebar.button("Login"):
        if authenticate(*creds):
            refresh_leaderboard()
            df = get_leaderboard()
            st.table(df)
        else:
            st.sidebar.error("Invalid Kaggle credentials!")


if __name__ == "__main__":
    main()
