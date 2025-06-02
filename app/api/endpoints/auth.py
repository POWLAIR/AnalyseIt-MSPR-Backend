# app/api/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.core.security import create_access_token, verify_password, hash_password
from app.db.models.user import User
from app.core.deps import get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    is_admin: bool

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False

class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool

    class Config:
        from_attributes = True

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Connexion utilisateur avec email et mot de passe
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin
    })
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        is_admin=user.is_admin
    )

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Créer un nouvel utilisateur
    """
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Créer le nouvel utilisateur
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Récupérer les informations de l'utilisateur connecté
    """
    return UserResponse.from_orm(current_user)

@router.post("/logout")
def logout():
    """
    Déconnexion (côté client, suppression du token)
    """
    return {"message": "Déconnexion réussie"}
