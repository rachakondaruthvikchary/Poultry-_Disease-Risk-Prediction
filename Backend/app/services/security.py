from datetime import datetime, timedelta, timezone
from jose import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return check_password_hash(hashed_password, plain_password)
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    # Use a lighter PBKDF2 cost so signup/login feel responsive on modest hardware.
    return generate_password_hash(password, method='pbkdf2:sha256:100000')


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
