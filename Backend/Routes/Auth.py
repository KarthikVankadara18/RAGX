from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from Backend.Security.User_Model import UserModel
from Backend.Security.JWT import create_access_token
from Backend.Security.Password import verify_password

route = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length= 5, description= "Email of the user")
    password: str = Field(..., min_length= 8,description= "Password of the user")

class RegisterResponse(BaseModel):
    user_id: str
    email: str

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

@route.post("/register", response_model= RegisterResponse)
def register_user(request: RegisterRequest):
    print(f"Registering user with email: {request.email}")
    try:
        user_model = UserModel()
        return user_model.create_user(
            email= request.email,
            password= request.password
        )
    except ValueError as e:
        raise HTTPException(status_code= 400, detail= str(e))

@route.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    user_model = UserModel()

    user = user_model.get_user_by_email(request.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not user.get("is_active", False):
        raise HTTPException(
            status_code=403,
            detail="User account is inactive.",
        )

    if not verify_password(
        request.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(str(user["_id"]))
    print(f"User {request.email} logged in successfully. Access token generated.")

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }