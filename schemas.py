# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class QuizOut(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True

class QuestionOut(BaseModel):
    id: int
    text: str
    options: List[str]

class AnswerSubmit(BaseModel):
    question_id: int
    selected_option: str
