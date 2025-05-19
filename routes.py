# app/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import database
import models
import schemas
import auth

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth helper
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from jose import JWTError, jwt
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Signup
@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter_by(username=user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"msg": "User created"}

# Login → Token
@router.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# Get all quizzes
@router.get("/quizzes", response_model=list[schemas.QuizOut])
def get_quizzes(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Quiz).all()

# Get questions by quiz id
@router.get("/quiz/{quiz_id}/questions")
def get_questions(quiz_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    questions = db.query(models.Question).filter_by(quiz_id=quiz_id).all()
    result = []
    for q in questions:
        options = db.query(models.Option).filter_by(question_id=q.id).all()
        result.append({
            "id": q.id,
            "text": q.text,
            "options": [o.text for o in options]
        })
    return result

# Submit answers and get score
@router.post("/quiz/{quiz_id}/submit")
def submit_quiz(quiz_id: int, answers: list[schemas.AnswerSubmit], db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    score = 0
    for ans in answers:
        q = db.query(models.Question).filter_by(id=ans.question_id, quiz_id=quiz_id).first()
        if q and q.correct_option == ans.selected_option:
            score += 1
    # Save progress
    progress = models.UserProgress(user_id=user.id, quiz_id=quiz_id, score=score, completed=True)
    db.add(progress)
    db.commit()
    return {"score": score}
