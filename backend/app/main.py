from fastapi import FastAPI

from backend.app.modules.customers.router import router as customers_router


app = FastAPI(title="Event_Horizon_AI_Sales")
app.include_router(customers_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "project": "Event_Horizon_AI_Sales",
        "status": "running",
    }
