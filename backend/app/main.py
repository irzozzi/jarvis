from fastapi import FastAPI

from .api import auth, users
from .core.database import Base, engine
from .models import user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis API")
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "Hello Jarvis!"}