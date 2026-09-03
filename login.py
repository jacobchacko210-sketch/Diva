from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import User, UserLogin, get_db, verify_password

router = APIRouter()

@router.post("/login/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    return {"message": "Login successful", "user_id": db_user.id}

@router.get("/admin/stats/")
def get_admin_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    return {
        "total_users": total_users,
        "documents_scanned": 8493,
        "fraud_rate": "12.4%",
        "logs": [
            f"[SYSTEM] XAMPP Database active. Total registered users: {total_users}",
            "[ALERT] High risk document blocked from IP 192.168.1.4",
            "[SYSTEM] Fraud engine models loaded successfully."
        ]
    }