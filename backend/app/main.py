from fastapi import FastAPI
from .core.database import engine, Base
from .models import user, habit, habit_log, goal
from .api import auth, users, habits, insights, context, personality, goals, chat, events, notifications





Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(habits.router)  
app.include_router(insights.router)
app.include_router(context.router)
app.include_router(personality.router)
app.include_router(goals.router)
app.include_router(chat.router)
app.include_router(events.router)
app.include_router(notifications.router)

@app.get("/")
def root():
    return {"message": "Hello Jarvis!"}