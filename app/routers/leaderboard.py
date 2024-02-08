import os
import subprocess
from io import StringIO

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import get_connection, setup_logging

router = APIRouter(
    prefix="/leaderboard",
    tags=["leaderboard"],
    dependencies=[Depends(get_connection), Depends(setup_logging)],
    responses={404: {"description": "Not found"}},
)


@router.get("/accuracy_scores/")
async def accuracy_scores() -> JSONResponse:
    conn = get_connection()
    sql_query = "SELECT * from accuracy_scores;"
    df = pd.read_sql_query(sql_query, conn).drop(["id"], axis=1).fillna(0)
    df.sort_values(by="score", inplace=True, ascending=False)
    df["last"] = df["last"].astype(str)
    df["score"] = df["score"].astype(str)
    json_data = df.to_dict(orient="records")
    conn.close()

    return JSONResponse(content=json_data, status_code=200)


@router.post("/refresh_accuracy_scores/")
async def refresh_accuracy_scores() -> None:
    conn = get_connection()
    logger = setup_logging()
    sql_query = "SELECT * from accuracy_scores;"
    accuracy_scores = pd.read_sql_query(sql_query, conn).drop(["id"], axis=1)
    sql_query = "SELECT * from users;"
    users = pd.read_sql_query(sql_query, conn).drop(["id"], axis=1)
    for _, row in users.iterrows():
        try:
            os.environ["KAGGLE_USERNAME"] = row["username"]
            os.environ["KAGGLE_KEY"] = row["apikey"]

            command = "kaggle competitions submissions -c rsna-pneumonia-detection-challenge"
            result = subprocess.run(command, shell=True, capture_output=True, text=True).stdout
            cleaned_string = "\n".join(line.strip() for line in result.strip().split("\n"))
            cleaned_string = "\n".join(cleaned_string.split("\n")[1:])
            data = StringIO(cleaned_string)
            users_submitions = pd.read_fwf(data).drop(0, axis=0)
            users_submitions["privateScore"] = users_submitions["privateScore"].astype(float)
            users_submitions.sort_values(by="privateScore", inplace=True, ascending=False)

            if users_submitions.shape[0]:

                if row["teamname"] not in accuracy_scores["teamname"].to_list():
                    logger.info(f"LEADERBOARD INSERTING: {row['teamname']} with {users_submitions.iloc[0].to_string} into the database.")
                    cursor = conn.cursor()
                    sql_query_insert = """
                    INSERT INTO accuracy_scores (teamname, score, entries, last)
                    VALUES (%s, %s, %s, %s);
                    """
                    values = (
                        row["teamname"],
                        users_submitions.iloc[0]["privateScore"] if users_submitions.iloc[0]["privateScore"] else 0,
                        users_submitions.shape[0],
                        users_submitions.iloc[0]["date"],
                    )
                    cursor.execute(sql_query_insert, values)
                    cursor.close()
                    conn.commit()
                elif float(users_submitions.iloc[0].get("privateScore")) > float(
                    accuracy_scores.loc[accuracy_scores.teamname == row["teamname"]].get("score", 0)
                ):
                    logger.info(f"LEADERBOARD UPDATING: {row['teamname']} with {users_submitions.iloc[0].to_string} into the database.")
                    cursor = conn.cursor()
                    update_query = """
                    UPDATE accuracy_scores
                    SET score = %s, entries = %s, last = %s
                    WHERE teamname = %s;
                    """
                    new_values = (
                        users_submitions.iloc[0]["privateScore"] if users_submitions.iloc[0]["privateScore"] else 0,
                        users_submitions.shape[0],
                        users_submitions.iloc[0]["date"],
                        row["teamname"],
                    )

                    cursor.execute(update_query, new_values)
                    cursor.close()
                    conn.commit()
                else:
                    logger.info(f"LEADERBOARD SKIPPING: {users_submitions.iloc[0].to_string} into the database.")

        except Exception as e:
            logger.error(f"Error: {e} while fetching data for {row['teamname']}")

    conn.close()
    return JSONResponse(content={"message": "Successfully!"}, status_code=200)
