from fastapi import FastAPI
from api.routers.entry_router import router as entry_router
from database.setup import router as db_router

app = FastAPI()
app.include_router(entry_router)
app.include_router(db_router)