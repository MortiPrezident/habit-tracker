from fastapi import FastAPI
from web.routers import auth


app = FastAPI()

app.include_router(auth)

