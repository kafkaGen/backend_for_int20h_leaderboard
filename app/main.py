from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import leaderboard, login

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins if needed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(login.router)
app.include_router(leaderboard.router)
