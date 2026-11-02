
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError

from database import get_connection
from auth import hash_password, verify_password, create_token, verify_token

app = FastAPI(title="MyGame Backend")

security = HTTPBearer()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ProgressRequest(BaseModel):
    current_level: int = 1
    experience: int = 0
    saved_data: dict = {}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        return verify_token(credentials.credentials)
    except (InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired login token"
        )


@app.get("/")
def home():
    return {"message": "MyGame Backend is running!"}


@app.post("/register")
def register(data: RegisterRequest):
    if len(data.username) < 3 or len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Invalid username or password"
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (data.username, data.email, hash_password(data.password))
        )
        connection.commit()
        return {"message": "Account created successfully"}

    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email may already exist"
        )

    finally:
        cursor.close()
        connection.close()


@app.post("/login")
def login(data: LoginRequest):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT user_id, username, password_hash FROM users WHERE username = %s",
            (data.username,)
        )
        user = cursor.fetchone()

        if not user or not verify_password(
            data.password, user["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )

        cursor.execute(
            "UPDATE users SET last_login = NOW() WHERE user_id = %s",
            (user["user_id"],)
        )
        connection.commit()

        token = create_token(user["user_id"])

        return {
            "message": "Login successful",
            "token": token,
            "user_id": user["user_id"],
            "username": user["username"]
        }

    finally:
        cursor.close()
        connection.close()


@app.get("/progress")
def get_progress(user_id: int = Depends(get_current_user)):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT current_level, experience, saved_data, updated_at "
            "FROM player_progress WHERE user_id = %s",
            (user_id,)
        )

        progress = cursor.fetchone()

        if not progress:
            return {
                "current_level": 1,
                "experience": 0,
                "saved_data": {}
            }

        if isinstance(progress["saved_data"], str):
            progress["saved_data"] = json.loads(progress["saved_data"])

        return progress

    finally:
        cursor.close()
        connection.close()


@app.post("/progress")
def save_progress(
    data: ProgressRequest,
    user_id: int = Depends(get_current_user)
):
    if data.current_level < 1 or data.experience < 0:
        raise HTTPException(
            status_code=400,
            detail="Level must be at least 1 and experience cannot be negative"
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO player_progress
            (user_id, current_level, experience, saved_data)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                current_level = VALUES(current_level),
                experience = VALUES(experience),
                saved_data = VALUES(saved_data)
            """,
            (
                user_id,
                data.current_level,
                data.experience,
                json.dumps(data.saved_data)
            )
        )

        connection.commit()

        return {"message": "Progress saved successfully"}

    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save player progress"
        )

    finally:
        cursor.close()
        connection.close()
