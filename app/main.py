from fastapi import FastAPI

from app.core.cors import setup_cors
from app.routes.contact import router as contact_router
from app.routes.auth import router as auth_router


app = FastAPI()

setup_cors(app)

app.include_router(contact_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "Hello from FastAPI!"}