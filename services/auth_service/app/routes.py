from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from app.dependencies import get_db, get_current_user, require_role
from app.models import User
from app.schemas import UserRegister, UserResponse, LoginSchema, TokenResponse
from app.security import verify_password, create_access_token

password_hash = PasswordHash.recommended()

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=password_hash.hash(user_data.password),
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return new_user



@router.post("/login", response_model=TokenResponse)
def login_user(
    user_data: LoginSchema,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/candidate-only")
def candidate_only(
    current_user: User = Depends(require_role(["candidate"]))
):
    return {
        "message": "Candidate access granted",
        "user": current_user.name
    }


@router.get("/recruiter-only")
def recruiter_only(
    current_user: User = Depends(require_role(["recruiter"]))
):
    return {
        "message": "Recruiter access granted",
        "user": current_user.name
    }


@router.get("/admin-only")
def admin_only(
    current_user: User = Depends(require_role(["admin"]))
):
    return {
        "message": "Admin access granted",
        "user": current_user.name
    }