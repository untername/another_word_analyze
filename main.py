from fastapi import FastAPI
from core.database import DataBase, Engine
import routers


DataBase.metadata.create_all(bind=Engine)

app = FastAPI()
app.include_router(routers.router)
