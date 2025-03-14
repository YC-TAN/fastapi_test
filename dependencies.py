from typing import Annotated
from sqlmodel import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jwt.exceptions import InvalidTokenError

from .database import get_session
from .utils import (
    SECRET_KEY,
    ALGORITHM
)
from .models import User, TokenData
from .crud import get_user_by_email


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

TokenDep = Annotated[str, Depends(oauth2_scheme)]

#TODO Check if def get_session actually belongs to this file
SessionDep = Annotated[Session, Depends(get_session)]

async def get_current_user(token: TokenDep, session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_email(session=session, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


ActiveUserDep = Annotated[User, Depends(get_current_active_user)]