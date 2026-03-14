from fastapi import FastAPI
from .core.database import engine, Base
from .models import user, habit, habit_log
from .api import auth, users, habits, insights

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(habits.router)  
app.include_router(insights.router)

@app.get("/")
def root():
    return {"message": "Hello Jarvis!"}