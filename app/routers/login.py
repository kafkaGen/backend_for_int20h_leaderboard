import os
import subprocess

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import get_connection, setup_logging

router = APIRouter(
    prefix="/login",
    tags=["login"],
    dependencies=[Depends(get_connection), Depends(setup_logging)],
    responses={404: {"description": "Not found"}},
)


@router.post("/register/")
async def register(teamname: str, username: str, apikey: str) -> JSONResponse:
    response = JSONResponse(content={"message": "User already exists!"}, status_code=200)
    conn = get_connection()
    logger = setup_logging()
    sql_query = "SELECT * FROM users;"
    df = pd.read_sql_query(sql_query, conn)
    if teamname not in df["teamname"].to_list() or apikey not in df["apikey"].to_list():
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"] = apikey
        command = "kaggle competitions list"
        result = subprocess.run(command, shell=True, capture_output=True, text=True).stdout
        if result == "":
            logger.error(f"Invalid Kaggle credentials: {username}, {apikey}")
            response = JSONResponse(content={"message": "Invalid Kaggle credentials!"}, status_code=400)
            return response

        logger.info(f"LOGING INSERTING: {teamname}, {username}, {apikey} into the database.")
        cursor = conn.cursor()
        sql_query_insert = """
        INSERT INTO users (teamname, username, apikey)
        VALUES (%s, %s, %s);
        """
        values = (teamname, username, apikey)
        cursor.execute(sql_query_insert, values)
        cursor.close()
        conn.commit()
        response = JSONResponse(content={"message": "User registered successfully!"}, status_code=200)
    conn.close()

    return response
