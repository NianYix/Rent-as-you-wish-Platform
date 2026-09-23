from typing import Annotated, Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.security import safe_decode_token
from app.models import AdminAccount, User, UserRole, UserStatus


def get_token_payload(authorization: Optional[str] = Header(default=None)) -> Optional[dict]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AppError("无效的 Authorization", status_code=401)
    payload = safe_decode_token(parts[1])
    if not payload:
        raise AppError("登录已过期，请重新登录", status_code=401)
    return payload


def get_current_user_optional(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[Optional[dict], Depends(get_token_payload)],
) -> Optional[User]:
    if not payload or payload.get("typ") == "admin":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = db.get(User, int(user_id))
    if not user or user.status == UserStatus.DISABLED.value:
        return None
    return user


def get_current_user(
    user: Annotated[Optional[User], Depends(get_current_user_optional)],
) -> User:
    if not user:
        raise AppError("请先登录", status_code=401)
    return user


def require_merchant(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role not in (UserRole.MERCHANT.value, UserRole.ADMIN.value):
        raise AppError("需要商家权限", status_code=403)
    return user


def get_current_admin(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[Optional[dict], Depends(get_token_payload)],
) -> AdminAccount:
    if not payload or payload.get("typ") != "admin":
        raise AppError("请先登录管理后台", status_code=401)
    admin_id = payload.get("sub")
    admin = db.get(AdminAccount, int(admin_id))
    if not admin or not admin.is_active:
        raise AppError("管理员不存在或已禁用", status_code=401)
    return admin


DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_user)]
OptionalUserDep = Annotated[Optional[User], Depends(get_current_user_optional)]
MerchantUserDep = Annotated[User, Depends(require_merchant)]
AdminDep = Annotated[AdminAccount, Depends(get_current_admin)]
