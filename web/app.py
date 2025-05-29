from fastapi import FastAPI
from web.routers import auth, habit_service


app = FastAPI()

app.include_router(auth.router)
app.include_router(habit_service.router)



@app.get("/health")
async def check_health():
    return {"message": True}