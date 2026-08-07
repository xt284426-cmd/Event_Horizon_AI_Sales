import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.modules.customers.router import router as customers_router


app = FastAPI(title="Event_Horizon_AI_Sales")

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(customers_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "project": "Event_Horizon_AI_Sales",
        "status": "running",
    }
