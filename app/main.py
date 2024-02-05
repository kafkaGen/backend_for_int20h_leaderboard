from fastapi import FastAPI

from .routers import leaderboard, login

app = FastAPI()

app.include_router(login.router)
app.include_router(leaderboard.router)
