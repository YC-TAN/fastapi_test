from datetime import datetime, timezone
from enum import Enum
from pydantic import EmailStr, SecretStr
from sqlmodel import Field, SQLModel


# User Model
class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    # USER = "user"

# class UserRole(str, Enum):
#     MANAGER = auto()
#     EDITOR = auto()
#     ADMIN = MANAGER | EDITOR
#     # USER = "user"


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_superuser: bool = Field(default=True)
    disabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    role: UserRole = Field(default=UserRole.EDITOR)  # Default to 'editor'


# TODO separate update pw to another model
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(
        default=None,
        description="Password must be at least 8 characters long, contain a mix of uppercase and lowercase letters, numbers, and symbols.", 
        min_length=8, 
        max_length=40,
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).+$",
    ) # this will be removed as admin should not change pw
    disabled: bool | None = None # Only admin has permission


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(SQLModel):
    email: EmailStr | None = None


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None # sub = subject


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

# Form model
class FormData(SQLModel):
    email: EmailStr
    password: str

    model_config = {"extra": "forbid"} # forbid extra field



# Other class in the future
class UserLogin(UserBase):
    password: str

# Allow users to update their own password
class UserUpdatePassword(SQLModel):
    current_password: str
    new_password: str

# if user forget their password
class AdminPasswordReset(SQLModel):
    new_password: str