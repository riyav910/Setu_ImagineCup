from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="Setu AI Backend")

# CORS (Allow React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect Routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Setu AI Backend is Running 🚀"}

# To run: uvicorn app.main:app --reload