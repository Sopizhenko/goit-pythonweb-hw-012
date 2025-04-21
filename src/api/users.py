"""
Users API module for managing user-related endpoints.
"""

from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    File,
    HTTPException,
    status,
    BackgroundTasks,
)

from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.database.db import get_db
from src.schemas import User, RequestEmail, ResetPassword
from src.conf.config import settings
from src.services.auth import (
    get_current_user,
    get_current_admin_user,
    create_email_token,
    get_email_from_token,
)
from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.services.email import send_reset_password_email
from src.services.redis_cache import cache_response, redis_cache


router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.

    Args:
        request (Request): The incoming request object.
        user (User): The current authenticated user.

    Returns:
        User: The user's profile information.

    Note:
        This endpoint is rate-limited to 10 requests per minute.
        Response is cached for 5 minutes.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the user's avatar by uploading a new image.

    Args:
        file (UploadFile): The image file to upload.
        user (User): The current authenticated user.
        db (AsyncSession): Database session.

    Returns:
        User: The updated user profile with the new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    updated_user = await user_service.update_avatar_url(user.email, avatar_url)

    # Clear user's cache after avatar update
    await redis_cache.clear_user_cache(user.id)

    return updated_user


@router.post("/request-reset-password", status_code=status.HTTP_200_OK)
async def request_reset_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.

    Args:
        body (RequestEmail): The request body containing the user's email.
        background_tasks (BackgroundTasks): Background tasks for sending email.
        request (Request): The incoming request.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the password reset email has been sent.

    Raises:
        HTTPException: If the user is not found or email is not confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and user.confirmed:
        background_tasks.add_task(
            send_reset_password_email,
            email=user.email,
            username=user.username,
            host=str(request.base_url),
        )
        return {"message": "Password reset email has been sent"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found or email not confirmed",
    )


@router.get("/reset-password/{token}", status_code=status.HTTP_200_OK)
async def verify_reset_token(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify a password reset token.

    Args:
        token (str): The reset token from the email.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the token is valid.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if user and user.confirmed:
        return {"message": "Token is valid"}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token or user not found",
    )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset a user's password using a reset token.

    Args:
        body (ResetPassword): The request body containing the token and new password.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the password has been reset.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    email = await get_email_from_token(body.token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if user and user.confirmed:
        await user_service.change_password(
            email=user.email, new_password=body.new_password
        )
        # Clear user's cache after password change
        await redis_cache.clear_user_cache(user.id)
        return {
            "message": f"Password has been reset successfully for user {user.username}"
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token or user not found",
    )
