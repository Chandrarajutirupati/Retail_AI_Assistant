from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from sql_agent import ask_database
from database import get_dashboard_kpis

app = FastAPI(
    title="Retail AI Assistant API",
    version="1.0"
)


class Question(BaseModel):
    question: str


# ---------------------------------------
# Home
# ---------------------------------------
@app.get("/")
def home():
    return {
        "message": "Retail AI Assistant API is running!"
    }


# ---------------------------------------
# Ask AI
# ---------------------------------------
@app.post("/ask")
def ask(question: Question):

    try:
        response = ask_database(question.question)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------------------------------
# Dashboard KPIs
# ---------------------------------------
@app.get("/dashboard")
def dashboard():

    try:
        return get_dashboard_kpis()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


