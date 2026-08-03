from fastapi import FastAPI


app = FastAPI(title="Event_Horizon_AI_Sales")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "project": "Event_Horizon_AI_Sales",
        "status": "running",
    }
