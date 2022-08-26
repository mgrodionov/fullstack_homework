from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as main_router


app = FastAPI(
    title="Homework",
    description="Homework for fullstack candidate"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3333", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router, prefix="/api")
