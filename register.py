from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import User, UserCreate, get_db, get_password_hash

router = APIRouter()

@router.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Account created successfully", "user_id": new_user.id}