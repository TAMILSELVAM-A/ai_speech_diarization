from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.v1.endpoints import diarization
import os

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

if __name__ == "__main__":
    import uvicorn
    # port = int(os.environ.get("PORT", 8000))
    app.run(port=int(os.environ.get("PORT", 8000)),host='0.0.0.0',debug=True)

