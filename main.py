from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from api.routers.entry_router import router as entry_router
from api.routers.topic_router import router as topic_router
from api.routers.auth_router import router as auth_router

app = FastAPI()
app.include_router(entry_router)
app.include_router(topic_router)
app.include_router(auth_router)
