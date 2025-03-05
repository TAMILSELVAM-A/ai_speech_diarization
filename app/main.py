from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints import diarization

app = FastAPI(title="Speaker Diarization API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diarization.router, prefix="/api/v1", tags=["diarization"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Speaker Diarization API!"}
